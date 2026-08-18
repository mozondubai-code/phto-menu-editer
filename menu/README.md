# Bain Al Jusrain — menu data and dish photography

Source: `JUSRAIN_TRIFOLD_Brocure_AR.pdf` (Arabic trifold, 2 pages).
Restaurant: مطعم بين الجسرين / Bain Al Jusrain, Rabdan Al Maqta, Abu Dhabi.

## What is here

| Path | Contents |
|---|---|
| `data/menu.json` | All 108 items — section, Arabic name, transliteration, English name, price as printed, image status, and a ready-to-run image prompt per dish |
| `data/menu.csv` | The same table, flat, for spreadsheets |
| `images/from_pdf/` | The 5 usable dish photos lifted from the brochure at native resolution and upscaled to 2048px |
| `images/flagged/` | Brochure photos that carry someone else's watermark — do not reuse |
| `images/hd/` | HD output of generated dish photos (empty until generation runs) |
| `scripts/` | The extraction, export, generation and QC scripts |

## Menu coverage

108 dishes across 15 sections. The brochure only ever showed 8 photos, so
**103 of 108 dishes have no picture yet**.

| Section | Items |
|---|---|
| Jusrain Special Paratha | 14 |
| Hot Drinks | 7 |
| Special Soups | 11 |
| Rice Dishes | 3 |
| Rice Combo Meals | 2 |
| Bread | 3 |
| Jusrain Special Biryani | 14 |
| Special Beef Dishes | 3 |
| Special Mutton Dishes | 9 |
| Jusrain Special Pulao and Kabsa | 4 |
| Special Chicken Dishes | 10 |
| Special Charcoal Grills | 8 |
| Special Salads | 4 |
| Special Fish Dishes | 6 |
| Special Breakfast Dishes | 10 |

## Rebuilding

```bash
python menu/scripts/extract_pdf_photos.py --pdf <brochure.pdf>   # brochure photos -> HD
python menu/scripts/export_menu.py                               # menu.json + menu.csv
python menu/scripts/generate_dish_images.py --dry-run            # list what is missing
python menu/scripts/generate_dish_images.py --section "Special Soups"
python menu/scripts/contact_sheet.py                             # QC sheet of everything
```

`generate_dish_images.py` drives the repo's `gpt-image` skill, so it needs
`uv` and an `OPENAI_API_KEY` (exported, or in `.claude/skills/gpt-image/.env`).
It skips slugs that already have an HD file, so it is resumable and can be run
section by section.

## Things found in the brochure that need a decision

1. **Two brochure photos carry third-party watermarks.** The rice-combo thali is
   a watermarked Shutterstock frame, and the noodle platter carries a "Pups with
   Chopsticks" blog watermark. Neither is safe to reuse — they are recorded in
   `images/flagged/` and in `images/from_pdf/manifest.json` and both dishes are
   marked `needs_generation`.
2. **`سلطة عربية` (Arabic salad) is listed twice** in Special Salads, at 10.00 and
   at 5.00. Kept both, the 5.00 one slugged `salata-arabiya-saghira`; confirm
   which is right.
3. **`كاداي لحم بقري` (beef kadai) is printed under the mutton header.** Kept as
   printed.
4. **`نصف برياني دجاج` (20.00) costs more than `برياني دجاج` (13.00)** — reads as
   "biryani with half a chicken" rather than a half portion. Kept as printed.
5. `برياني سمك` is priced `SEASONAL` and four fish dishes are priced `APS`
   (as per size); both are carried through verbatim.
