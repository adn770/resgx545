+++
id = "E430"
claim = "After a douti with no wait, none of pa0 to pa15 holds the waited iteration's pa0 at its pixel beyond chance (0 to 25 of 1062 pixels per register, three runs), pa4, pa8 and pa12 hold the target's pre-fill 0xdeadbeef on 258 to 288 pixels in all 9 runs, and the other registers hold 0, 2, 6, 0x40000000, 0x3f800000 and other floats that differ between runs on 7 to 54 percent of the pixels, depending on the register and the pair of runs"
unit = "pds"
method = "probes/pds/no-wait-where.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the triangle with the pixel PDS program of E393 (pds_iter_nowait.s: one douti, source 1, no completion bit, no wait) and a shader copying each of pa0 to pa15 to o0 in turn (48 jobs, three runs), against the waited iteration (pds_iter_wait.s) read at pa0 to pa3 (12 jobs); every pixel read; compared pixel by pixel (tools/usse-asm/pixels.py)"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["pds-no-wait-where"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTU1.WAIT_FETCH"]
+++

**Results.** The waited pa0 takes 47 distinct values over the triangle's 1062 pixels. In the no-
wait jobs the pixels whose pa_k equals the waited pa0 at the same pixel number, per run, for k = 0
to 15: pa0 18, 25 and 17; pa4 7, 6, 7; pa5 6, 11, 7; pa8 19, 18, 19; pa9 7, 7, 10; pa12 13, 12,
10; pa13 8, 3, 9; the other nine registers 0 in every run. The no-wait pa0 has 45 distinct values;
it equals the next run's at 747 and 877 of 1062 pixels (the first and third runs: 773), the other
registers' adjacent runs at 494 to 986 pixels and any two of the three runs at 489 to 986: values
that change between runs on 76 to 573 pixels of the 1062, up to 54 percent. The commonest values
are 0 and 0x40000000 (2.0) in every register but pa0 (0x2 on 113 to 134 pixels, then 0x41ac0000
and 0x419c0000) and pa1 (0x4226xxxx values), 0x3f800000 in the registers of 3, 7 and 11, and
0xdeadbeef (the render target's pre-fill) in pa4, pa8 and pa12 on 258, 265 and
271; 258, 277 and 267; 258, 288 and 275 pixels. With the wait, pa1 to pa3 read as in the no-wait
jobs (pa1 the same 0x4226xxxx values on 57 to 58 pixels).

**What it shows.** The iterated value is in no register of the pixel's first sixteen when the
shader reads without waiting, the matches being the coincidences of a 47-valued field [infer];
what the registers hold are leftovers, some of the target's own pre-fill. Whether the value
arrives after the shader has read, or goes to another task's registers, is not shown. Q027 stays
open.
