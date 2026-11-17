"""Generate everything downstream of the NPC files. Safe to re-run; output is deterministic.

Writes:
  exports/voices.json            NPC id -> ElevenLabs voice and delivery
  exports/live-config.json       NPC id -> live-reaction settings (active NPCs only)
  exports/image-prompts/<id>.txt prompt block built from the NPC's look rules
  exports/claude-briefs/<id>.md  compact brief for Claude Projects and the live brain
  exports/cards/<id>.json        Character Card V3 (only with --cards)
  ROSTER.md                      table between the ROSTER markers
Retired NPCs are left out of every export but stay in the roster.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canon import ROOT, SECTIONS, Npc, h2_sections, load_fragments, load_npcs  # noqa: E402
from validate import validate  # noqa: E402

ROSTER_START = "<!-- ROSTER:START -->"
ROSTER_END = "<!-- ROSTER:END -->"

DEFAULT_PLATFORMS = {"youtube": True, "twitch": True, "instagram": True, "tiktok": False}
DEFAULT_STYLE = {"max_words": 30, "emoji": False, "signature_opener": ""}

# Body sections copied into the Claude brief, in this order.
BRIEF_SECTIONS = [
    "One-line pitch",
    "Backstory (canon)",
    "Personality & motivations",
    "How they talk",
    "Per-section behaviour",
    "Live reactions",
    "Social captions voice",
]


def _d(value) -> dict:
    return value if isinstance(value, dict) else {}


def _l(value) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _dump(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _section_roles(npc: Npc) -> dict[str, dict]:
    sections = _d(npc.meta.get("sections"))
    return {
        key: _d(sections.get(key))
        for key in SECTIONS
        if _d(sections.get(key)).get("role")
    }


def voices_export(npcs: list[Npc]) -> dict:
    out = {}
    for npc in npcs:
        voice = _d(npc.meta.get("voice"))
        if not voice.get("elevenlabs_voice_id"):
            continue
        out[npc.id] = {
            "name": npc.name,
            "voice_id": voice["elevenlabs_voice_id"],
            "model": voice.get("elevenlabs_model") or "",
            "settings": {k: v for k, v in _d(voice.get("settings")).items() if v is not None},
            "delivery": _d(voice.get("delivery")),
            "audio_tags_allowed": _l(voice.get("audio_tags_allowed")),
        }
    return out


def live_config(npcs: list[Npc]) -> dict:
    cfg = {}
    for npc in npcs:
        if npc.status != "active":
            continue
        live = _d(npc.meta.get("live"))
        rules = _d(npc.meta.get("content_rules"))
        voice = _d(npc.meta.get("voice"))
        look = _d(npc.meta.get("look"))
        cfg[npc.id] = {
            "name": npc.name,
            "species": npc.meta.get("species") or "",
            "autonomy": live.get("autonomy") or "shadow",
            "platforms": {**DEFAULT_PLATFORMS, **_d(live.get("platforms"))},
            "triggers": _l(live.get("triggers")),
            "avoid_topics": _l(live.get("avoid_topics")),
            "reply_style": {**DEFAULT_STYLE, **_d(live.get("reply_style"))},
            "max_replies_per_hour": live.get("max_replies_per_hour", 20),
            "never_say": _l(rules.get("dont")),
            "never_look": _l(look.get("never")),
            "catchphrases": _l(voice.get("catchphrases")),
            "verbal_habits": _l(voice.get("verbal_habits")),
            "sections": {key: v.get("role", "") for key, v in _section_roles(npc).items()},
            "brief": f"claude-briefs/{npc.id}.md",
        }
    return cfg


def image_prompt(npc: Npc) -> str:
    look = _d(npc.meta.get("look"))
    head = npc.name + (f", {npc.meta['species']}" if npc.meta.get("species") else "")
    lines = [f"# Generated from npcs/{npc.path.name}. Do not hand-edit.", head]
    if look.get("silhouette"):
        lines.append(f"Silhouette: {look['silhouette']}")
    if _l(look.get("palette")):
        lines.append("Palette: " + ", ".join(_l(look["palette"])))
    if look.get("wardrobe_default"):
        lines.append(f"Wardrobe: {look['wardrobe_default']}")
    if _l(look.get("signature_props")):
        lines.append("Props: " + ", ".join(_l(look["signature_props"])))
    if _l(look.get("never")):
        lines.append("Never: " + "; ".join(_l(look["never"])))
    if _l(look.get("reference_images")):
        lines.append("Reference images: " + ", ".join(_l(look["reference_images"])))
    notes = h2_sections(npc.body).get("Image-prompt notes")
    if notes:
        lines += ["", notes]
    return "\n".join(lines) + "\n"


def claude_brief(npc: Npc, fragments: dict[str, str]) -> str:
    meta = npc.meta
    voice = _d(meta.get("voice"))
    delivery = _d(voice.get("delivery"))
    rules = _d(meta.get("content_rules"))
    live = _d(meta.get("live"))
    parts = [f"<!-- Generated from npcs/{npc.path.name}. Do not hand-edit. -->", f"# {npc.name} ({npc.id})", ""]

    facts = [f"Status: {npc.status}", f"Canon version: {meta.get('canon_version')}"]
    if meta.get("species"):
        facts.append(f"Species: {meta['species']}")
    if _l(meta.get("franchise")):
        facts.append("Franchise: " + ", ".join(_l(meta["franchise"])))
    parts += [f"- {fact}" for fact in facts] + [""]

    roles = _section_roles(npc)
    if roles:
        parts.append("## Where they appear")
        for key, value in roles.items():
            extra = "; ".join(x for x in (value.get("frequency"), value.get("venue")) if x)
            parts.append(f"- {SECTIONS[key][0]}: {value['role']}" + (f" ({extra})" if extra else ""))
        parts.append("")

    voice_lines = [f"- {k.capitalize()}: {v}" for k, v in delivery.items() if v]
    if _l(voice.get("verbal_habits")):
        voice_lines.append("- Verbal habits: " + "; ".join(_l(voice["verbal_habits"])))
    if _l(voice.get("catchphrases")):
        voice_lines.append("- Catchphrases: " + "; ".join(_l(voice["catchphrases"])))
    if _l(voice.get("audio_tags_allowed")):
        voice_lines.append("- Audio tags allowed: " + " ".join(_l(voice["audio_tags_allowed"])))
    if voice.get("sample_line"):
        voice_lines.append(f"- Sample line: {voice['sample_line']}")
    if voice_lines:
        parts += ["## Voice signature"] + voice_lines + [""]

    rule_lines = []
    if _l(rules.get("do")):
        rule_lines.append("- Do: " + "; ".join(_l(rules["do"])))
    if _l(rules.get("dont")):
        rule_lines.append("- Never: " + "; ".join(_l(rules["dont"])))
    if rules.get("rating"):
        rule_lines.append(f"- Rating: {rules['rating']}")
    if rule_lines:
        parts += ["## Rules"] + rule_lines + [""]

    live_lines = [f"- Autonomy: {live.get('autonomy') or 'shadow'}"]
    if _l(live.get("triggers")):
        live_lines.append("- Jumps in on: " + "; ".join(_l(live["triggers"])))
    if _l(live.get("avoid_topics")):
        live_lines.append("- Avoids: " + "; ".join(_l(live["avoid_topics"])))
    style = {**DEFAULT_STYLE, **_d(live.get("reply_style"))}
    live_lines.append(f"- Replies up to {style['max_words']} words; emoji {'allowed' if style['emoji'] else 'not allowed'}")
    parts += ["## Live reaction settings"] + live_lines + [""]

    relationships = [r for r in (meta.get("relationships") or []) if isinstance(r, dict) and r.get("with")]
    if relationships:
        parts.append("## Relationships")
        parts += [f"- {r['with']}: {r.get('dynamic', '')}".rstrip(": ") for r in relationships]
        parts.append("")

    shared = [(name, fragments[name]) for name in _l(meta.get("fragments")) if name in fragments]
    if shared:
        parts.append("## Shared traits")
        for name, text in shared:
            parts += [f"### {name}", text, ""]

    body = h2_sections(npc.body)
    for heading in BRIEF_SECTIONS:
        if body.get(heading):
            parts += [f"## {heading}", body[heading], ""]

    return "\n".join(parts).rstrip() + "\n"


def character_card(npc: Npc) -> dict:
    body = h2_sections(npc.body)
    voice = _d(npc.meta.get("voice"))
    catchphrases = _l(voice.get("catchphrases"))
    description = "\n\n".join(t for t in (body.get("One-line pitch"), body.get("Backstory (canon)")) if t)
    return {
        "spec": "chara_card_v3",
        "spec_version": "3.0",
        "data": {
            "name": npc.name,
            "description": description,
            "personality": body.get("Personality & motivations", ""),
            "scenario": "",
            "first_mes": catchphrases[0] if catchphrases else "",
            "mes_example": body.get("How they talk", ""),
            "creator_notes": f"Exported from hai-npc-canon ({npc.id}). The Markdown file is canon, not this card.",
            "system_prompt": "",
            "post_history_instructions": "",
            "alternate_greetings": catchphrases[1:],
            "tags": _l(npc.meta.get("franchise")),
            "creator": "HomelandAI",
            "character_version": str(npc.meta.get("canon_version")),
            "group_only_greetings": [],
            "extensions": {
                "hai": {
                    "id": npc.id,
                    "species": npc.meta.get("species") or "",
                    "sections": {key: v.get("role", "") for key, v in _section_roles(npc).items()},
                    "voice_id": voice.get("elevenlabs_voice_id") or "",
                    "look": _d(npc.meta.get("look")),
                }
            },
        },
    }


def _cell(value) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def roster_table(npcs: list[Npc]) -> str:
    if not npcs:
        return "_No NPCs yet._"
    rows = ["| ID | Name | Species | Status | Sections | Franchise |", "|---|---|---|---|---|---|"]
    for npc in sorted(npcs, key=lambda n: n.id):
        sections = ", ".join(SECTIONS[key][0] for key in _section_roles(npc))
        franchise = ", ".join(_l(npc.meta.get("franchise")))
        rows.append(
            f"| {_cell(npc.id)} | {_cell(npc.name)} | {_cell(npc.meta.get('species'))} "
            f"| {_cell(npc.status)} | {_cell(sections)} | {_cell(franchise)} |"
        )
    return "\n".join(rows)


def update_roster(root: Path, table: str) -> None:
    path = root / "ROSTER.md"
    text = path.read_text(encoding="utf-8")
    if ROSTER_START not in text or ROSTER_END not in text:
        raise SystemExit("ROSTER.md is missing its ROSTER:START / ROSTER:END markers")
    head, rest = text.split(ROSTER_START, 1)
    _, tail = rest.split(ROSTER_END, 1)
    path.write_text(f"{head}{ROSTER_START}\n{table}\n{ROSTER_END}{tail}", encoding="utf-8")


def build(root: Path = ROOT, with_cards: bool = False) -> list[str]:
    everyone = load_npcs(root)
    npcs = [n for n in everyone if n.status != "retired"]
    fragments = load_fragments(root)
    exports = root / "exports"

    for sub in ("image-prompts", "claude-briefs") + (("cards",) if with_cards else ()):
        shutil.rmtree(exports / sub, ignore_errors=True)
    exports.mkdir(exist_ok=True)

    _write(exports / "voices.json", _dump(voices_export(npcs)))
    _write(exports / "live-config.json", _dump(live_config(npcs)))
    for npc in npcs:
        _write(exports / "image-prompts" / f"{npc.id}.txt", image_prompt(npc))
        _write(exports / "claude-briefs" / f"{npc.id}.md", claude_brief(npc, fragments))
        if with_cards:
            _write(exports / "cards" / f"{npc.id}.json", _dump(character_card(npc)))

    update_roster(root, roster_table(everyone))
    return [n.id for n in npcs]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--cards", action="store_true", help="also write Character Card V3 JSON")
    args = parser.parse_args()

    errors, warnings = validate(args.root)
    for message in warnings:
        print(f"WARNING  {message}")
    if errors:
        for message in errors:
            print(f"ERROR    {message}")
        print("\nFix these before building exports.")
        return 1

    built = build(args.root, with_cards=args.cards)
    print(f"Built exports for {len(built)} NPC(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
