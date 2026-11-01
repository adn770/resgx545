+++
id = "Q014"
question = "why does render command word 23 bit 27 (cmd:23^=0x8000000) fault with the same 3936 pixels differing in both runs, while bit 28 gives 4000 and then 3968?"
unit = "render"
phase = 6
evidence = ["E029"]
terms = []
+++

The sweep `render-command-words` flips every bit of every dword of the 64x64 triangle's render
command and sets each to 0 and 0xffffffff (E029 reads word 11 of it), and ran twice (the second
is the follow-up run). Word 23 has no record. In it:

- bits 0, 1, 4 to 20, 22 and 23 fault the job with all 4096 pixels at the sentinel (hash
  0xe4364b426cdce325); bits 3 and 21 hang the job (3072 pixels differ); bit 2 and bits 24 to
  26 are not among the failing cases.
- bit 27 (`cmd:23^=0x8000000`) faults the job with 3936 of 4096 pixels differing from the
  baseline, first pixel (32, 0) at the sentinel 0xdeadbeef, hash 0x594a1b99e627f7a5. Both
  runs agree exactly.
- bit 28 faults with 4000 differing in the first run (hash 0xdcf6c0e2040198a5) and 3968 in the
  follow-up run (hash 0x39efaba83319a125), bit 29 hangs with 1536 differing, bits 30 and 31
  fault with 3584 (hash 0x927a9f8b8aa231a5, both runs).

So for bits 27 to 31 part of the target agrees with the baseline when the job fails: 160 pixels
for bit 27, 96 or 128 for bit 28. Those pixels are not the sentinel; the data does not say which
pixels they are, only the count.

Open: what word 23 is (the bits above 26 behave unlike the low ones); which pixels survive and
why their number is the same in both runs for bit 27 and not for bit 28.

To settle it: run `cmd:23^=0x8000000` ten times in fresh boots and after other jobs, with every
pixel of the target printed, to locate the surviving pixels (whole rows, tiles or scattered)
and see whether their number takes one value or several; do the same for bits 28, 30 and 31.
