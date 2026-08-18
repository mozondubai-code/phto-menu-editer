# phto-menu-editer

Restaurant site plus the Claude Code skills used to build picture-based menus for it.

The web app is the [Gericht restaurant template](https://github.com/namrata121212/Restaurant-Website)
(Create React App): navbar, header, about, special menu, chef, awards, gallery,
find-us and footer sections, with the assets under `src/assets`.

## Running the site

```bash
npm install
npm start      # dev server on http://localhost:3000
npm run build  # production bundle in build/
npm test       # CRA test runner
```

Source layout:

- `src/components` — reusable pieces (Navbar, MenuItem, SubHeading, Footer bits)
- `src/container` — page sections (Header, AboutUs, Menu, Chef, Laurels, Gallery, FindUs, Footer, Intro)
- `src/constants` — `data.js` (menu content) and `images.js` (asset map)

## Installed skills

These live in `.claude/skills/` and load automatically in Claude Code sessions on
this repo.

| Skill | What it does |
|---|---|
| `aac-pictogram-generator` | Turns a dish description or photo into an ARASAAC pictogram board for accessible / picture menus. Needs `pip install requests pillow spacy torch transformers` then `python .claude/skills/aac-pictogram-generator/scripts/prepare_model.py`. |
| `gpt-image` | Generates and edits images with OpenAI `gpt-image-2` via `uv run`. Needs [uv](https://docs.astral.sh/uv/) and an `OPENAI_API_KEY` (exported, or in `.claude/skills/gpt-image/.env` — git-ignored). |
| `codex-imagegen` | Generates images through the Codex CLI's built-in `$imagegen` (gpt-image-2), then places and resizes the result. Needs the [`codex` CLI](https://developers.openai.com/codex) v0.130+ and `codex login`. Its Mode B (`--dangerously-bypass-approvals-and-sandbox`) hands the Codex sub-agent unapproved shell access — read the skill's `SECURITY.md` first. |

Each skill's `SKILL.md` carries its full flag reference.

## Credits

- Site template: [namrata121212/Restaurant-Website](https://github.com/namrata121212/Restaurant-Website)
- Pictogram pipeline: [julianfromano/aac_pictogram_generator](https://github.com/julianfromano/aac_pictogram_generator) (CC BY-NC-SA 4.0)
- GPT image skill: [dshark3y/gpt-image-2-skill](https://github.com/dshark3y/gpt-image-2-skill)
- Codex imagegen skill: [JunSeo99/claude-skill-codex-imagegen](https://github.com/JunSeo99/claude-skill-codex-imagegen) (MIT)
- Pictographic symbols are property of the Government of Aragón, created by
  Sergio Palao for [ARASAAC](http://www.arasaac.org), CC BY-NC-SA.
