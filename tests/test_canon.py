import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import build_exports  # noqa: E402
import validate as validate_mod  # noqa: E402

FIXTURE = (REPO / "tests" / "fixtures" / "npc-999-fixture.md").read_text(encoding="utf-8")


def make_repo(tmp: Path) -> Path:
    for name in ("schema", "sections", "fragments"):
        shutil.copytree(REPO / name, tmp / name)
    for name in ("CHANGELOG.md", "ROSTER.md"):
        shutil.copy(REPO / name, tmp / name)
    (tmp / "npcs").mkdir()
    (tmp / "exports").mkdir()
    return tmp


def swap(text: str, old: str, new: str) -> str:
    assert old in text, f"test setup: {old!r} not found in fixture"
    return text.replace(old, new, 1)


class CanonTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = make_repo(Path(self._tmp.name))

    def add(self, filename: str, text: str):
        (self.repo / "npcs" / filename).write_text(text, encoding="utf-8")

    def errors(self):
        errors, _ = validate_mod.validate(self.repo)
        return errors

    def warnings(self):
        _, warnings = validate_mod.validate(self.repo)
        return warnings

    def assertHasError(self, needle: str):
        errors = self.errors()
        self.assertTrue(any(needle in e for e in errors), f"no error containing {needle!r} in {errors}")

    def test_repo_as_shipped_is_valid(self):
        errors, _ = validate_mod.validate(REPO)
        self.assertEqual(errors, [])

    def test_template_validates_as_draft(self):
        shutil.copy(REPO / "npcs" / "_template.md", self.repo / "npcs" / "npc-000-slug.md")
        self.assertEqual(self.errors(), [])

    def test_valid_active_npc_passes(self):
        self.add("npc-999-fixture.md", FIXTURE)
        self.assertEqual(self.errors(), [])

    def test_missing_required_field(self):
        self.add("npc-999-fixture.md", swap(FIXTURE, "canon_version: 1.0.0\n", ""))
        self.assertHasError("canon_version")

    def test_active_without_voice_id_fails(self):
        self.add("npc-999-fixture.md", swap(FIXTURE, 'elevenlabs_voice_id: "TESTVOICE0001"', 'elevenlabs_voice_id: ""'))
        self.assertHasError("voice.elevenlabs_voice_id")

    def test_active_without_reference_image_fails(self):
        self.add("npc-999-fixture.md", swap(FIXTURE, '["assets/npc-999-fixture/front.png"]', "[]"))
        self.assertHasError("look.reference_images")

    def test_active_without_section_role_fails(self):
        text = swap(FIXTURE, 'role: "test host"', 'role: ""')
        text = swap(text, 'role: "test guest"', 'role: ""')
        self.add("npc-999-fixture.md", text)
        self.assertHasError("at least one section")

    def test_active_with_empty_heading_fails(self):
        text = swap(FIXTURE, "Answers test questions briefly and ignores everything else.", "")
        self.add("npc-999-fixture.md", text)
        self.assertHasError("Live reactions")

    def test_real_person_without_permission_fails_when_active(self):
        text = swap(FIXTURE, "modeled_on_real_person: false", "modeled_on_real_person: true")
        text = swap(text, "permission_status: not_applicable", "permission_status: pending")
        self.add("npc-999-fixture.md", text)
        self.assertHasError("real person")

    def test_real_person_with_permission_passes(self):
        text = swap(FIXTURE, "modeled_on_real_person: false", "modeled_on_real_person: true")
        text = swap(text, "permission_status: not_applicable", "permission_status: granted")
        self.add("npc-999-fixture.md", text)
        self.assertEqual(self.errors(), [])

    def test_real_person_pending_is_only_a_warning_for_draft(self):
        text = swap(FIXTURE, "status: active", "status: draft")
        text = swap(text, "modeled_on_real_person: false", "modeled_on_real_person: true")
        text = swap(text, "permission_status: not_applicable", "permission_status: pending")
        self.add("npc-999-fixture.md", text)
        self.assertEqual(self.errors(), [])
        self.assertTrue(any("real person" in w for w in self.warnings()))

    def test_unknown_relationship_fails(self):
        text = swap(FIXTURE, "relationships: []", 'relationships:\n  - { with: npc-123-ghost, dynamic: "x" }')
        self.add("npc-999-fixture.md", text)
        self.assertHasError("unknown NPC npc-123-ghost")

    def test_missing_fragment_fails(self):
        self.add("npc-999-fixture.md", swap(FIXTURE, "fragments: []", "fragments: [not-a-fragment]"))
        self.assertHasError("not-a-fragment")

    def test_duplicate_voice_id_fails(self):
        self.add("npc-999-fixture.md", FIXTURE)
        second = swap(FIXTURE, "npc-999-fixture", "npc-998-second")
        self.add("npc-998-second.md", second)
        self.assertHasError("voice id already used")

    def test_same_delivery_warns(self):
        self.add("npc-999-fixture.md", FIXTURE)
        second = swap(FIXTURE, "npc-999-fixture", "npc-998-second")
        second = swap(second, "TESTVOICE0001", "TESTVOICE0002")
        self.add("npc-998-second.md", second)
        self.assertEqual(self.errors(), [])
        self.assertTrue(any("sound alike" in w for w in self.warnings()))

    def test_bad_hex_colour_fails(self):
        self.add("npc-999-fixture.md", swap(FIXTURE, '"#D4AF37"', '"gold"'))
        self.assertHasError("palette")

    def test_unquoted_hex_colour_reports_yaml_error(self):
        self.add("npc-999-fixture.md", swap(FIXTURE, '["#D4AF37", "#0B1A2F"]', "[#D4AF37, #0B1A2F]"))
        self.assertHasError("invalid YAML")

    def test_file_name_must_match_id(self):
        self.add("npc-777-wrong.md", FIXTURE)
        self.assertHasError("does not match the file name")

    def test_unknown_field_fails(self):
        self.add("npc-999-fixture.md", swap(FIXTURE, "fragments: []", "fragments: []\nfavorite_color: red"))
        self.assertHasError("favorite_color")

    def test_missing_section_brief_fails(self):
        (self.repo / "sections" / "hai-radio.md").unlink()
        self.assertHasError("hai-radio.md")

    def test_build_writes_exports_and_roster(self):
        self.add("npc-999-fixture.md", FIXTURE)
        built = build_exports.build(self.repo, with_cards=True)
        self.assertEqual(built, ["npc-999-fixture"])
        exports = self.repo / "exports"

        voices = json.loads((exports / "voices.json").read_text(encoding="utf-8"))
        self.assertEqual(voices["npc-999-fixture"]["voice_id"], "TESTVOICE0001")
        self.assertNotIn("style", voices["npc-999-fixture"]["settings"])

        live = json.loads((exports / "live-config.json").read_text(encoding="utf-8"))
        entry = live["npc-999-fixture"]
        self.assertEqual(entry["autonomy"], "shadow")
        self.assertFalse(entry["platforms"]["tiktok"])
        self.assertEqual(entry["never_say"], ["no test insults"])
        self.assertEqual(entry["sections"], {"typed_out_loud": "test host", "hai_radio": "test guest"})

        prompt = (exports / "image-prompts" / "npc-999-fixture.txt").read_text(encoding="utf-8")
        self.assertIn("Palette: #D4AF37, #0B1A2F", prompt)
        self.assertIn("Never: no test hats", prompt)

        brief = (exports / "claude-briefs" / "npc-999-fixture.md").read_text(encoding="utf-8")
        self.assertIn("## Voice signature", brief)
        self.assertIn("Catchphrases: Fixture online.; Test complete.", brief)
        self.assertIn("## Live reactions", brief)
        self.assertNotIn("Change notes", brief)

        card = json.loads((exports / "cards" / "npc-999-fixture.json").read_text(encoding="utf-8"))
        self.assertEqual(card["spec"], "chara_card_v3")
        self.assertEqual(card["data"]["first_mes"], "Fixture online.")
        self.assertEqual(card["data"]["extensions"]["hai"]["id"], "npc-999-fixture")

        roster = (self.repo / "ROSTER.md").read_text(encoding="utf-8")
        self.assertIn("| npc-999-fixture | Test Fixture | test canine | active | Typed Out Loud, HAI Radio | Test Franchise |", roster)

    def test_build_is_deterministic(self):
        self.add("npc-999-fixture.md", FIXTURE)

        def snapshot():
            files = sorted(p for p in self.repo.rglob("*") if p.is_file() and "npcs" not in p.parts)
            return {str(p.relative_to(self.repo)): p.read_bytes() for p in files}

        build_exports.build(self.repo)
        first = snapshot()
        build_exports.build(self.repo)
        self.assertEqual(first, snapshot())

    def test_retired_npc_is_left_out_of_exports_but_stays_in_roster(self):
        self.add("npc-999-fixture.md", swap(FIXTURE, "status: active", "status: retired"))
        build_exports.build(self.repo)
        exports = self.repo / "exports"
        self.assertEqual(json.loads((exports / "voices.json").read_text(encoding="utf-8")), {})
        self.assertEqual(json.loads((exports / "live-config.json").read_text(encoding="utf-8")), {})
        self.assertIn("retired", (self.repo / "ROSTER.md").read_text(encoding="utf-8"))

    def test_removed_npc_leaves_no_stale_exports(self):
        self.add("npc-999-fixture.md", FIXTURE)
        build_exports.build(self.repo)
        (self.repo / "npcs" / "npc-999-fixture.md").unlink()
        build_exports.build(self.repo)
        self.assertFalse((self.repo / "exports" / "claude-briefs" / "npc-999-fixture.md").exists())
        self.assertIn("_No NPCs yet._", (self.repo / "ROSTER.md").read_text(encoding="utf-8"))

    def test_draft_npc_is_exported_for_review_but_not_live(self):
        self.add("npc-999-fixture.md", swap(FIXTURE, "status: active", "status: draft"))
        build_exports.build(self.repo)
        exports = self.repo / "exports"
        self.assertTrue((exports / "claude-briefs" / "npc-999-fixture.md").exists())
        self.assertEqual(json.loads((exports / "live-config.json").read_text(encoding="utf-8")), {})


if __name__ == "__main__":
    unittest.main()
