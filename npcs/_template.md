---
# Copy this file to npcs/npc-NNN-slug.md (next free number, lowercase slug).
# The id below must match the file name, never changes, and is never reused.
id: npc-000-slug
name: "Display Name"
aliases: []
status: draft                  # draft | active | retired
canon_version: 0.1.0           # bump with a CHANGELOG entry that says why
franchise: []                  # e.g. ["HAI Frequency"]
species: ""

# If this NPC's face, body or voice is modeled on a real person, say so and
# record permission. An active NPC modeled on a real person must be "granted".
real_person:
  modeled_on_real_person: false
  permission_status: not_applicable   # not_applicable | pending | granted
  notes: ""

# Where this NPC appears. Leave a section's role empty if they do not appear there.
sections:
  typed_out_loud:        { role: "", frequency: "" }
  beats_bars_breakdowns: { role: "", frequency: "" }
  hai_radio:             { role: "", venue: "", frequency: "" }
  silent_but_deadly:     { role: "", frequency: "" }

# Voice signature: the voice, how it is delivered, and the verbal habits.
voice:
  elevenlabs_voice_id: ""
  elevenlabs_model: ""
  settings: { stability: null, similarity: null, style: null, speed: null }
  delivery: { pace: "", pitch: "", accent: "", energy: "" }
  verbal_habits: []            # sentence rhythm, fillers, how they open and close
  catchphrases: []
  audio_tags_allowed: []       # e.g. ["[laughs]", "[whispers]"]
  sample_line: ""

# Visual canon. Quote hex codes: ["#D4AF37"] (an unquoted # starts a YAML comment).
look:
  silhouette: ""
  palette: []
  wardrobe_default: ""
  signature_props: []
  never: []                    # visual canon violations
  reference_images: []         # repo paths under assets/<id>/ or links

animation:
  hedra_avatar: ""
  character_animator_puppet: ""

relationships: []              # - { with: npc-001-name, dynamic: "..." }

content_rules:
  do: []
  dont: []
  rating: ""

# How this NPC reacts to live chat and comments. New NPCs always start in shadow
# mode: they draft replies, a human approves. See CANON-RULES.md.
live:
  autonomy: shadow             # shadow | approve | auto
  triggers: []                 # words, topics or moments that make this NPC jump in
  avoid_topics: []
  reply_style: { max_words: 30, emoji: false, signature_opener: "" }
  platforms: { youtube: true, twitch: true, instagram: true, tiktok: false }
  max_replies_per_hour: 20

fragments: []                  # names of files in fragments/, without .md
---

# Display Name

## One-line pitch

## Backstory (canon)

## Personality & motivations

## How they talk

<!-- 3 to 5 sample lines in their voice. -->

## Per-section behaviour

### Typed Out Loud

### Beats Bars & Breakdowns

### HAI Radio

### Silent But Deadly

## Live reactions

<!-- What they notice in chat and comments, how they handle praise, questions, trolls and spam, and what they never respond to. -->

## Social captions voice

## Image-prompt notes

## Open questions

## Change notes

- 0.1.0 (YYYY-MM-DD): Created. Why:
