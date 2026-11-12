+++
id = "E898"
claim = "Round 7 offline, a program and tool record, no hardware run (Q291): the position-store pixel program pix_posstore.s (17 instructions, landed as probes/pds/templates/pix_posstore.s), assembled with our usse-asm (sha256 8a136e52...), passes sgx-sim as a triangle's pixel instance at 2048 of 2048 pixels of a 64 x 32 area with pa0 = x + 0.5 and pa1 = y + 0.5: each stores pa0, pa0, pa1 and 0x7E570000 | g25 at scratch 16 x (g24 << 5 | g23) and leaves o0 = pa0; it reads only g23, g24 and g25, the globals sgx-sim models in a triangle's pixel task (it refuses g18 there), so one job's rows must touch one tile"
unit = "usse"
method = "Offline, no run (round 7, decision R7-1 a; plan closing7/a/exp-pixel-r7.md section 1.2, decision 10 a for the landing). The plan's draft closing7/a/q291/pix_posstore.s was assembled with the landed tools/usse-asm/usse-asm (listing pix_posstore.lst, binary pix_posstore.bin, hashes SHA256.txt) and run by the plan's scratch harness closing7/a/q291/simcheck (after closing6/r6-pixel's debug-src/simcheck; sgx-sim and usse-isa of resgx545 main 418467e): Machine with tri_pixel set, temps 4, one instance per pixel of a 64 x 32 area, pa0 and pa1 the floats x + 0.5 and y + 0.5 (E437's position pair), the scratch bus at 0x5CAF0000 (the immediates the tool patches); output simcheck.out. In the fold (2026-11-12) the harness was rebuilt from its published copy (resgx545-data cited/closing7/a/q291/) and re-run on the published binary: output byte-identical, exit 0; usse-asm assembles the published source and the landed template (whose header comment alone differs) to the same sha256 8a136e52d7966dc41b5f20da97f16347e5484bc8b6e1e37618def59cea2fdf9f, and SHA256.txt verifies. The landed checks, written first: crates/sgx-tools/tests/posstore_sim.rs (the template assembled by sgx-tools, the same 2048-pixel check) and tools/usse-asm/test_posstore.py (usse-asm's binary equals the plan's sha256; only g23 to g25 read)"
tiers = ["infer"]
date = "2026-11-12"
data = ["cited-scratch:closing7/a/q291/", "probes/pds/templates/pix_posstore.s"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++
**What was done.** Q291 asks whether the 1.25 band of the ZLS store applies to the iterated
attributes, which lie past the target where the colour store writes nothing; round 6 dropped its
rows because no landed program stored an instance's attribute at a scratch address formed from its
position. The round 7 plan wrote one (`closing7/a/q291/pix_posstore.s`), assembled it with our
assembler and ran it in our simulator; the fold lands it as a probe template with two tests and
re-ran the plan's harness from the published copy (byte-identical).

**The program.** `slot = g24 << 5 | g23` (in a triangle's pixel task g23 = x mod 32, g24 = y mod
16, g25 the lane in the 2 x 2 quad: E808), masked to 9 bits; the register offset 0x00100000 | slot
makes each `stad [r0,+r1]` store at 16 x slot bytes (the high x low rule of `eot_tile.s`). Dword 0
gets pa0 from every instance that runs (no `.skipinv`, E111), dwords 1 to 3 pa0, pa1 and
0x7E570000 | g25 from the valid instances; `o0 = pa0` at the end.

**Results (simulator, not hardware).** `simcheck.out`: the 17 instructions as the simulator
decodes them, then `posstore: 2048 pixels, 0 failures`: at each pixel of the 64 x 32 area the four
stores land at 0x5CAF0000 + 16 x slot with pa0, pa0, pa1 and the lane tag, and o0 is pa0.
`posstore_sim.rs` repeats the check on the template as `sgx-tools` assembles it.

**What it shows.** [infer] The program does what its rows need, as far as sgx-sim models a
triangle's pixel task: each stored slot carries its own position (value = slot position) and lane,
so a wrong slot or a wrong value is visible in the scratch read-back. It reads only the three
globals measured in a triangle's pixel task; since g23 and g24 repeat every tile, two tiles of a
job share slots, and a run's rows must each touch one 32 x 16 tile.

**What it does not show.** Anything about the hardware: the program has not run on the laptop.
The simulator runs one instance at a time (no lanes run together, no invalid instances of a
touched quad, so dword 0 against dword 1 is not exercised), and the register-offset store rule is
measured in end-of-tile and vertex tasks (`eot_tile.s`, `vtx_dump_sa.s`), not in a triangle's pixel
task. Nothing here bears on Q291's band itself.
