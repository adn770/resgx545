+++
id = "E451"
claim = "After a first-context render that keeps the DPM owner with render flag bit 2 (TA3DCtl dword 20 = its RT data set + 0x18, dword 25 clear), a second context's render with the bits clear leaves dword 20 as it was in 2 of 2 runs; with bit 3 or bits 3 and 2 kept the words read 0 after the pair in 2 of 2 runs each; the second context's own kept words take dword 20 and 25 when only it keeps (2 of 2) and replace the first's when both keep with 0xc (2 of 2), or dword 21 when both keep with 0x4 (2 of 2); all 56 renders exact"
unit = "render"
method = "probes/render/kept-owner-two-contexts.toml (kept-owner-two-contexts.sh) on the laptop (direct cable), linux fork 01cff214d7d2 with the debug option on, module srcversion FC6EB50DEF21E3A6249727F (the loaded module, read from /sys/module, equal to the installed file's modinfo; both printed by the run), sgxfive-test tri -n 2 --ctx2 --words DIR (the second context in the same VM renders after each render of the first; debugfs buf09 saved after each pair of renders), the render flags (TA command dword 7, kernel value 0x400) flipped through the kernel poke ta:7^=V before render 1 of the first context (--kpoke-render), of the second (--kpoke-render2) or both: no flip, V = 0x4, 0x8, 0xc in the first, 0xc in the second, 0xc in both, 0x4 in both; two runs of each (14 runs), the GPU reset before each"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["render-kept-owner-two-contexts"]
terms = ["FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE"]
+++

**What runs.** E316 read, on one context, that render flag bit 2 keeps TA3DCtl dword 20 (the first
DPM slot's RT data) after the render and leaves dword 25 clear, and that bit 3 or both keep both.
The slot step of the TA kick (3d.md section 4.4) stores a kept owner when another RT data takes
the slot. Here the second context's RT data lies at another address (0x32423300 against
0x32411300), so its render is a later job on a context at another address.

**Results** (TA3DCtl dwords 20, 21, 25 after render pair 1, the first context flagged in render 1
and the second's render 1 following; the same in both runs of each case; after pair 2 all were 0):

| flags flipped in render 1 of | dword 20 | dword 21 | dword 25 |
|---|---|---|---|
| none | 0 | 0 | 0 |
| first, 0x4 | 0x32411318 (the first's RT data + 0x18) | 0 | 0 |
| first, 0x8 | 0 | 0 | 0 |
| first, 0xc | 0 | 0 | 0 |
| second, 0xc | 0x32423318 (the second's) | 0 | 0x32423318 |
| both, 0xc | 0x32423318 (the second's) | 0 | 0x32423318 |
| both, 0x4 | 0x32411318 (the first's) | 0x32423318 (the second's) | 0 |

All 56 renders (14 runs, 28 on each context) were exact (0 wrong inside, outside and at the
edges, guard 0) and all 56 jobs completed; the health fill and triangle ran exact before and
after. The kept words were read after the pair, so a word the first render kept and the second
cleared is seen as 0.

**What it shows.**

- A later job on a context at another address, with the bits clear, leaves the dword 20 that bit 2
  alone kept as it is, read after the pair (2 of 2) [HW]. After bit 3 (NO_DEALLOCATE), alone or
  with bit 2, the words read 0 after the pair (2 of 2 each) [HW]; that the first render set them
  (E316, one context) and the second cleared them is [infer], as nothing was read between the
  two renders.
- A job that keeps an owner itself when the first context's owner is already in dword 20: with bit
  2 alone in both, the second's goes to dword 21 and the first's stays in 20; with 0xc in both the
  second's replaces the first's in 20 and 25 [HW]. So the second slot word holds a second kept owner
  when bit 2 alone keeps both.
- No fault, hang or wrong pixel followed a kept owner of a context that is alive (56 of 56 renders)
  [HW]; that the stored DPM state of a kept owner was used is not shown.

**What it does not show.** A kept owner of a context that is gone (the contexts here were alive
when the words were read); a third context; the DPM registers beside the words (E458, Q106).

**Provenance.** The sgxfive-test binary of these runs is the one whose sha256 each env.toml names
(7de509d3...); it was built from source not yet committed, which was later committed in f63c7d19.
