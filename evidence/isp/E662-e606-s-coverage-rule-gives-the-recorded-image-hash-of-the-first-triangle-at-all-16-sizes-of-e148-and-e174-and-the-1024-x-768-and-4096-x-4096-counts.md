+++
id = "E662"
claim = "The coverage rule of E606 (vertices on the 1/256 pixel grid, the pixel centre tested exactly, left and top edges owning ties) applied to the library's first triangle ((8, 8), (56, 20), (20, 56) of a 64 x 64 target, scaled in 1/16 pixel) gives the recorded image hash of every render of the 16 sizes of E148, E023 and E174: 32 of 32 hashes of 14 sizes (both colour pairs, 64 x 64 to 256 x 256, 128 x 96), the first render of 1024 x 768 (207456 triangle and 578976 background pixels, hash 0xc9e301d225fe2325) and of 4096 x 4096 (4422528 and 12354688, hash 0x08197f1b8b083325), 3 of the 16 sizes are sizes E606 ran (64 x 64, 128 x 128, 256 x 128) and 13 are not (64 x 128, 128 x 64 and 256 x 64 of the same family among them, the half-sizes 72, 80, 96 and 48, the heights above 128, 1024 x 768 and 4096 x 4096); those renders were checked before only against a CPU reference with a one-pixel undecided band around every edge, the hash is an exact image"
unit = "isp"
method = "offline, no new run: the image of the default triangle computed by the integer rule of E606 (Python with numpy, scratch, and the Rust test the_rule_alone_reproduces_the_first_triangles_hash_at_all_16_sizes_whether_or_not_e606_ran_them of sgx-pipe's tests/isp_arith.rs, whose constants are the hashes printed by the runs), compared with the 'target: WxH hash' lines of the target-sizes and client-jobs outputs and the parameter-buffer sweeps' raw output (the hash is FNV-1a 64 over the little-endian dwords of the target, the tool's own); no other triangle, no other size, no run on the laptop"
tiers = ["HW"]
date = "2026-11-09"
data = ["render-target-sizes", "render-client-jobs", "dpm-parameter-buffer"]
terms = []
+++

**Results.** [HW] The model is applied to the single triangle every one of these runs drew, at the
size of the run: green (0xff00ff00) inside, 0xff203040 outside; the second render of each run, with
the colours red and dark blue, shares the coverage. All 32 recorded hashes of the 13 sizes of E148
and E023's 128 x 96 equal the model's (the 64 x 64 image has E023's 1062 and 3034 pixels), and so do
the first renders of E174's two large sizes (of the renders that did not overflow the parameter
buffer, the second and later renders of the 1024 x 768 sweep repeat the first's hash: 14 of the 20
later renders; the other 6 are E174's overflowed cases). The 4096 x 4096 render's counts are E174's
4422528 and 12354688.

**What it shows.** [HW] For this triangle the rule that E606 measured on random sub-pixel triangles
at 64 x 64, 128 x 128 and 256 x 128 holds on every size of the render-target-size runs, including
sizes E606 did not run (a half-size that is not a power of two, a height of 256, a target of 4
macrotiles across and down). It is a result about one triangle with vertices on the 1/16 pixel grid
scaled in the library's way: whether random sub-pixel triangles keep the rule on those targets is
not shown, and the pipeline simulator keeps refusing every size E606 did not run (Q240: 13 of the
16, those of the same power-of-two family among them) until a sweep says so.

**What it does not show.** A second triangle, vertices off the grid of 1/16 pixel, a target of other
proportions, the depth, the iteration, the visible behaviour of the TA at those sizes (the 1024 x
768 and 4096 x 4096 jobs go through four macrotiles a row: Q139, Q100, Q086).
