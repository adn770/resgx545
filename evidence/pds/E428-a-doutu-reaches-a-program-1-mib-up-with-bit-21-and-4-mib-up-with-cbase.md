+++
id = "E428"
claim = "A DOUTU word with only bit 21 set (the offset's bits 20:19 in word bits 21:20, CBASE 0) starts a USE program placed 1 MiB above the code heap's base, and one with CBASE 8 starts a program placed 4 MiB above it, in 3 of 3 runs each, while the bit-21 form at 4 MiB (all zero) starts the program at the base: the 18 program-counter bits reach bit 21 of the word and CBASE adds the offset's bits 22:19"
unit = "pds"
method = "probes/pds/doutu-place.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: sgxfive-test probe --place OFFSET=FILE --place-form cbase|exe18: a USE program writing the colour 0x61 mapped at the USSE pixel heap's base (0x37000000) + 0x10000, 0x100000 or 0x400000 and started in place of the fill shader (colour 0xBA5E, at the base) by a primary DOUTU with the offset in EXE and CBASE (cbase) or in an 18-bit EXE (exe18); six probes of three runs, 18 jobs, the colour of every pixel read"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["pds-doutu-place"]
terms = ["PORT.DOUTU", "DOUTU0.TEMPS"]
+++

**Results.** The fill's colour is uniform in every job (2048 of 2048 pixels):

- 0x10000 (64 KiB) and 0x100000 (1 MiB), either form: 0x61, the placed program ran (12 of 12
  jobs). Bits 21:0 of the word were 0x000002 (cbase) and 0x200000 (exe18, bit 21 only) at 1 MiB.
- 0x400000 (4 MiB): cbase (bits 21:0 = 0x000008) 0x61 (3 of 3); exe18 (bits 21:0 = 0, as the
  18-bit EXE's bits 20:3 of 4 MiB are zero) 0xBA5E, the program at the heap's base (3 of 3).

**What it shows.** The word's bits 21:20 are address bits: the word 0x200000 alone starts the
program at 1 MiB, where a 16-bit EXE (bits 19:4) would give the base. CBASE (bits 3:0) takes the
offset past the 18-bit reach: 8 starts the program at 4 MiB. So EXE is 18 bits wide, reaching 2
MiB, and CBASE adds multiples of 512 KiB (its bits 22:19) [infer for the sum when both are
non-zero: not run]. The heap is 5 MiB (DEV_QUERY), so 4 MiB is in it: the question
of the word's width is answered.
