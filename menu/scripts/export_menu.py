"""Turn the transcribed menu into menu.json / menu.csv plus per-dish image prompts.

Each item gets a stable slug, the price as printed, whether a photo already
exists in menu/images/, and a fully specified image prompt written in the
labeled schema both image skills expect.

Usage:
    python menu/scripts/export_menu.py [--images-dir menu/images] [--out-dir menu/data]
"""

import argparse
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from menu_source import MENU, RESTAURANT  # noqa: E402

# Dishes whose photo already exists, slug -> file (relative to the repo root).
EXISTING = {
    "aruz-abyad": "menu/images/from_pdf/aruz-abyad.jpg",
    "shai-karak": "menu/images/from_pdf/shai-karak.jpg",
    "fahm-aadi": "menu/images/from_pdf/fahm-aadi.jpg",
    "lahm-baqari-maqli": "menu/images/from_pdf/lahm-baqari-maqli.jpg",
    "biryani-al-fahm-kamil": "menu/images/from_pdf/biryani-al-fahm-kamil.jpg",
}

# Extra plating direction for dishes whose English name alone is too thin a brief.
SUBJECT_HINTS = {
    "Jusrain Special Paratha": "a flaky paratha roll sliced open to show the filling, stacked on a wooden board",
    "Hot Drinks": "the drink in the glass it is served in, steam rising",
    "Special Soups": "a bowl of soup with its garnish, spoon resting alongside",
    "Rice Dishes": "a mound of rice in a serving bowl",
    "Rice Combo Meals": "a full combo tray: rice, curries in small bowls, pickle and salad",
    "Bread": "the flatbread torn open, stacked on a plate",
    "Jusrain Special Biryani": "long-grain biryani rice with the meat on top, fried onions and coriander",
    "Special Beef Dishes": "beef curry or fry in a karahi, thick masala clinging to the meat",
    "Special Mutton Dishes": "mutton pieces on the bone in a rich masala, in a copper karahi",
    "Jusrain Special Pulao and Kabsa": "pulao rice with meat, almonds and raisins on a large platter",
    "Special Chicken Dishes": "chicken pieces coated in glossy masala, garnished with spring onion",
    "Special Charcoal Grills": "charcoal-grilled meat with visible char marks, served with fries and salad",
    "Special Salads": "a fresh salad in a white bowl, ingredients clearly separated",
    "Special Fish Dishes": "the fish plated whole or as fillets with lemon wedges and herbs",
    "Special Breakfast Dishes": "the breakfast dish in a small bowl with bread alongside",
}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_prompt(name_en, translit, name_ar, section_en):
    subject = SUBJECT_HINTS.get(section_en, "the dish plated for a menu photo")
    return "\n".join([
        "Use case: food-menu photography",
        "Asset type: square menu tile, 1024x1024, for a printed and digital restaurant menu",
        f"Primary request: appetizing photograph of {name_en} ({translit} / {name_ar}), "
        f"a {section_en.lower()} item at an Emirati and South Asian restaurant in Abu Dhabi",
        f"Subject: {subject}",
        "Scene/backdrop: dark matte slate surface with a faint warm reflection, minimal props",
        "Style/medium: high-end commercial food photography, true-to-life textures",
        "Composition/framing: 45-degree hero angle, dish centred, shallow depth of field, "
        "room around the plate so the tile can be cropped",
        "Lighting/mood: warm directional key light from the left, soft shadow falloff, "
        "glossy highlights on sauces",
        "Color: warm amber and deep aubergine accents to match the brand palette",
        "Constraints: photorealistic, no text, no logos, no watermark, no hands, no cutlery in frame",
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="menu/data")
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    items, seen = [], {}
    for section_ar, section_en, dishes in MENU:
        for name_ar, translit, name_en, price in dishes:
            slug = slugify(translit)
            seen[slug] = seen.get(slug, 0) + 1
            if seen[slug] > 1:  # e.g. Keema appears as a paratha and as a breakfast dish
                slug = f"{slug}-{slugify(section_en)}"
            image = EXISTING.get(slug)
            items.append({
                "id": len(items) + 1,
                "slug": slug,
                "section_ar": section_ar,
                "section_en": section_en,
                "name_ar": name_ar,
                "transliteration": translit,
                "name_en": name_en,
                "price_aed": price,
                "image": image,
                "image_status": "from_brochure" if image else "needs_generation",
                "image_prompt": build_prompt(name_en, translit, name_ar, section_en),
            })

    payload = {"restaurant": RESTAURANT, "source": "JUSRAIN_TRIFOLD_Brocure_AR.pdf",
               "item_count": len(items), "items": items}
    with open(os.path.join(args.out_dir, "menu.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    with open(os.path.join(args.out_dir, "menu.csv"), "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "slug", "section_en", "section_ar", "name_ar",
                                                "transliteration", "name_en", "price_aed",
                                                "image", "image_status"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items)

    have = sum(1 for i in items if i["image"])
    print(f"{len(items)} items -> {args.out_dir}/menu.json + menu.csv")
    print(f"photos present: {have} | still to produce: {len(items) - have}")


if __name__ == "__main__":
    main()
