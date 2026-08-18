---
name: gpt-image
description: Generate and edit images using OpenAI's gpt-image-2 model via CLI scripts. Use this skill whenever the user asks to generate, create, edit, modify, composite, restyle, or transform images using GPT image generation — including requests like "generate an image of...", "create a logo", "make an ad", "edit this photo", "apply style transfer", "put this person in a scene", "translate the text in this image", "make a comic strip", "create a UI mockup", "create an infographic", or any prompt-to-image or image-to-image workflow. Also trigger for requests involving product mockups, virtual try-on, lighting/weather changes, object removal, sketch-to-render, or multi-image compositing. If the user mentions GPT image, gpt-image-2, OpenAI image generation, or DALL-E-style workflows, use this skill. Always use this skill — don't attempt to call the OpenAI image API from memory.
---

# GPT Image Skill

Generate and edit images using OpenAI's `gpt-image-2` model through two CLI scripts.

## Setup

No install step needed — scripts use PEP 723 inline metadata. `uv run` handles dependency resolution automatically on first invocation.

The scripts read `OPENAI_API_KEY` from the environment. Two ways to provide it:

1. **Exported in the user's shell** (preferred, and standard for most CLI tools):
   ```bash
   export OPENAI_API_KEY=sk-...
   ```
   Typically placed in `~/.zshrc` / `~/.bashrc` so it survives across sessions. If it's already set for other OpenAI tools, nothing more to do.

2. **`.env` file** in the skill root (`<SKILL_DIR>/.env`), as a fallback when the shell export isn't set:
   ```
   OPENAI_API_KEY=sk-...
   ```

An already-exported shell variable takes precedence over `.env`, so both can coexist. If neither is present, the scripts exit with a clear error — remind the user to pick one.

## Two Scripts

| Script | Purpose | When to use |
|--------|---------|-------------|
| `scripts/generate.py` | Text → image (generation) | No input image. Creating from scratch. |
| `scripts/edit.py` | Text + image(s) → image (editing) | Has 1-10 input images. Modifying, compositing, restyling. |

## Quick Decision

- **User has no images** → `generate.py`
- **User provides image(s)** → `edit.py`
- **User wants variants** → add `--n 2` (or 3, 4) to either script

## generate.py — Full Reference

```bash
uv run <SKILL_DIR>/scripts/generate.py \
  --prompt "Your prompt here" \
  --output /path/to/output.png \
  --size 1024x1536 \
  --quality medium \
  --output-format png \
  --n 1 \
  --env-file <SKILL_DIR>/.env
```

| Flag | Required | Default | Values |
|------|----------|---------|--------|
| `--prompt` | Yes | — | The generation prompt |
| `--output` | No | `output.<format>` | File path for the result |
| `--size` | No | `1024x1024` | `auto` or any valid WxH (see Size Constraints) |
| `--quality` | No | `medium` | `low`, `medium`, `high`, `auto` |
| `--output-format` | No | `png` | `png`, `jpeg`, `webp` |
| `--output-compression` | No | — | `0`–`100` (only with jpeg/webp) |
| `--n` | No | `1` | `1`–`4` variants |
| `--env-file` | No | `../.env` | Path to .env with OPENAI_API_KEY |

When `--n` > 1, outputs are saved as `output_1.png`, `output_2.png`, etc.

## edit.py — Full Reference

```bash
uv run <SKILL_DIR>/scripts/edit.py \
  --prompt "Your edit instruction" \
  --images input1.png input2.png \
  --output /path/to/output.png \
  --size 1024x1536 \
  --quality medium \
  --output-format png \
  --n 1 \
  --env-file <SKILL_DIR>/.env
```

| Flag | Required | Default | Values |
|------|----------|---------|--------|
| `--prompt` | Yes | — | The editing instruction |
| `--images` | Yes | — | 1–10 input image paths |
| `--output` | No | `output.<format>` | File path for the result |
| `--size` | No | `1024x1024` | `auto` or any valid WxH (see Size Constraints) |
| `--quality` | No | `medium` | `low`, `medium`, `high`, `auto` |
| `--output-format` | No | `png` | `png`, `jpeg`, `webp` |
| `--output-compression` | No | — | `0`–`100` (only with jpeg/webp) |
| `--n` | No | `1` | `1`–`4` variants |
| `--env-file` | No | `../.env` | Path to .env with OPENAI_API_KEY |

### Multi-image editing

Pass multiple `--images` for compositing, style transfer, virtual try-on, etc.
Reference images by index in your prompt: "Image 1 is the scene, Image 2 is the style reference."

## Size Constraints (gpt-image-2)

Both edges must be multiples of 16. Max edge ≤ 3840px. Ratio ≤ 3:1.
Total pixels: 655,360 – 8,294,400. Above 2K (3,686,400 px) is experimental.

Pass `--size auto` to let the model pick.

Common sizes:

| Use case | Size |
|----------|------|
| Square (default) | `1024x1024` |
| Portrait | `1024x1536` |
| Landscape | `1536x1024` |
| Widescreen / slide | `1536x864` |
| 2K / QHD | `2560x1440` |
| 4K landscape | `3840x2160` |
| 4K portrait | `2160x3840` |

The scripts validate size automatically and print a warning above 2K.

## Quality Guide

| Setting | When to use |
|---------|-------------|
| `low` | Speed-critical, high-volume batches, previews, experimentation |
| `medium` | Default for most production work — good balance of quality and speed |
| `high` | Small or dense text, detailed infographics, close-up portraits, identity-sensitive edits |
| `auto` | Let the model pick based on the prompt |

## Output Format

`gpt-image-2` returns PNG by default. Pass `--output-format jpeg` or `--output-format webp` for smaller files and faster generation. For lossy formats, add `--output-compression 0-100` to control quality/size tradeoff.

**Note:** `gpt-image-2` does **not** support transparent backgrounds. If you need alpha transparency, run a downstream background-removal step on an opaque PNG output.

## Prompting — Read Before Writing Any Prompt

Before crafting a prompt, read `references/prompting-guide.md` for detailed patterns.

Key principles in brief:

1. **Structure**: background/scene → subject → key details → constraints. Include intended use.
2. **Be specific**: name materials, textures, visual medium. Add "photorealistic" for photo outputs.
3. **Composition**: specify framing, angle, lighting, layout placement.
4. **People**: describe scale, body framing, gaze, object interactions.
5. **Constraints**: state exclusions ("no watermark") and invariants ("preserve identity").
6. **Text in images**: put literal text in quotes, specify typography, use `high` quality for dense text.
7. **Multi-image**: reference by index + description, explain how images interact.
8. **Iterate**: start clean, refine with small single-change follow-ups.

## Workflow Patterns

### Generate: Infographic
```bash
uv run <SKILL_DIR>/scripts/generate.py \
  --prompt "Create a detailed infographic about [topic]. Include [data points]. Clean layout, clear labels, readable text. White background." \
  --size 1024x1536 --quality high \
  --output infographic.png
```

### Generate: Photorealistic image
```bash
uv run <SKILL_DIR>/scripts/generate.py \
  --prompt "Create a photorealistic photograph of [subject]. [Camera/lens details]. [Lighting]. Natural texture, no retouching." \
  --size 1024x1536 --quality medium \
  --output photo.png
```

### Generate: Logo (multiple variants)
```bash
uv run <SKILL_DIR>/scripts/generate.py \
  --prompt "Create an original logo for [brand]. [Brand personality]. Clean vector-like shapes, strong silhouette, flat design, plain background. No watermark." \
  --size 1024x1024 --quality medium --n 4 \
  --output logo.png
```

### Generate: Ad creative
```bash
uv run <SKILL_DIR>/scripts/generate.py \
  --prompt "Create a polished ad for [brand]. [Audience + vibe]. Tagline: \"EXACT TEXT HERE\". Clean composition, legible typography. No extra text, no watermarks." \
  --size 1024x1536 --quality medium \
  --output ad.png
```

### Generate: UI mockup
```bash
uv run <SKILL_DIR>/scripts/generate.py \
  --prompt "Create a realistic mobile app UI mockup for [app concept]. [Layout details]. Clean typography, minimal decoration. Place in an iPhone frame." \
  --size 1024x1536 --quality medium \
  --output mockup.png
```

### Generate: Comic strip
```bash
uv run <SKILL_DIR>/scripts/generate.py \
  --prompt "Create a vertical comic strip with 4 panels. Panel 1: [scene]. Panel 2: [scene]. Panel 3: [scene]. Panel 4: [scene]." \
  --size 1024x1536 --quality medium \
  --output comic.png
```

### Edit: Style transfer
```bash
uv run <SKILL_DIR>/scripts/edit.py \
  --prompt "Use the same style from the input image and generate [new subject]. Keep the same [style cues]. White background." \
  --images style_reference.png \
  --size 1024x1536 --quality medium \
  --output styled.png
```

### Edit: Product mockup / clean background
```bash
uv run <SKILL_DIR>/scripts/edit.py \
  --prompt "Extract the product, place on plain white background. Preserve product geometry and label legibility. Add subtle contact shadow. Do not restyle." \
  --images product_photo.png \
  --size 1024x1536 --quality medium \
  --output mockup.png
```

### Edit: Virtual try-on
```bash
uv run <SKILL_DIR>/scripts/edit.py \
  --prompt "Dress the person using the provided clothing images. Do not change face, body shape, pose, or identity. Replace only clothing with realistic fit. Match lighting and shadows." \
  --images person.png top.png jacket.png shoes.png \
  --size 1024x1536 --quality medium \
  --output tryon.png
```

### Edit: Object removal
```bash
uv run <SKILL_DIR>/scripts/edit.py \
  --prompt "Remove [object] from the image. Do not change anything else." \
  --images input.png \
  --size 1024x1536 --quality medium \
  --output cleaned.png
```

### Edit: Scene compositing (multi-image)
```bash
uv run <SKILL_DIR>/scripts/edit.py \
  --prompt "Place the [element] from Image 2 into Image 1, next to [anchor]. Match lighting, perspective, scale, and shadows. Do not change anything else." \
  --images scene.png element.png \
  --size 1024x1536 --quality medium \
  --output composite.png
```

### Edit: Translation
```bash
uv run <SKILL_DIR>/scripts/edit.py \
  --prompt "Translate all text in the image to [language]. Do not change any other aspect of the image." \
  --images original.png \
  --size 1024x1536 --quality medium \
  --output translated.png
```

### Edit: Lighting / weather change
```bash
uv run <SKILL_DIR>/scripts/edit.py \
  --prompt "Make it look like [weather/time]. Preserve all objects, camera angle, and composition." \
  --images original.png \
  --size 1024x1536 --quality medium \
  --output transformed.png
```

### Edit: Sketch to photorealistic render
```bash
uv run <SKILL_DIR>/scripts/edit.py \
  --prompt "Turn this drawing into a photorealistic image. Preserve exact layout, proportions, and perspective. Choose realistic materials and lighting. Do not add new elements or text." \
  --images sketch.png \
  --size 1024x1536 --quality medium \
  --output render.png
```

## Error Handling

The scripts validate:
- `.env` exists and contains `OPENAI_API_KEY`
- Size meets all gpt-image-2 constraints (multiples of 16, ratio, pixel count)
- `--output-compression` only used with jpeg/webp and in range 0-100
- Input images exist (edit mode)
- Image count ≤ 10 (edit mode)

If something fails, read the error message — it explains what constraint was violated.

## Output

Save generated images to the path specified by `--output`, defaulting to the current working directory. After saving, surface the file path(s) to the user so they can open or preview them. If the user supplied input images for an edit, use the exact paths they provided — don't move or copy them.
