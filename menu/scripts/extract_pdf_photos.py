"""Pull the dish photos out of the source brochure and prepare HD versions.

Reads the AR trifold PDF, extracts every embedded photo at native resolution,
keeps the ones that are actual dish photography (skipping the marble
background, the KeeTa logo and the WhatsApp QR code), and writes an enhanced
2048px-long-edge copy named after the dish it depicts.

Enhancement is non-generative: Lanczos upscale, unsharp mask, and a mild
contrast/saturation lift. It cannot invent detail that is not in the source.

Usage:
    python menu/scripts/extract_pdf_photos.py --pdf <brochure.pdf> --out menu/images/from_pdf
"""

import argparse
import json
import os

import pymupdf
from PIL import Image, ImageEnhance, ImageFilter

# xref of the source image -> (slug, dish, note)
PHOTO_MAP = {
    48: ("paratha-rolls-platter", "بَراتا جوسرين الخاصة (section hero)", "stuffed paratha rolls on a board"),
    49: ("aruz-abyad", "أرز أبيض / Plain white rice", "white rice bowl"),
    51: ("shai-karak", "شاي كرك / Karak tea", "karak tea being poured"),
    55: ("fahm-aadi", "فحم عادي / Classic charcoal grill", "grilled chicken with fries — brochure cover"),
    6: ("lahm-baqari-maqli", "لحم بقري مقلي / Beef fry", "dark chilli-glazed beef strips"),
    7: ("biryani-al-fahm-kamil", "برياني الفحم كامل / Full charcoal biryani", "whole roast chicken over biryani rice"),
}
# Extracted but deliberately not shipped.
REJECTED = {
    5: ("sahn-fransisco", "صحن فرانسيسكو", "carries a \"Pups with Chopsticks\" blog watermark — must be relicensed or reshot"),
    50: ("rice-combo-thali", "وجبات الأرز الكومبو", "carries a visible Shutterstock watermark — must be relicensed or reshot"),
    31: ("marble-background", "-", "page background texture, not a dish"),
    52: ("keeta-logo", "-", "delivery partner logo"),
    53: ("whatsapp-qr", "-", "WhatsApp QR code"),
    57: ("icon", "-", "small UI icon"),
}

TARGET_LONG_EDGE = 2048


def enhance(img, long_edge=TARGET_LONG_EDGE):
    """Upscale to HD and apply a light print-to-screen cleanup."""
    scale = long_edge / max(img.size)
    if scale > 1:
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=110, threshold=3))
    img = ImageEnhance.Contrast(img).enhance(1.06)
    img = ImageEnhance.Color(img).enhance(1.08)
    return img


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--out", default="menu/images/from_pdf")
    parser.add_argument("--raw-out", default=None, help="Also keep the untouched extracted originals here")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    if args.raw_out:
        os.makedirs(args.raw_out, exist_ok=True)

    doc = pymupdf.open(args.pdf)
    seen, manifest = set(), []
    for pno, page in enumerate(doc, 1):
        for info in page.get_images(full=True):
            xref = info[0]
            if xref in seen:
                continue
            seen.add(xref)
            blob = doc.extract_image(xref)
            if xref in REJECTED:
                slug, dish, note = REJECTED[xref]
                manifest.append(dict(xref=xref, page=pno, slug=slug, dish=dish, shipped=False, note=note))
                continue
            if xref not in PHOTO_MAP:
                manifest.append(dict(xref=xref, page=pno, slug=None, shipped=False, note="unmapped image"))
                continue

            slug, dish, note = PHOTO_MAP[xref]
            src_path = os.path.join(args.raw_out or args.out, f"_src_{slug}.{blob['ext']}")
            with open(src_path, "wb") as fh:
                fh.write(blob["image"])
            img = Image.open(src_path).convert("RGB")
            out_path = os.path.join(args.out, f"{slug}.jpg")
            enhanced = enhance(img)
            enhanced.save(out_path, "JPEG", quality=95, subsampling=0)
            if not args.raw_out:
                os.remove(src_path)
            manifest.append(dict(xref=xref, page=pno, slug=slug, dish=dish, shipped=True, note=note,
                                 source_px=f"{img.width}x{img.height}",
                                 output_px=f"{enhanced.width}x{enhanced.height}",
                                 file=os.path.relpath(out_path)))
            print(f"{slug:28} {img.width}x{img.height} -> {enhanced.width}x{enhanced.height}")

    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print(f"\nShipped {sum(1 for m in manifest if m['shipped'])} photos to {args.out}")


if __name__ == "__main__":
    main()
