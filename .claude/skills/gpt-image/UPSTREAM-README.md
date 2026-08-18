# GPT Image - Claude Code Skill

Claude can't reliably call OpenAI's image API from memory. The surface keeps moving, the size constraints are easy to get wrong, and more often than not Claude either guesses the signature or silently skips "generate me an image" tasks entirely. This skill fixes that.

Two CLI scripts wrapped as a [Claude Code](https://claude.com/claude-code) skill: `generate.py` for text-to-image with `gpt-image-2`, and `edit.py` for editing or compositing up to 10 reference images. Dependencies install on first run via `uv` and PEP 723 inline metadata. No glue code. No boilerplate.

## Requirements

| Requirement | Purpose |
|---|---|
| **[uv](https://docs.astral.sh/uv/)** | Runs the scripts and manages dependencies automatically. No `pip install` needed. |
| **OpenAI API key** | Must have access to `gpt-image-2`. Requires [API organization verification](https://help.openai.com/en/articles/10910291-api-organization-verification). |
| **Claude Code** (optional) | Only needed if you want Claude to invoke the skill automatically. The scripts also work standalone. |

### Installing uv

`uv` is a fast Python package manager from Astral. It replaces `pip` + `venv` + `pyenv` with a single tool that's roughly 10-100x faster. These scripts rely on `uv run` to fetch dependencies on first invocation, so it must be installed.

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Homebrew:**
```bash
brew install uv
```

**Verify the install:**
```bash
uv --version
```

If `uv` isn't on your PATH after install, restart your shell or follow the on-screen instructions from the installer. Full docs: <https://docs.astral.sh/uv/getting-started/installation/>.

## Setup

**1. Clone or copy the skill into your Claude Code skills directory.**

```bash
# User-wide (recommended)
git clone https://github.com/dshark3y/gpt-image-2-skill.git ~/.claude/skills/gpt-image

# Or project-scoped
git clone https://github.com/dshark3y/gpt-image-2-skill.git <project>/.claude/skills/gpt-image
```

The skill itself lives in the `gpt-image/` subdirectory of this repo. That's what Claude Code picks up.

**2. Add your OpenAI API key.**

The scripts read `OPENAI_API_KEY` from the environment. You have two options:

**Option A - export in your shell** (recommended; matches how most CLI tools work):

```bash
# Add to ~/.zshrc or ~/.bashrc so it sticks across sessions
export OPENAI_API_KEY="sk-..."
```

Reload your shell (`source ~/.zshrc`) or open a new terminal. If you already have the key exported for another OpenAI tool, you're done. No extra step.

**Option B - `.env` file in the skill directory** (good for project-scoped keys):

```bash
cp gpt-image/.env.example gpt-image/.env
# then edit gpt-image/.env and paste your key
```

The scripts look for a shell-exported `OPENAI_API_KEY` first and fall back to `.env`. Both can coexist; the shell export wins. `.env` is gitignored so your key won't end up in commits.

**3. Done.** First invocation triggers `uv` to install `openai` (takes a couple of seconds). Every subsequent run is instant.

## Usage

### As a Claude Code skill (recommended)

Just ask Claude normally. The skill description covers generation, editing, compositing, logos, ads, UI mockups, infographics, product mockups, virtual try-on, style transfer, lighting/weather changes, object removal, translation, sketch-to-render, comic strips, and more. Claude picks the right script, crafts the prompt, and saves the result.

### As standalone CLI scripts

Generate from scratch:
```bash
uv run gpt-image/scripts/generate.py \
  --prompt "A vintage 1960s travel poster for Kyoto in autumn" \
  --size 1024x1536 \
  --quality high \
  --output kyoto.png
```

Edit an existing image:
```bash
uv run gpt-image/scripts/edit.py \
  --prompt "Replace the sky with a dramatic thunderstorm. Keep everything else identical." \
  --images photo.jpg \
  --output photo-stormy.png
```

Multi-image compositing:
```bash
uv run gpt-image/scripts/edit.py \
  --prompt "Place the dog from Image 2 next to the woman in Image 1. Match lighting and scale." \
  --images scene.png dog.png \
  --output composite.png
```

Four logo variants at once:
```bash
uv run gpt-image/scripts/generate.py \
  --prompt "Original logo for 'Field & Flour', a local bakery. Warm, simple, timeless. Flat vector shapes, strong silhouette, plain background." \
  --n 4 \
  --output logo.png
# → logo_1.png, logo_2.png, logo_3.png, logo_4.png
```

## Flag reference

### `generate.py`

| Flag | Required | Default | Values |
|------|----------|---------|--------|
| `--prompt` | yes | - | The generation prompt |
| `--output` | no | `output.<format>` | File path for the result |
| `--size` | no | `1024x1024` | `auto` or any valid `WxH` (see [size constraints](#size-constraints)) |
| `--quality` | no | `medium` | `low`, `medium`, `high`, `auto` |
| `--output-format` | no | `png` | `png`, `jpeg`, `webp` |
| `--output-compression` | no | - | `0`-`100` (only with jpeg/webp) |
| `--n` | no | `1` | `1`-`4` variants |
| `--env-file` | no | `../.env` | Path to `.env` with `OPENAI_API_KEY` |

### `edit.py`

All of the above, plus:

| Flag | Required | Default | Values |
|------|----------|---------|--------|
| `--images` | yes | - | 1-10 input image paths |

## Size constraints

`gpt-image-2` accepts any resolution that satisfies all of these rules:

- Both edges must be **multiples of 16**
- Max edge **≤ 3840 px**
- Long-to-short ratio **≤ 3:1**
- Total pixels **655,360 to 8,294,400**

Above **2560x1440** (2K / 3.69M pixels) is officially experimental. Expect more variance. The scripts print a warning but don't block.

Common sizes that satisfy every constraint:

| Use case | Size |
|----------|------|
| Square (default) | `1024x1024` |
| Portrait | `1024x1536` |
| Landscape | `1536x1024` |
| Widescreen / slide | `1536x864` |
| 2K / QHD | `2560x1440` |
| 4K landscape | `3840x2160` |
| 4K portrait | `2160x3840` |

Pass `--size auto` to let the model pick.

## Quality guide

| Setting | When to use |
|---------|-------------|
| `low` | Speed-critical, high-volume batches, previews, rapid iteration |
| `medium` | Default. Good balance of quality and speed. |
| `high` | Dense text, infographics, close-up portraits, identity-sensitive edits |
| `auto` | Let the model pick based on prompt |

## Prompting

See [`gpt-image/references/prompting-guide.md`](gpt-image/references/prompting-guide.md) for core patterns, and the "Workflow Patterns" section of [`gpt-image/SKILL.md`](gpt-image/SKILL.md) for copy-pasteable recipes covering infographics, logos, ads, UI mockups, photorealism, virtual try-on, sketch-to-render, scene compositing, and more.

Three principles that actually change output quality:

1. **Structure beats creativity.** Scene, subject, details, constraints, in that order. Prompts that wander produce images that wander.
2. **For edits, restate what to preserve on every iteration.** Skip this and the model drifts: faces change, layouts shift, text mutates. The "preserve" list matters more than the "change" list.
3. **Quote literal text and use `--quality high` for dense typography.** Otherwise you get close-but-not-verbatim output, usually on the most important word.

## Limitations & intentional omissions

A couple of things this skill deliberately doesn't do, and why.

- **No transparent backgrounds.** `gpt-image-2` does not currently support `background: "transparent"`. The OpenAI API rejects the request. Earlier GPT Image models (`gpt-image-1`, `gpt-image-1.5`) did support it, but this skill targets `gpt-image-2` exclusively, so the flag isn't exposed. If you need alpha transparency, run a downstream background-removal step on the opaque PNG output.

- **No `input_fidelity` flag.** The OpenAI documentation is internally inconsistent on this parameter:
  - The **formal API reference** states: *"For `gpt-image-2`, omit this parameter; the API doesn't allow changing it because the model processes every image input at high fidelity automatically."*
  - The **OpenAI Cookbook** prompting guide, however, shows `input_fidelity="high"` being passed to `gpt-image-2` in several edit examples (sections 5.6 to 5.9).

  Rather than expose a flag that might work or might 400 depending on which side of the doc is authoritative on any given day, this skill omits it entirely and trusts the formal API reference: `gpt-image-2` already processes inputs at high fidelity by default, so passing the flag would be a no-op in the best case.

## Other notes

- **Organization verification required.** OpenAI requires [API organization verification](https://help.openai.com/en/articles/10910291-api-organization-verification) for all GPT Image models. If you get a 403, check your org settings.
- **Cost is token-based.** `gpt-image-2` pricing scales with quality x size. `low` is dramatically cheaper than `high`. See [OpenAI's pricing page](https://openai.com/api/pricing/) for current rates. At time of writing, `medium` 1024x1024 is $0.053/image and `high` 1024x1024 is $0.211/image.
- **Latency.** Complex prompts or high quality settings can take up to 2 minutes. `low` is typically a few seconds.

## Project layout

```
gpt-image/
├── SKILL.md                   # Claude's instructions for using the skill
├── .env                       # Your OPENAI_API_KEY (gitignored, you create this)
├── .env.example               # Template
├── scripts/
│   ├── generate.py            # Text → image
│   └── edit.py                # Image(s) → image
└── references/
    └── prompting-guide.md     # Detailed prompting patterns
```

## Packaging as a `.skill` file

Claude Code can load a skill from a zipped `.skill` bundle. Useful if you want to move a pre-configured copy to another machine or share it with a teammate. Here's the full path from zero.

### 1. Install `uv`

`uv` is the runtime the scripts depend on. (Not `uvx`, which is `uv`'s ephemeral tool runner and isn't what PEP 723 inline scripts need.)

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Homebrew:**
```bash
brew install uv
```

Verify:
```bash
uv --version
```

### 2. Create an OpenAI API key

1. Go to <https://platform.openai.com/api-keys> and sign in.
2. Click **Create new secret key**, name it something like `gpt-image-skill`, and copy the value (starts with `sk-`).
3. If you haven't already, complete [API organization verification](https://help.openai.com/en/articles/10910291-api-organization-verification) from <https://platform.openai.com/settings/organization/general>. This is **required** for all GPT Image models. Without it, `gpt-image-2` requests return 403.

### 3. Provide the API key

The scripts check a shell-exported `OPENAI_API_KEY` first, then fall back to a `.env` file inside the skill directory. Pick whichever fits your flow:

**Shell export** (no `.env` needed; key travels with your shell, not the bundle):

```bash
export OPENAI_API_KEY="sk-your-real-key-here"
# Add the same line to ~/.zshrc or ~/.bashrc if you want it to persist.
```

**`.env` inside the skill** (key travels with the bundle; convenient for personal redistribution across your own machines, but strip it before sharing):

```bash
cp gpt-image/.env.example gpt-image/.env
echo "OPENAI_API_KEY=sk-your-real-key-here" > gpt-image/.env
cat gpt-image/.env  # confirm
```

### 4. Zip into a `.skill` bundle

From the repo root:

```bash
zip -r gpt-image.skill gpt-image/
```

That produces `gpt-image.skill`, a single file you can move, share, or install into another Claude Code environment. Drop `.DS_Store` files from the archive while you're at it:

```bash
zip -r gpt-image.skill gpt-image/ -x "*.DS_Store"
```

**⚠ Sharing with others?** Strip your `.env` first so your API key doesn't travel with the bundle. Recipients repeat step 3 on their own machine.

```bash
rm gpt-image/.env
zip -r gpt-image.skill gpt-image/ -x "*.DS_Store"
```

### 5. Install the bundle

Unzip the `.skill` into your Claude Code skills directory. Same as the normal [Setup](#setup) flow, just from a bundle instead of a clone:

```bash
unzip gpt-image.skill -d ~/.claude/skills/
```

Claude Code picks it up on next launch. If you stripped the `.env` in step 4, repeat step 3 on the target machine.

## Contributing

PRs welcome. If it misbehaves on a specific workflow, open an issue with the prompt, flags, and output.

## License

MIT. Do whatever you want.
