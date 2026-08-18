"""Generate an AAC pictogram board for a menu item.

Takes the dish description (and optionally a photo of the dish), extracts the
food keywords, resolves each one to an ARASAAC pictogram and composes them into
a single image: the main item large on the left, a secondary item on the right
and up to five modifiers in a row along the bottom.

Usage:
    python scripts/pictogram_generator.py --text "Hamburguesa con queso y papas fritas"
    python scripts/pictogram_generator.py --text "..." --image https://example.com/dish.jpg
    python scripts/pictogram_generator.py --text "..." --image ./photos/dish.jpg --out board.png

Pictograms are property of the Government of Aragon, created by Sergio Palao
for ARASAAC (http://www.arasaac.org), distributed under CC BY-NC-SA.
"""

import argparse
import json
import os
from io import BytesIO

import requests
from PIL import Image

DEFAULT_CACHE_DIR = os.path.join(".cache", "arasaac")
SPACY_MODELS = {"es": "es_core_news_lg", "en": "en_core_web_lg"}
CLIP_CHECKPOINT = "openai/clip-vit-base-patch32"

CANVAS_SIZE = (500, 500)
MAIN_SIZE = (300, 300)
SECONDARY_SIZE = (200, 200)
TERTIARY_SIZE = (100, 100)
MAX_TERTIARY = 5


# --- ARASAAC keywords -------------------------------------------------------

def load_keywords(language, cache_dir):
    """Read the cached ARASAAC food keywords, downloading them on a cache miss."""
    path = os.path.join(cache_dir, f"keywords_{language}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    url = f"https://api.arasaac.org/v1/pictograms/{language}/search/food"
    response = requests.get(url, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"ARASAAC keyword request failed: {response.status_code}")

    keywords = set()
    for item in response.json():
        for entry in item.get("keywords", []):
            keyword = entry.get("keyword")
            if keyword:
                keywords.add(keyword.lower())
    keywords = sorted(keywords)

    os.makedirs(cache_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(keywords, handle, ensure_ascii=False, indent=0)
    return keywords


def load_nlp(language):
    import spacy

    model = SPACY_MODELS.get(language)
    if model is None:
        raise SystemExit(f"No spaCy model configured for language '{language}'")
    try:
        return spacy.load(model)
    except OSError as error:
        raise SystemExit(
            f"spaCy model '{model}' is missing. Run: python scripts/prepare_model.py --lang {language}"
        ) from error


# --- Image side: pick the dish's main ingredient from a photo ----------------

def load_image(source):
    """Open an image from a URL or a local path."""
    if source.startswith("http://") or source.startswith("https://"):
        response = requests.get(source, timeout=60)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    return Image.open(source).convert("RGB")


def get_best_matching_keyword(image_source, keywords, batch_size=256):
    """Score every ARASAAC keyword against the photo with CLIP, best one wins."""
    import torch
    from transformers import CLIPModel, CLIPProcessor

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained(CLIP_CHECKPOINT).to(device)
    processor = CLIPProcessor.from_pretrained(CLIP_CHECKPOINT)
    image = load_image(image_source)

    best_keyword, best_score = None, float("-inf")
    # CLIP's text encoder caps out at 77 tokens per prompt, so the keyword list
    # is scored in batches rather than as one giant forward pass.
    for start in range(0, len(keywords), batch_size):
        batch = keywords[start:start + batch_size]
        inputs = processor(
            text=batch, images=image, return_tensors="pt", padding=True, truncation=True
        ).to(device)
        with torch.no_grad():
            logits = model(**inputs).logits_per_image[0]
        index = int(logits.argmax())
        if float(logits[index]) > best_score:
            best_score = float(logits[index])
            best_keyword = batch[index]

    return best_keyword.split(" ")[0] if best_keyword else None


# --- Text side: keywords and their closest ARASAAC synonyms ------------------

def adjust_similarity(word, similarity, boost_compound=0.05, penalty_diminutive=0.05):
    """Prefer compound keywords ("queso crema") over diminutives ("quesito")."""
    diminutives = ("ito", "ita", "illo", "illa", "itos", "itas", "illos", "illas")
    if word.endswith(diminutives):
        similarity -= penalty_diminutive
    if " " in word or "-" in word:
        similarity += boost_compound
    return similarity


def extract_keywords_with_synonyms(nlp, text, keyword_docs, keywords_set, threshold=0.6):
    """Map the description's nouns/adjectives/verbs onto ARASAAC keywords."""
    doc = nlp(text.lower())
    tokens = [
        token
        for token in doc
        if token.pos_ in ("NOUN", "ADJ", "VERB") and not token.is_stop and token.has_vector
    ]

    valid_keywords = []
    replaced_words = {}

    for token in tokens:
        if token.text in keywords_set:
            if token.text not in valid_keywords:
                valid_keywords.append(token.text)
            continue

        best_keyword, best_similarity = None, 0
        for keyword, keyword_doc in keyword_docs:
            similarity = adjust_similarity(keyword, token.similarity(keyword_doc))
            if similarity > best_similarity:
                best_similarity, best_keyword = similarity, keyword
        if best_similarity >= threshold and best_keyword not in valid_keywords:
            valid_keywords.append(best_keyword)
            replaced_words[token.text] = best_keyword

    return valid_keywords, replaced_words, doc


def find_secondary_keyword(main_keyword, doc, keywords_set):
    """Pick the modifier attached to the main item, e.g. "hamburguesa de pollo"."""
    main_token = next((token for token in doc if token.text == main_keyword), None)
    if main_token is None:
        return None

    for token in doc:
        keyword = token.text
        if keyword == main_keyword or keyword not in keywords_set:
            continue
        if token.head == main_token or token in main_token.subtree:
            return keyword
        if keyword in main_keyword:
            return keyword
    return None


# --- Pictogram fetching and composition -------------------------------------

def search_pictograms(keyword, language):
    url = f"https://api.arasaac.org/api/pictograms/{language}/bestsearch/{keyword}"
    response = requests.get(url, timeout=60)
    if response.status_code != 200:
        return []
    return [item for item in response.json() if "work" not in item.get("tags", [])]


def download_pictogram(pictogram_id, name, folder):
    url = f"https://static.arasaac.org/pictograms/{pictogram_id}/{pictogram_id}_300.png"
    response = requests.get(url, timeout=60)
    if response.status_code != 200:
        return None
    path = os.path.join(folder, f"{name}_{pictogram_id}.png")
    with open(path, "wb") as handle:
        handle.write(response.content)
    return path


def combine_images(categorized_paths, output_path):
    """Lay the pictograms out on one transparent canvas and save it."""
    canvas_width, canvas_height = CANVAS_SIZE
    combined = Image.new("RGBA", CANVAS_SIZE, (255, 255, 255, 0))

    if categorized_paths["main"]:
        main_img = Image.open(categorized_paths["main"]).resize(MAIN_SIZE).convert("RGBA")
        combined.paste(main_img, (0, (canvas_height - MAIN_SIZE[1]) // 2), main_img)

    if categorized_paths["secondary"]:
        sec_img = Image.open(categorized_paths["secondary"]).resize(SECONDARY_SIZE).convert("RGBA")
        combined.paste(sec_img, (MAIN_SIZE[0], (canvas_height - SECONDARY_SIZE[1]) // 2), sec_img)

    tertiary = categorized_paths.get("tertiary", [])[:MAX_TERTIARY]
    if tertiary:
        start_x = (canvas_width - TERTIARY_SIZE[0] * len(tertiary)) // 2
        y_pos = canvas_height - TERTIARY_SIZE[1]
        for index, path in enumerate(tertiary):
            img = Image.open(path).resize(TERTIARY_SIZE).convert("RGBA")
            combined.paste(img, (start_x + index * TERTIARY_SIZE[0], y_pos), img)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    combined.save(output_path)


def build_board(text, image_source, language, folder, output_path, max_pictograms, cache_dir):
    os.makedirs(folder, exist_ok=True)
    keywords = load_keywords(language, cache_dir)
    keywords_set = set(keywords)
    nlp = load_nlp(language)
    keyword_docs = [(kw, nlp(kw)) for kw in keywords if nlp(kw).has_vector]

    main_keyword = None
    if image_source:
        main_keyword = get_best_matching_keyword(image_source, keywords)

    valid_keywords, replacements, doc = extract_keywords_with_synonyms(
        nlp, text, keyword_docs, keywords_set
    )
    print("Keywords:", valid_keywords)
    print("Synonym replacements:", replacements)

    if not valid_keywords and not main_keyword:
        print("No ARASAAC keywords matched this description.")
        return None

    if not main_keyword or main_keyword not in keywords_set:
        main_keyword = valid_keywords[0]
    if main_keyword not in valid_keywords:
        valid_keywords.append(main_keyword)

    secondary_keyword = find_secondary_keyword(main_keyword, doc, keywords_set)
    if not secondary_keyword:
        others = [word for word in valid_keywords if word != main_keyword]
        secondary_keyword = others[0] if others else None
    print(f"Main: {main_keyword} | Secondary: {secondary_keyword}")

    categorized_paths = {"main": None, "secondary": None, "tertiary": []}
    used = set()
    for keyword in valid_keywords:
        if keyword in used:
            continue
        results = search_pictograms(keyword, language)
        if not results:
            continue
        path = download_pictogram(results[0]["_id"], keyword.replace(" ", "_"), folder)
        if not path:
            continue
        if keyword == main_keyword:
            categorized_paths["main"] = path
        elif keyword == secondary_keyword:
            categorized_paths["secondary"] = path
        else:
            categorized_paths["tertiary"].append(path)
        used.add(keyword)
        if len(used) >= max_pictograms:
            break

    if categorized_paths["main"] is None:
        categorized_paths["main"] = categorized_paths["secondary"]
        categorized_paths["secondary"] = None

    if not any(categorized_paths.values()):
        print("No valid pictograms were found for these keywords.")
        return None

    combine_images(categorized_paths, output_path)
    print(f"Composed image saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True, help="Dish name or description")
    parser.add_argument("--image", help="URL or local path of a photo of the dish")
    parser.add_argument("--lang", default="es", choices=sorted(SPACY_MODELS))
    parser.add_argument("--folder", default="pictogramas", help="Where downloaded pictograms go")
    parser.add_argument("--out", default=os.path.join("pictogramas", "resultado.png"))
    parser.add_argument("--max-pictograms", type=int, default=15)
    parser.add_argument("--cache-dir", default=DEFAULT_CACHE_DIR)
    args = parser.parse_args()

    build_board(
        text=args.text,
        image_source=args.image,
        language=args.lang,
        folder=args.folder,
        output_path=args.out,
        max_pictograms=args.max_pictograms,
        cache_dir=args.cache_dir,
    )


if __name__ == "__main__":
    main()
