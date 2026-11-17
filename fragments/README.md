# Fragments

A fragment is a shared trait pack several NPCs can reuse, such as a code of conduct, a way of speaking or a set of house rules. Write it once, list its name in each NPC's `fragments` field, and it is appended to that NPC's Claude brief.

To add one, create `fragments/<name>.md`. A short header is optional:

```
---
name: example-fragment
description: One line on what this pack covers.
---

- Trait or rule one.
- Trait or rule two.
```

`validate.py` fails if an NPC lists a fragment that does not exist. No fragments exist yet.
