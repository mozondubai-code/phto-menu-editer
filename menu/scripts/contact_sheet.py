"""Build a labelled contact sheet of the dish images, for eyeballing a batch at once.

Usage:
    python menu/scripts/contact_sheet.py --dirs menu/images/from_pdf menu/images/hd --out menu/images/contact_sheet.jpg
"""

import argparse
import glob
import os

from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dirs", nargs="+", default=["menu/images/from_pdf", "menu/images/hd"])
    parser.add_argument("--out", default="menu/images/contact_sheet.jpg")
    parser.add_argument("--cell", type=int, default=360)
    parser.add_argument("--cols", type=int, default=4)
    args = parser.parse_args()

    paths = sorted(p for d in args.dirs for ext in ("jpg", "png")
                   for p in glob.glob(os.path.join(d, f"*.{ext}")) if not os.path.basename(p).startswith("_"))
    if not paths:
        raise SystemExit("no images found in " + ", ".join(args.dirs))

    cols = min(args.cols, len(paths))
    rows = (len(paths) + cols - 1) // cols
    label_h = 26
    sheet = Image.new("RGB", (cols * args.cell, rows * (args.cell + label_h)), "white")
    draw = ImageDraw.Draw(sheet)

    for i, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((args.cell, args.cell))
        cx, cy = (i % cols) * args.cell, (i // cols) * (args.cell + label_h)
        sheet.paste(img, (cx + (args.cell - img.width) // 2, cy + label_h + (args.cell - img.height) // 2))
        draw.text((cx + 6, cy + 7), os.path.splitext(os.path.basename(path))[0][:44], fill="black")

    sheet.save(args.out, "JPEG", quality=92)
    print(f"{len(paths)} images -> {args.out} ({sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
