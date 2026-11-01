+++
id = "E629"
claim = "The depth a job that overflows stores has its sign bit set (every non-zero dword of the window: 49408 of 49408 at 1024x768 with G = 1, 571392 of 571392 with G = 33) in exactly the jobs whose first abort's threshold was raised (TA3DCtl dwords 37 and 38 read 1 << 16 | P - 0x22 and 0x20, E625) and in none of the others: 44 of 44 overflowing depth jobs (the z = 0.5 triangle at G = 1 in 0x23, 0x24, 0x26, 0x28, 0x2a, 0x2c pages signed and in 0x2d, 0x2e, 0x2f, 0x30 and 0x34 pages positive, 2 runs each; at G = 33 signed in 0x23 and 0x28 and positive in 0x30; the full-screen ramp signed in 0x23, 0x28 and 0x30 at G = 33 and in 0x28 and 0x30 at G = 1; the 6 jobs of 4096x4096 in 0x2000 pages positive, 246016, 148096 and 12584064 non-zero dwords, none raised), the pitch does not decide it (G = 1 and G = 33 agree in 5 of 5 cells), the number of partial renders does not (1 in the signed z = 0.5 cells and in the positive 0x30 one, 2 in the signed ramp cells in 0x23 and 0x28, 1 at 0x30), and the scene does only through its page need (the z = 0.5 triangle is raised below 0x2d pages, the ramp at 0x30 as well); within the z = 0.5 scene a raise is the same as P below 0x2d, so the sign follows a scene-dependent P boundary that the raise follows too, and the one pair that tells them apart is the 0x30 z = 0.5 job (positive, not raised) against the ramp (signed, raised); the sign of a job is repeatable (2 of 2 runs identical in all 22 cells: the table's 19 and 3 of 4096x4096)"
unit = "zls"
method = "tri --depth --depth-ctl 0x0017110c (G = 33) or 0x0017100c (G = 1) with --depth-dump on the z = 0.5 triangle (--poke blk:1) or the full-screen ramp (--tri-full --tri-z), a fill marker per job, regtimeline over the TA's registers so that the partial renders are counted with the sign, on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool sgxfive-test-1135 (sha256 7732b945...): the 38 dp jobs of table depth (19 cells, each twice after a reset), the 6 w4096 jobs and the follow-up a jobs; the sign counted over the stored dwords by the dataset's analysis/an_p1139.py and an_raise.py"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["dpm-partial-model-batch"]
terms = ["CR_ISP_ZLSCTL", "Dynamic Parameter Management (DPM)"]
+++

**What ran.** The `dp-*` jobs of table `depth` (38 jobs, 19 cells, each twice after a reset) and
the `w4096-*` and follow-up a jobs: `tri --depth --depth-ctl 0x0017110c` (G = 33) or 0x0017100c (G
= 1), the z = 0.5 triangle (`--poke blk:1`) or the full-screen ramp (`--tri-full --tri-z`), fill
marker per job, `--depth-dump`, regtimeline over the TA's registers so that the partial renders
are counted with the sign (`analysis/an_p1139.py`, `analysis/an_raise.py`; same laptop, kernel,
module, tool as E625). The table that settles Q107: (case, partial renders, zero dwords, window,
signed / non-zero) is `analysis/recompute-b.out` after "## depth cases".

**Results [HW].** H-sign-P (declared: the z = 0.5 scene is signed iff P < 0x2c; the ramp whenever
it overflows) scored fit 3 of 3, held out 8 of 9, control 11 of 12: the one miss is 0x2c, signed
in both runs (the boundary lies between 0x2c and 0x2d: 0x2d, 0x2e and 0x2f were run after the
batch, 2 runs each, positive); the ramp's whole-buffer 0x60 and 0x100 jobs (explore) complete and
are positive. H-sign-N (signed iff at least two partial renders): refuted, the signed z = 0.5
cells have 1 partial render each. H-sign-G (the pitch): refuted, 5 of 5 cells identical at G = 1
and 33. H-sign-S (the scene): the ramp at 0x30 is signed and the z = 0.5 triangle is not, E468's
job against E461's: the disagreement of Q107 and Q038 is the scene's page need, not a variable of
the store. What tracks the sign in all 44 overflowing jobs, as an observation, is the raise of
E625: dwords 37 and 38 non-zero in the 26 signed jobs and 0 and 0 in the 18 positive ones (44 of
44, `analysis/an_raise.py`; the raise rule 2 * thr0 < U + 2 of E625 predicts them for the default
triangle). The `dl-*` jobs of E628 do not test it: their store is the index buffer, in which the
scene's depth is invisible, so no sign of the scene's depth is read there (E467: a load clears the
sign).

**Reading [infer].** The sign is set on the depth of the macrotiles a partial render stored and
the TA then went on tiling at the raised threshold: the final render takes the stored depth as it
left (negated, E466's float-negation reading) and leaves the macrotiles it drew itself, so a job
whose one partial render comes at the end of the geometry (no raise) keeps positive values.
Whether the negation is what the partial render stores or what the load does with a stored value
is not seen.

**Not shown.** The sign at other scenes and sizes (the 4096x4096 jobs in 0x2000 pages are not
raised); the sign of a job with more than one raise (never seen); the tile order of the store.
