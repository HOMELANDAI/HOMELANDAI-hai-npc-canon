# hai-npc-canon

The single source of truth for HomelandAI (HAI) NPCs, the recurring brand characters that run across Typed Out Loud, Beats Bars & Breakdowns, HAI Radio and Silent But Deadly.

One Markdown file per NPC. Everything else (voice map, image prompts, Claude briefs, live-reaction config, roster) is generated from those files, so an NPC is defined once.

## Layout

```
README.md            this file
ROSTER.md            one row per NPC (generated)
CANON-RULES.md       working rules and universe rules shared by every NPC
CHANGELOG.md         why every canon change happened
sections/            one brief per show: purpose, format, which NPCs, rules
npcs/                one file per NPC (+ _template.md)
fragments/           shared trait packs reused by several NPCs
relationships.md     NPC-to-NPC dynamics
assets/<npc-id>/     reference images
schema/npc.schema.json   the rules every NPC header must pass
scripts/             validate.py, build_exports.py
tests/               unit tests and a fixture NPC (not canon)
exports/             GENERATED, never hand-edit
.github/workflows/   validate on every push, regenerate exports on main
```

## Add an NPC

1. Copy `npcs/_template.md` to `npcs/npc-NNN-slug.md`. Use the next free number and a lowercase slug. The `id` inside must match the file name and is never reused.
2. Fill the header (machine-readable) and the body (story, voice, behaviour).
3. Run `python scripts/validate.py` and fix what it reports.
4. Add a `CHANGELOG.md` entry that says why. Claude's GitHub sync never sees commit messages, so the reason has to live in a file.
5. Commit to `main`. The build action regenerates `exports/` and `ROSTER.md`.

Status ladder: `draft` (may be mostly empty) then `active` (must be complete: species, a section role, a voice id, at least one reference image, and every key heading filled) then `retired`.

## Voice signature

Every NPC's `voice` block holds four layers:

- Voice: an ElevenLabs voice id, model and settings. No two NPCs may share a voice id.
- Delivery: pace, pitch, accent, energy. `validate.py` warns when two NPCs share all three of pace, pitch and accent.
- Verbal habits: sentence rhythm, fillers, openers and closers, plus catchphrases.
- Audio tags: the only tags the NPC may use, such as laughs or whispers.

`exports/voices.json` maps each NPC id to its voice, ready for scripts or an audio pipeline.

## Live reactions

The `live` block says how an NPC reacts to chat and comments: what triggers it, what it avoids, how long its replies run, which platforms it may speak on and how often.

Autonomy ladder, set per NPC:

1. `shadow`: the NPC drafts replies, nothing is posted.
2. `approve`: drafts wait in a queue for a human tap.
3. `auto`: posts on its own, still behind the guardrails.

Every NPC starts in `shadow`. TikTok is off by default because it has no official LIVE API. `exports/live-config.json` is what a live engine reads. That engine is not part of this repo yet.

## Use it in the "Homeland AI Brands" Claude Project

1. In the Project, add this repo through the GitHub option in the knowledge section and pick the `main` branch.
2. Select: `ROSTER.md`, `CANON-RULES.md`, `CHANGELOG.md`, `relationships.md`, `sections/`, `npcs/`, `fragments/`. Leave out `scripts/`, `tests/` and `.github/` to keep knowledge lean.
3. Press Sync after every canon change. Sync is on demand, not automatic.
4. Images may not be read by the sync. Upload reference images to the Project or the chat directly.

Each NPC file is written to make sense on its own, because on large knowledge sets Claude retrieves pieces rather than reading everything.

## Local commands

```
pip install -r scripts/requirements.txt
python scripts/validate.py
python scripts/build_exports.py            # voices, image prompts, briefs, live config, roster
python scripts/build_exports.py --cards    # also Character Card V3 JSON (optional, untested in any app)
python -m unittest discover -s tests -v
```

## Not built yet

- The live engine: chat and comment intake, triage, the NPC brain, guardrails and the approval queue.
- A Supabase mirror of NPC data (the repo stays the master; the mirror is read-only).
