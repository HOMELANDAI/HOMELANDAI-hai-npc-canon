"""Shared helpers for the HAI NPC canon repo: frontmatter parsing and file loading."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

FRONTMATTER_RE = re.compile(
    r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)(.*)\Z", re.DOTALL
)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# key used in NPC headers -> (display name, section brief file name)
SECTIONS = {
    "typed_out_loud": ("Typed Out Loud", "typed-out-loud.md"),
    "beats_bars_breakdowns": ("Beats Bars & Breakdowns", "beats-bars-breakdowns.md"),
    "hai_radio": ("HAI Radio", "hai-radio.md"),
    "silent_but_deadly": ("Silent But Deadly", "silent-but-deadly.md"),
}


class CanonError(Exception):
    """A canon file could not be read."""


@dataclass
class Npc:
    path: Path
    meta: dict
    body: str

    @property
    def id(self) -> str:
        return str(self.meta.get("id") or "")

    @property
    def name(self) -> str:
        return str(self.meta.get("name") or "")

    @property
    def status(self) -> str:
        return str(self.meta.get("status") or "")


def parse_text(text: str, label: str) -> tuple[dict, str]:
    """Split a Markdown file into its YAML header (a dict) and its body."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise CanonError(f"{label}: missing YAML frontmatter (the file must start with a --- block)")
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise CanonError(
            f"{label}: invalid YAML frontmatter ({exc}). Hex colours must be quoted, like \"#D4AF37\"."
        ) from exc
    if not isinstance(meta, dict):
        raise CanonError(f"{label}: frontmatter must be a set of key: value fields")
    return meta, match.group(2)


def h2_sections(body: str) -> dict[str, str]:
    """Return {heading: text} for each '## ' heading, with HTML comments removed."""
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = COMMENT_RE.sub("", "\n".join(buf)).strip()
            current = line[3:].strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = COMMENT_RE.sub("", "\n".join(buf)).strip()
    return sections


def load_npcs(root: Path = ROOT, errors: list[str] | None = None) -> list[Npc]:
    """Load every npcs/*.md except files starting with an underscore (the template)."""
    npcs: list[Npc] = []
    for path in sorted((root / "npcs").glob("*.md")):
        if path.name.startswith("_"):
            continue
        try:
            meta, body = parse_text(path.read_text(encoding="utf-8"), path.name)
        except CanonError as exc:
            if errors is None:
                raise
            errors.append(str(exc))
            continue
        npcs.append(Npc(path, meta, body))
    return npcs


def load_fragments(root: Path = ROOT) -> dict[str, str]:
    """Return {fragment name: text} for fragments/*.md (README excluded)."""
    fragments: dict[str, str] = {}
    folder = root / "fragments"
    if not folder.exists():
        return fragments
    for path in sorted(folder.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        text = path.read_text(encoding="utf-8")
        try:
            _, body = parse_text(text, path.name)
        except CanonError:
            body = text
        fragments[path.stem] = body.strip()
    return fragments
