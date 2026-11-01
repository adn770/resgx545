+++
id = "E569"
claim = "The 28 triangle jobs of the Q021 probes (a vertex shader writing a set of four outputs o4, o5 = x, y, o6 = 0.25, o7 = x + y, two temporaries more than E420's; the pixel shader storing pa2, pa3, pa4 or pa5; five runs of 0x40c00801 and two controls of 0x40800801 per register, 7 jobs each) all failed with 'job hung, context lost (Connection timed out)' (28 of 28; the kernel log names 28 hung jobs and 'recovering'), no pixel was read, and the health triangle drew exactly after each of the 28 (a reset between, the 28 jobs took about 8 s each); the question whether pa3 is a fourth component or 1.0 (Q021) has no result from this batch, and the two controls of 0x40800801 hung too, so the hang is not tied to the fourth component's source word"
unit = "texture"
method = "probes/texture/tx-*.toml of phase 11.32 (probes/texture/templates/tx_map.s: one program, 2048 pixels a fill, pa0 = (y << 16) | x, each pixel one smp, the scratch buffer the texture, dword i = 0xD0000000 | i) run by probes/texture/templates/run-all-1132.sh on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed and loaded alike), tool sgxfive-test-1126 sha256 751f7223...f82e, stock firmware; tools/texture/p1132/declared.tsv sha256 9395f6dd...7b2a and predictions-declared.tsv sha256 4ee35db3...84beb hashed before the first run (the runs began at 02:36:08, the hashes were written at 00:38) and unchanged; no register written, only debugfs reset and /dev/kmsg; raw dumps gzipped under resgx545-data/texture/p1132/<script>/ with the case tables, the stdout of each script in texture/p1132/stdout/ and the kernel logs; recomputed by tools/texture/p1132/recompute/recompute_p1132.py (declared predictions the model no longer renders: 0). Group douti4 (28 triangle jobs, probe --tri with --vtx-coords)"
tiers = ["HW"]
date = "2026-11-09"
data = ["texture-p1132-tx-douti4"]
terms = ["DOUTI0.COMPONENTS"]
+++

**Results.** [HW] 28 of 28 hung; the recompute lists each as failed. The two controls per register
use the same new vertex program with the old source word, so they isolate the source word only: the
hang is not the source word. No job ran E420's unchanged probe in the same session and none isolates
the vertex program, its two extra temporaries or the output set from one another, so which of them
hangs the job is not known. E541 (the TA's object tables of 11.31) saw jobs hang or fault where a
set was described past the outputs its vertex program writes (3 of 7 jobs of one pattern) without
deciding that this is the cause; here the set has four outputs and the program writes o4 to o7, so
it is a candidate that is not tested.

**Predictions.** None declared (the jobs are tables); the outcome 'pa3 = 1.0 or x + y' was not
reachable.

**Not shown.** Whether E420's probes still run on this module (not re-run in this batch).
