# Changelog

Format follows Keep a Changelog. Every entry says why, because Claude's GitHub sync never sees commit messages.

Canon versions: MAJOR is a retcon that breaks earlier episodes or posts (species, backstory, who someone is). MINOR is a new NPC or a new section role. PATCH is wording, typos and prompt tweaks.

## [Unreleased]

## [0.1.0] - 2026-11-17

### Added
- Repo scaffold: NPC template, JSON schema, four section briefs, validation and export scripts, tests and two GitHub Actions workflows.
  Why: NPCs run across all four HAI brands and had no written definition, so voices, visuals and live replies had nothing shared to stay consistent with.
- Voice signature block (voice, delivery, verbal habits, audio tags) and a `live` block (autonomy, triggers, platforms, rate limit) on every NPC.
  Why: NPCs must sound distinct and must react to chat and comments within limits the owner controls.
