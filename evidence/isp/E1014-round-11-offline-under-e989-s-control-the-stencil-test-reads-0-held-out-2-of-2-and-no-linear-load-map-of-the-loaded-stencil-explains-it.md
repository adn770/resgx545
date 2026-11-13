+++
id = "E1014"
claim = "Round 11 offline (Q071; no run): under E989's control (0xf8e6a00e: the bits E411 flipped singly to no effect flipped together, so bits 12, 16 and 20 cleared as in E997's linear store), the stencil test of r10-st1's rows q071-b0 and q071-l1 reads 0, not the loaded buffer at a linear offset: with the rules frozen by hash (q071_rule.py, 5f705c49...) before either row was opened, H-ZEROLOAD (every test reads 0, the invert stores 0xff) held 2 of 2 (2048 of 2048 pixels and 73728 of 73728 stencil-store bytes each), and three linear load maps (byte 64 y + x, E997's stride; raster inside the 512-byte tile slot; byte 4 (64 y + x)) and E988's twiddled order failed 2 of 2 (1024 extra pixels, or 70176 to 72192 of 73728 store bytes); the twiddled order held E988's base rows st1-b0 and st1-lane1 (the controls, 2 of 2) and the four other maps failed them [HW data, held out in rows]; [infer] any one-to-one map of the 2048 loaded bytes passes half the pixels under a one-bit mask, so 2048 drawn needs the loaded byte unread; no kept row clears a strict subset of bits 12, 16 and 20 (the 56 --depth-ctl values of resgx545-data), so which bit linearises the store and which one stops the stencil read is not separated"
unit = "isp"
method = "Offline, no run (round 11, decision R11-5 (a), package P2; the round 11 ranking, finding 2). Data: r10-st1 (render/closing-r10-st1, dataset render-closing-r10-st1) attempt out/20261113-103934, stage st1: the held-out rows q071-b0 and q071-l1 (E989) and the control rows st1-b0 and st1-lane1 (E988's base rows), each row's loaded stencil (.stencil.1.bin.gz), stencil store (.stencil-store.1.bin.gz) and drawn count (.txt.gz). The ranking's closing11/plan/c4-q071/: q071_rule.py (the five rules with E988's test: a pixel draws iff (byte & mask) == 0, the store byte inverted where drawn, the unwritten bytes the 0xdeadbeef fill; sha256 5f705c493cec7a6b2a4684291766ccab005b27e289cb0796b95d6009be4a8528 in q071_rule.sha256; FREEZE.log, 11:04:02Z, lists what was read before the freeze: the records, the session's generator, tables, scorer and fold notes, and one format probe of st1-b0, no q071-* file), q071_score.py (standard library) and its q071_score.out; ctl_all.txt, every --depth-ctl value in resgx545-data's tables, scripts and notes. This record re-ran q071_score.py with the repository's .venv (python -B) and got q071_score.out byte-identical to the ranking's."
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r10-st1:out/20261113-103934/st1/", "cited-scratch:closing11/plan/c4-q071/"]
terms = ["CR_ISP_ZLSCTL", "ISP2"]
+++
**What was done.** E997 found that bits 12, 16 and 20 of CR_ISP_ZLSCTL cleared together store a
linear image of the tile area instead of the twiddled tiles. E989 ran the same control mask under
E988's stencil test against a loaded stencil and saw every pixel drawn and 0xff stored at every
byte, as a test reading 0 would. The two together allow a second reading of E989: the load is
linear too, and the test reads the loaded bytes at other offsets. The ranking froze five rules by
hash and then scored the two E989 rows (never opened before) and E988's two base rows as controls.

**Results [HW data].** q071_score.out, per row: the drawn pixels against the rule's (2048 a row)
and every byte of the 73728-byte stencil store.

| rule | st1-b0, st1-lane1 (controls) | q071-b0, q071-l1 (held out) |
|---|---|---|
| H-TWIDLOAD (E988's order) | held 2 of 2 | failed 2 of 2 (1024 extra pixels) |
| H-LINLOAD-A (byte 64 y + x) | failed (512 extra, 512 missing) | failed 2 of 2 (1024 extra) |
| H-LINLOAD-B (raster in the slot) | failed (512 extra, 512 missing) | failed 2 of 2 (1024 extra) |
| H-LINLOAD-C (byte 4 (64 y + x)) | failed (1024 missing) | failed 2 of 2 (store 70176, 70656 of 73728) |
| H-ZEROLOAD (the test reads 0) | failed (1024 missing) | held 2 of 2 (2048 pixels, 73728 bytes) |

Both held-out rows drew 2048, stored 0xff at the first 2048 bytes and left the fill past them, and
their loaded buffers are the fill pattern. H-LINLOAD-C draws all 2048 pixels on these rows by
chance of its spread offsets but writes the store at offsets up to 8188.

**Other rows.** ctl_all.txt lists the 56 --depth-ctl values of resgx545-data. The rows with any of
bits 12, 16 and 20 cleared clear all three (r10-x's zb-clr-f0, zb-all-f0, zb-all-f1, zb-all-load,
and E989's two); E411's single clears stored a constant fill, which shows pages, not a layout.

**What it shows.** Under E989's control the stencil test does not read the loaded buffer in any
of the linear orders E997's store suggests, nor in the twiddled one: it reads 0 [HW data, 2 of 2
held out]. [infer] Any one-to-one map of the 2048 loaded bytes would pass exactly half the pixels
under a one-bit mask, so the 2048 drawn pixels need a byte that was not read from the buffer;
E989's claim stands as written, and the reading "the load is linear too" is refuted.

**What it does not show.** Which of bits 12, 16 and 20 (or which of 15, 21 to 23 and 27 to 31)
makes the store linear and which stops the stencil read: no kept row clears a strict subset of the
three. Whether a depth load under the same control is linear (the store with every byte 0xff cannot
show a layout). The rows to settle it are laptop rows: each bit and each pair under E977's ramp
store and under E988's stencil test (the round 11 ranking, section 4, row 2).
