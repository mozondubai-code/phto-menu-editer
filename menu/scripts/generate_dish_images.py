"""Produce a dish photo for every menu item that does not have one yet.

Reads menu/data/menu.json and, for each item whose image_status is
"needs_generation", runs the repo's gpt-image skill to render a menu tile,
then writes an HD (2048px) copy alongside it. Already-rendered slugs are
skipped, so the run is resumable and can be filtered per section.

Requires OPENAI_API_KEY (exported, or in .claude/skills/gpt-image/.env).

Usage:
    python menu/scripts/generate_dish_images.py --dry-run
    python menu/scripts/generate_dish_images.py --section "Special Soups"
    python menu/scripts/generate_dish_images.py --limit 10 --quality high
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageFilter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILL_DIR = os.path.join(REPO_ROOT, ".claude", "skills", "gpt-image")
GENERATE = os.path.join(SKILL_DIR, "scripts", "generate.py")
ENV_FILE = os.path.join(SKILL_DIR, ".env")


def preflight(dry_run):
    if dry_run:
        return
    if not shutil.which("uv"):
        sys.exit("uv is not installed — see https://docs.astral.sh/uv/getting-started/installation/")
    if not os.environ.get("OPENAI_API_KEY") and not os.path.exists(ENV_FILE):
        sys.exit(f"No OPENAI_API_KEY in the environment and no {ENV_FILE}. "
                 "Export the key or write it to that file, then re-run.")


def to_hd(src, dest, long_edge=2048):
    img = Image.open(src).convert("RGB")
    scale = long_edge / max(img.size)
    if scale > 1:
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=90, threshold=3))
    img.save(dest, "JPEG", quality=95, subsampling=0)
    return img.size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--menu", default="menu/data/menu.json")
    parser.add_argument("--out-dir", default="menu/images/generated")
    parser.add_argument("--hd-dir", default="menu/images/hd")
    parser.add_argument("--section", help="Only this section_en")
    parser.add_argument("--slug", help="Only this slug")
    parser.add_argument("--limit", type=int, help="Stop after N images")
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--dry-run", action="store_true", help="Print what would run, call nothing")
    args = parser.parse_args()

    preflight(args.dry_run)
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.hd_dir, exist_ok=True)

    menu = json.load(open(args.menu, encoding="utf-8"))
    todo = [i for i in menu["items"] if i["image_status"] == "needs_generation"]
    if args.section:
        todo = [i for i in todo if i["section_en"] == args.section]
    if args.slug:
        todo = [i for i in todo if i["slug"] == args.slug]

    done = failed = 0
    for item in todo:
        out = os.path.join(args.out_dir, f"{item['slug']}.png")
        hd = os.path.join(args.hd_dir, f"{item['slug']}.jpg")
        if os.path.exists(hd):
            continue
        if args.limit is not None and done >= args.limit:
            break

        label = f"{item['slug']} ({item['name_en']})"
        if args.dry_run:
            print(f"would generate {label}")
            done += 1
            continue

        cmd = ["uv", "run", GENERATE, "--prompt", item["image_prompt"], "--output", out,
               "--size", args.size, "--quality", args.quality, "--output-format", "png"]
        if os.path.exists(ENV_FILE):
            cmd += ["--env-file", ENV_FILE]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(out):
            failed += 1
            print(f"FAILED {label}: {result.stderr.strip().splitlines()[-1] if result.stderr.strip() else 'no output'}")
            continue
        size = to_hd(out, hd)
        done += 1
        print(f"{done:>3}/{len(todo)} {label} -> {hd} {size[0]}x{size[1]}")

    print(f"\ngenerated {done}, failed {failed}, remaining {len(todo) - done - failed}")


if __name__ == "__main__":
    main()
