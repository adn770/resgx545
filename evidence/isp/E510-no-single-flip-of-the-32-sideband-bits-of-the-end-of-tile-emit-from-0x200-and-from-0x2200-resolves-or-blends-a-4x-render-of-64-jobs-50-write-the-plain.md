+++
id = "E510"
claim = "No single flip of the 32 sideband bits of the end-of-tile emit, from 0x200 and from 0x2200, resolves or blends a 4x render: of 64 jobs 50 write the plain triangle and background of 1248 and 2848 pixels, bits 0 and 1 change the byte order of the colour (0xff403020 and 0x403020ff for 0xff203040, no new colour), bit 2 packs two ARGB1555 pixels a dword (0x90c8, 0x83e0, 2048 dwords left at the fill), bit 3 writes 1024 pixels of 0xffffffff, bit 9 cleared from 0x2200 (0x2000) writes 128 background pixels, bit 12 set on 0x200 writes 14 values (four of them 0x0066 and 0x0000 pairs, none a mix or a copy of the two colours), and 4 jobs fail (bit 9 cleared from 0x200 hangs, bit 11 faults from both, bit 12 set on 0x2200 hangs); no pixel holds an average of the two colours (the control image has 24 aligned 2 x 2 blocks that mix them)"
unit = "isp"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e), probes/isp/msaa-resolve.toml (script msaa-resolve.sh, risky, run in the resume after the recovery path was changed: see the script's header and phases.toml): the 4x render of our stack with the closed driver's TE words (mode 2, 0xe0000000, 64 x 64) and macrotile words, the green shader, eot_plain with each of the 32 sideband bits flipped from 0x200 and from 0x2200 and the two controls, 66 jobs, one run each, every pixel kept"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["isp-msaa-resolve"]
terms = ["CR_ISP_MSAA", "CR_TE_AA"]
+++

**What ran.** 66 jobs (2 controls, 32 flips from each base): the controls give 4096 pixels, 1248
green and 2848 background (E439's counts). 62 jobs complete, 4 fail: bit 9 cleared from 0x200
(sideband 0) hangs the job, bit 11 faults it from both bases (0xa00, 0x2a00), bit 12 set on 0x2200
(0x3200) hangs it; the GPU recovered each time without a retry.

**Outcomes.** 50 of the 64 flips draw exactly the controls' two colours in the same places (bits 4
to 8, 10 and 13 to 31 from both bases, 25 + 25 jobs; bit 13 of 0x2200 gives 0x200 again). Bits 0,
1, 2, 3 give the same result from both bases: bit 0 the colours in the order 0xff403020, bit 1 the
order 0x403020ff (counts unchanged, 2848 and 1248), bit 2 two ARGB1555 pixels in one dword (0x90c8
background, 0x83e0 green; 1412 + 612 dwords of two equal pixels, 24 of mixed pairs of adjacent
pixels, 2048 dwords not written), bit 3 1024 pixels of 0xffffffff and 3072 not written. Bit 9
cleared from 0x2200 (0x2000) writes 128 background pixels and leaves 3968 at the fill (from 0x200
the same flip, bit 9 to 0, hangs the job); bit 12 set on 0x200 (0x1200) writes 14 values, the four
commonest 0x00660066 (1632), 0x00660000 (1196), 0x00000066 (792) and 0x00000000 (440), and ten
more (36 pixels), none of them a copy of 0xff00ff00 or 0xff203040 or a mix of the two. The 66 jobs
are labelled heldout in cases.tsv and declared.tsv, although plan.md calls them one run each, an
exploration (Q089 sidebands, no sets); no claim here counts them as held out.

**What it shows.** [HW] The sideband word selects the pixel format and the write pattern of the
end-of-tile task (channel order, a 16-bit pack, a partial write), none of its single bits turns the
4x samples into one averaged pixel: no pixel in the 50 jobs that draw the plain image holds a colour
between the green and the background, although the control image has 24 aligned 2 x 2 blocks that
mix the two (partially covered pixels where an averaging stage would give a third colour); the
changed jobs of bits 0 to 3 are the colours reordered or repacked, and those of bits 9 and 12 are
other values, none of them a mix. This colour test is limited to single-bit sideband changes of
our own emit. Together with E439 (no blend with the closed
driver's two sidebands and bit 48) and E508 (the stored image is one window of the samples) the
end-of-tile task has no resolve in a single-bit change of the sideband [infer].

**What it does not show.** Two or more bits together; a resolve in a later pass of the closed
driver (Q089); the sideband of the closed driver's own end-of-tile program (we run our own).
