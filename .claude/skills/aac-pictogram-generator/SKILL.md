---
name: aac-pictogram-generator
description: Generate ARASAAC pictogram boards for menu items — turn a dish name, description, or photo into a composed pictogram image (main item + secondary item + modifiers). Use whenever the user wants pictograms, AAC/augmentative-communication symbols, accessible or picture-based menus, "picture menu", "symbol menu", ARASAAC images, or an easy-read version of a dish, food item, or menu entry. Also use when a menu photo or dish description needs to be converted into visual symbols for people with communication difficulties.
---

# AAC Pictogram Generator

Turns a dish description (and optionally a photo of the dish) into a single
pictogram board built from [ARASAAC](https://arasaac.org) symbols, for
picture-based / easy-read restaurant menus.

Pipeline: spaCy extracts the food-related words from the description → each word
is matched to the closest ARASAAC keyword by vector similarity → when a photo is
supplied, CLIP picks which keyword the photo actually shows and that becomes the
main item → pictograms are downloaded and composed onto one 500×500 canvas.

Layout of the output image:

| Slot | Size | Position |
|---|---|---|
| Main item | 300×300 | Left, vertically centered |
| Secondary item | 200×200 | Right of the main item, vertically centered |
| Modifiers (up to 5) | 100×100 each | Row along the bottom, centered |

## Setup (once per machine)

```bash
pip install requests pillow spacy torch transformers
python <SKILL_DIR>/scripts/prepare_model.py --lang es
```

`prepare_model.py` downloads the spaCy vector model (`es_core_news_lg` for
Spanish, `en_core_web_lg` for English), pulls the CLIP checkpoint
(`openai/clip-vit-base-patch32`), and caches the ARASAAC food keyword list to
`.cache/arasaac/keywords_<lang>.json`. Pass `--skip-clip` when no dish photos
will be used — text-only runs never load CLIP.

The scripts need outbound network access to `api.arasaac.org` and
`static.arasaac.org`. The keyword cache makes later runs start fast; delete the
cache file to refresh it.

## Generating a board

Text only:

```bash
python <SKILL_DIR>/scripts/pictogram_generator.py \
  --text "Hamburguesa con queso, lechuga y papas fritas" \
  --out ./pictogramas/hamburguesa.png
```

With a photo of the dish (URL or local path) — the photo decides the main item:

```bash
python <SKILL_DIR>/scripts/pictogram_generator.py \
  --text "Torta helada de oreo con dulce de leche" \
  --image https://example.com/torta.webp \
  --out ./pictogramas/torta.png
```

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--text` | Yes | — | Dish name or description |
| `--image` | No | — | URL or local path of a dish photo |
| `--lang` | No | `es` | `es` or `en` |
| `--folder` | No | `pictogramas` | Where individual pictograms are saved |
| `--out` | No | `pictogramas/resultado.png` | Path of the composed board |
| `--max-pictograms` | No | `15` | Cap on pictograms fetched per dish |
| `--cache-dir` | No | `.cache/arasaac` | Keyword cache location |

For a whole menu, call the script once per item — each run writes its own board
and reuses the cached keyword list.

## Notes and limits

- Descriptions must be in the language passed to `--lang`; the keyword list and
  the spaCy vectors are language-specific.
- ARASAAC's keyword pool here is the set behind its `food` search, so
  non-food words in a description usually resolve to nothing and are skipped.
- If nothing matches, the script says so and writes no image rather than
  producing an empty canvas.
- Similarity threshold is `0.6`; short or highly branded dish names ("Combo
  Ranchero") often match nothing — feed the ingredient list instead.
- Run `python <SKILL_DIR>/scripts/pictogram_generator.py --help` for the full
  flag list.

## Attribution

The pictographic symbols are property of the Government of Aragón and were
created by Sergio Palao for ARASAAC (http://www.arasaac.org), which distributes
them under a Creative Commons BY-NC-SA license. Any menu that ships these images
must carry that attribution.

Adapted from [julianfromano/aac_pictogram_generator](https://github.com/julianfromano/aac_pictogram_generator)
(CC BY-NC-SA 4.0, see `LICENSE` in this skill directory).
