"""Validate the NPC canon. Exits with code 1 if any error is found; warnings do not fail."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jsonschema import Draft202012Validator  # noqa: E402

from canon import ROOT, SECTIONS, h2_sections, load_fragments, load_npcs  # noqa: E402

# Headings an active NPC must have filled in.
REQUIRED_HEADINGS = [
    "One-line pitch",
    "Backstory (canon)",
    "Personality & motivations",
    "How they talk",
    "Per-section behaviour",
    "Live reactions",
    "Change notes",
]


def _d(value) -> dict:
    return value if isinstance(value, dict) else {}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def validate(root: Path = ROOT) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    schema = json.loads((root / "schema" / "npc.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    npcs = load_npcs(root, errors)
    fragment_names = set(load_fragments(root))
    changelog = _read(root / "CHANGELOG.md")
    all_ids = {n.id for n in npcs if n.id}

    for _key, (title, filename) in SECTIONS.items():
        if not (root / "sections" / filename).exists():
            errors.append(f"sections/{filename}: missing section brief for {title}")

    seen_ids: dict[str, str] = {}
    voice_owner: dict[str, str] = {}
    delivery_owner: dict[tuple, str] = {}

    for npc in npcs:
        label = npc.path.name
        meta = npc.meta

        for err in sorted(validator.iter_errors(meta), key=lambda e: [str(p) for p in e.absolute_path]):
            where = ".".join(str(p) for p in err.absolute_path) or "(top level)"
            errors.append(f"{label}: {where}: {err.message}")

        npc_id = npc.id
        status = npc.status
        active = status == "active"

        if npc_id:
            if npc.path.stem != npc_id:
                errors.append(f"{label}: id '{npc_id}' does not match the file name")
            if npc_id in seen_ids:
                errors.append(f"{label}: duplicate id {npc_id} (also used in {seen_ids[npc_id]})")
            else:
                seen_ids[npc_id] = label

        for rel in meta.get("relationships") or []:
            target = _d(rel).get("with")
            if not target:
                continue
            if target == npc_id:
                errors.append(f"{label}: relationship points at itself")
            elif target not in all_ids:
                errors.append(f"{label}: relationship with unknown NPC {target}")

        for fragment in meta.get("fragments") or []:
            if fragment not in fragment_names:
                errors.append(f"{label}: fragment '{fragment}' not found in fragments/")

        real = _d(meta.get("real_person"))
        if real.get("modeled_on_real_person") and real.get("permission_status") != "granted":
            message = f"{label}: modeled on a real person but permission_status is not 'granted'"
            (errors if active else warnings).append(message)

        voice = _d(meta.get("voice"))
        voice_id = voice.get("elevenlabs_voice_id")
        if voice_id and status != "retired":
            if voice_id in voice_owner:
                errors.append(
                    f"{label}: voice id already used by {voice_owner[voice_id]}; every NPC needs its own voice"
                )
            else:
                voice_owner[voice_id] = label

        delivery = _d(voice.get("delivery"))
        triple = tuple(str(delivery.get(k) or "").strip().lower() for k in ("pace", "pitch", "accent"))
        if all(triple) and status != "retired":
            if triple in delivery_owner:
                warnings.append(
                    f"{label}: same pace, pitch and accent as {delivery_owner[triple]}; they may sound alike"
                )
            else:
                delivery_owner[triple] = label

        if active:
            sections = _d(meta.get("sections"))
            if not any(_d(v).get("role") for v in sections.values()):
                errors.append(f"{label}: an active NPC needs a role in at least one section")
            headings = h2_sections(npc.body)
            for heading in REQUIRED_HEADINGS:
                if not headings.get(heading):
                    errors.append(f"{label}: an active NPC needs a filled '## {heading}' section")
            if npc_id and npc_id not in changelog:
                warnings.append(f"{label}: {npc_id} is not mentioned in CHANGELOG.md")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    errors, warnings = validate(args.root)
    count = len([p for p in (args.root / "npcs").glob("*.md") if not p.name.startswith("_")])
    for message in warnings:
        print(f"WARNING  {message}")
    for message in errors:
        print(f"ERROR    {message}")
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) in {count} NPC file(s).")
        return 1
    print(f"OK: {count} NPC file(s) valid, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
