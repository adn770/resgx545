+++
id = "E148"
claim = "Render jobs from userspace draw every pixel exactly on 13 target sizes from 64x64 to 256x256, up to sixteen tile rows and eight tile columns, with the library's render state (bit 8 of the render context's isp_ipfmisc word set) and no BIF fault; what clearing that bit does above 64x64 and what the EDM's cleanups wait for are not shown by any run"
unit = "render"
method = "sgxfive-test tri, two renders each on a context sized for the target, on 13 sizes (probes/render/target-sizes.toml, script templates/target-sizes.sh), and the client-jobs run (probes/render/client-jobs.toml), on the laptop with the debug option on; the ISP, TA and VDM tables (E055, E056, E073) all draw 64x64 targets"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-target-sizes", "render-client-jobs"]
terms = ["CR_TE_SCREEN", "ta3d_ctl"]
+++

**What runs.** The library's render context for a target size builds the render state words, among
them the isp_ipfmisc word, which it sets to 0x000f0100 (bit 8 set). The triangle covers part of the
target, so tiles it does not touch carry background only. The targets are in tiles of 32x16 pixels
(E055). The target-sizes run draws the triangle twice, in two colours, on each of 13 sizes with a
context sized for that target: 64x64, 64x128, 64x144, 64x160, 64x192, 64x256, 128x64, 128x128,
128x144, 128x256, 256x64, 256x128 and 256x256. That is four to sixteen tile rows by two to eight
tile columns. The client-jobs run (E023) adds 128x96 and a 256x256 context used for a 64x64 target.

**Results.** All 26 renders of the target-sizes run are exact: 0 wrong pixels inside the triangle,
outside it and on its edges, `outside: 0 dwords`, `guard 0`, and the diff against the CPU
reference 0 of N pixels. Examples: 64x256 has 4296 triangle and 12088 background pixels, and
256x256 fills 65536 pixels (17208 triangle, 48328 background) with no unaccounted one. The
background counts include the tiles with no geometry, so every tile is drawn. The kernel log has
no BIF fault line over the run (one line, the campaign marker). In the client-jobs run 128x96 is
exact too (3252 triangle, 9036 background) and the 256x256 context draws a 64x64 target with the
same hashes as one sized for 64x64 (0x99385a04ee01c585 and 0xab267bd98022a81d). The tables that
poke render state (E055, E056, E073) all run 64x64 targets.

**Not shown.** No run clears bit 8 of the render context's isp_ipfmisc word, so whether tiles that
no geometry touches are skipped without it above 64x64 is not seen (Q029). No run reads the EDM's
cleanup of the render target data set or of the render context, or what each waits for (Q029). That
the EDM writes the TA/3D control block through the render context's page directory, and what a
read-only mapping of that page faults, is not run either (Q076). The sizes are those listed, one run
each.
