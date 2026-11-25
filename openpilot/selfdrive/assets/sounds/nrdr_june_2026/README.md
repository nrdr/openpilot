# June 2026 engagement sounds

Exact, unmodified recordings from `nrdr/openpilot` commit
`d6798c75a5` (June 29, 2026), under `selfdrive/assets/sounds/`.
The original `engage_tizi.wav` and `disengage_tizi.wav` are used on
comma 3X; comma 3 and comma four use the generic files, as that revision did.

Only engage, disengage, and engagement-refused sounds use this pack.
Their original automatic volume curve lives in
`openpilot/nrdr/ui/engagement_sounds.py`. Other alerts retain the current
recordings, gain behavior, and priorities. Quiet Mode still applies.

`openpilot/nrdr/tests/test_engagement_sound_pack.py` pins the original
SHA-256 hashes and verifies playback and volume behavior.
