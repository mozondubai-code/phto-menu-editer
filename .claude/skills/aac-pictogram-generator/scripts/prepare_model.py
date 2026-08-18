"""One-time setup for the AAC pictogram generator.

Downloads the spaCy language model and the CLIP checkpoint, then caches the
ARASAAC food keyword list to disk so that pictogram_generator.py starts fast
and works without re-querying the keyword endpoint on every run.

Usage:
    python scripts/prepare_model.py [--lang es] [--cache-dir .cache/arasaac]
"""

import argparse
import json
import os
import subprocess
import sys

import requests

SPACY_MODELS = {
    "es": "es_core_news_lg",
    "en": "en_core_web_lg",
}
CLIP_CHECKPOINT = "openai/clip-vit-base-patch32"
DEFAULT_CACHE_DIR = os.path.join(".cache", "arasaac")


def ensure_spacy_model(lang):
    """Download the spaCy vector model for `lang` if it is not installed yet."""
    import spacy

    model = SPACY_MODELS.get(lang)
    if model is None:
        raise SystemExit(f"No spaCy model configured for language '{lang}'")
    try:
        spacy.load(model)
        print(f"spaCy model already installed: {model}")
    except OSError:
        print(f"Downloading spaCy model: {model}")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model])
    return model


def ensure_clip():
    """Pull the CLIP weights into the local HuggingFace cache."""
    from transformers import CLIPModel, CLIPProcessor

    print(f"Downloading CLIP checkpoint: {CLIP_CHECKPOINT}")
    CLIPModel.from_pretrained(CLIP_CHECKPOINT)
    CLIPProcessor.from_pretrained(CLIP_CHECKPOINT)


def fetch_arasaac_food_keywords(language="es"):
    """Return the ARASAAC keywords tied to pictograms found under 'food'."""
    print("Downloading keywords from ARASAAC")
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
    return sorted(keywords)


def cache_keywords(language, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    keywords = fetch_arasaac_food_keywords(language)
    path = os.path.join(cache_dir, f"keywords_{language}.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(keywords, handle, ensure_ascii=False, indent=0)
    print(f"Cached {len(keywords)} keywords in {path}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", default="es", choices=sorted(SPACY_MODELS))
    parser.add_argument("--cache-dir", default=DEFAULT_CACHE_DIR)
    parser.add_argument(
        "--skip-clip",
        action="store_true",
        help="Skip the CLIP download when no dish photos will be used",
    )
    args = parser.parse_args()

    ensure_spacy_model(args.lang)
    if not args.skip_clip:
        ensure_clip()
    cache_keywords(args.lang, args.cache_dir)
    print("Setup complete.")


if __name__ == "__main__":
    main()
