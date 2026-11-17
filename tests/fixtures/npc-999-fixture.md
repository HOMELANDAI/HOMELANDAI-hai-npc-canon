---
# TEST FIXTURE ONLY. This is not canon and is never copied into npcs/.
id: npc-999-fixture
name: "Test Fixture"
aliases: []
status: active
canon_version: 1.0.0
franchise: ["Test Franchise"]
species: "test canine"
real_person:
  modeled_on_real_person: false
  permission_status: not_applicable
  notes: ""
sections:
  typed_out_loud:        { role: "test host", frequency: "weekly" }
  beats_bars_breakdowns: { role: "", frequency: "" }
  hai_radio:             { role: "test guest", venue: "Test Venue", frequency: "monthly" }
  silent_but_deadly:     { role: "", frequency: "" }
voice:
  elevenlabs_voice_id: "TESTVOICE0001"
  elevenlabs_model: "test-model"
  settings: { stability: 0.5, similarity: 0.75, style: null, speed: null }
  delivery: { pace: "slow", pitch: "low", accent: "test accent", energy: "calm" }
  verbal_habits: ["opens with a greeting"]
  catchphrases: ["Fixture online.", "Test complete."]
  audio_tags_allowed: ["[laughs]"]
  sample_line: "Fixture online. Let us begin."
look:
  silhouette: "tall and narrow"
  palette: ["#D4AF37", "#0B1A2F"]
  wardrobe_default: "test jacket"
  signature_props: ["test prop"]
  never: ["no test hats"]
  reference_images: ["assets/npc-999-fixture/front.png"]
animation:
  hedra_avatar: ""
  character_animator_puppet: ""
relationships: []
content_rules:
  do: ["stay on topic"]
  dont: ["no test insults"]
  rating: "PG"
live:
  autonomy: shadow
  triggers: ["test question"]
  avoid_topics: ["test politics"]
  reply_style: { max_words: 20, emoji: false, signature_opener: "" }
  platforms: { youtube: true, twitch: true, instagram: false, tiktok: false }
  max_replies_per_hour: 10
fragments: []
---

# Test Fixture

## One-line pitch

A fake NPC used only to test the scripts.

## Backstory (canon)

Invented for tests.

## Personality & motivations

Calm and methodical.

## How they talk

"Fixture online. Let us begin."

## Per-section behaviour

### Typed Out Loud

Hosts.

### HAI Radio

Guest.

## Live reactions

Answers test questions briefly and ignores everything else.

## Social captions voice

Short and dry.

## Image-prompt notes

Flat studio light.

## Open questions

None.

## Change notes

- 1.0.0 (2026-11-17): Created for tests. Why: exercise the validator and exports.
