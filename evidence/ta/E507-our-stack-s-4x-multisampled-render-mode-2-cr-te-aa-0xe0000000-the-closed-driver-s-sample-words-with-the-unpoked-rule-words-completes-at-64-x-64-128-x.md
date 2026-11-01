+++
id = "E507"
claim = "Our stack's 4x multisampled render (mode 2, CR_TE_AA 0xe0000000, the closed driver's sample words) with the unpoked rule words completes at 64 x 64, 128 x 64, 128 x 128, 256 x 128, 96 x 48 and 192 x 96 and faults the job (BIF fault at pages 0x20006, 0x20008 and 0x2000a) at 320 x 160, 384 x 192, 448 x 224, 512 x 256, 512 x 384 and 640 x 480, 6 of 6 held-out sizes; the poked family U2 (words 0x802002, 0x802002, stride 4) draws the same image as the rule at 64 x 64"
unit = "ta"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e), probes/ta/mtile-msaa.toml (script mtile-msaa.sh, the safe half of Q086's batch): tri --tri-full, mode 2, CR_TE_AA 0xe0000000, family R (unpoked) at 13 sizes and U2 at 64 x 64; the script stopped after the 640 x 480 job (three failed recoveries of the health triangle), so the 1024 x 768 job and all the other families were not run"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["ta-mtile-msaa"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE", "CR_TE_AA"]
+++

**What ran.** 13 of the declared 14 jobs, one run each (the declared fit sizes are 64 x 64, 128 x
64, 128 x 128, 256 x 128, 96 x 48 and 192 x 96, the declared held-out sizes 320 x 160 to 1024 x
768): R at 64 x 64, 128 x 64, 128 x 128, 256 x 128, 96 x 48, 192 x 96 (the fit, six sizes) and U2
at 64 x 64 (fit), then R at the held-out 320 x 160, 384 x 192, 448 x 224, 512 x 256, 512 x 384 and
640 x 480. Not run: R at 1024 x 768 (the batch stopped) and the families U2, U2Q, HS, FX at any
other size (declared as listed or in the risky script).

**Results.** The seven fit jobs draw exactly (all pixels green, the tile signature "gg..." the
same). H86i cannot fail in this form, because every job that completes is all green, so the
signature of a completing job cannot differ: it "holds" 7 of 7 with six comparisons of R with itself
and one of U2 with R at 64 x 64, and none of them could have failed. The six held-out jobs fault, 6
of 6 even with the rule's own words: "job faulted, context lost", the tool's diff line reads every
pixel of the target as differing, and the printed rows count 51187, 73554, 100338, 130845, 196276
and 307162 pixels at the sentinel and 8 others each, a few short of the target because the last
printed row of a dump has a tool message inserted into it (as in E511). The kernel log names a BIF
fault with `BIF_FAULT` 0x90004 at 0x2000606b (320 x 160), 0x20006061 (384 x 192), 0x20006062 (448 x
224 and 512 x 256) and 0x20008061 and 0x2000a061 (512 x 384 and 640 x 480). The script's health
triangle (a plain 64 x 64 triangle after a reset; the script prints a line only when it fails, and
its counter is reset by a pass) failed after 320 x 160, did not print after 384 x 192 and 448 x 224,
and failed after 512 x 256, 512 x 384 and 640 x 480: three in a row (the counter read 1, 2, 3),
which stopped the script. The kernel log has five `SGX recovery failed: -110` lines in the run
(16:53:11 to 16:53:40) and 15 BIF faults, 6 of them in the case jobs (8805, 8808, 8811, 8813, 8816,
8819) and the others in the health triangles' own jobs (8806 and 8807 after 320 x 160, for one);
kept in kernel.log, not read further.

**What it shows.** [HW] The unpoked 4x render of our stack works up to at least 256 x 128 and 192 x
96 and fails from 320 x 160: the failure is the stack's, before any macrotile word is poked, so the
held-out test of H86i could not run at those sizes. [infer] The kernel's render layout for a 4x
target (region headers, the pages the render context allocates) is too small past some size between
192 x 96 and 320 x 160 (Q140). The one non-trivial agreement: U2 at 64 x 64 draws the same 4096
pixels as R, and the closed driver's own 64 x 64 words are therefore accepted by our stack there.

**What it does not show.** H86i at any held-out size, the U2, U2Q, HS and FX families at 96 x 48 to
192 x 96, and the rule of the closed driver (the capture batch of sizes/ms4-sizes3d.txt was not
run).
