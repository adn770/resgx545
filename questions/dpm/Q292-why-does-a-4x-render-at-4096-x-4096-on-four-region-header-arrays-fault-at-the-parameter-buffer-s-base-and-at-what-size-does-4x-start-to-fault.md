+++
id = "Q292"
question = "a 4x render of the full triangle on a context made for 4x targets (four region-header arrays) faults at the parameter buffer's base (BIF_INT_STAT 0x90100, BIF_FAULT 0x10000011) past 1024 x 768 on its own maximum, with stream offsets of the first region headers zero (E869), and completes at the same size on a context made for a larger maximum with more tail-pointer room (E867): what part of the context's layout does a 4x job need, as a function of its target, which no fixed size limit and none of four tail-pointer extents gives (E868), and what clears the stream offsets"
unit = "dpm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E828", "E824", "E845", "E846", "E866", "E867", "E868", "E869", "E870"]
terms = ["Parameter Buffer (PB)", "CR_TE_AA", "CR_BIF_FAULT"]
+++
Split on 2026-11-11 from the laptop check R3-rgn4 (E828), job j4: with the fork's 4 MiB TA-data
slot a context made with `DRM_SGXFIVE_CTX_RENDER_AA_4X` for 4096 x 4096 is created, but the 4x job
(E824's words, `CR_TE_AA` 0xe0000000, mode 2, `--keep-overflow`) faulted with `BIF_INT_STAT`
0x90100 and `BIF_FAULT` 0x10000011. Page 0x10000 is the first page of the PARAMETERS heap, the
`param_base` of a render context in slot 0 in the kernel's layout, below the PB pages it maps from
`param_base` + 0x1000 (E828, read from the fork's code). 1048576 of 16777216 pixels were right
and the first wrong one is (1024, 0); 1048576 is 1024 x 1024, which would fit a right block at the
top left, but no image was kept to check it. No dump was written, so the four-array TA data size
there (0x223000 bytes by the layout model) was not measured. The health check passed 3 of 3
after it.

Known around it: four arrays complete every 4x size run from 64 x 64 to 1024 x 768 (E824, 8 of 8
held out; E828's 288 x 144 with the flag). Not run: any 4x size between 1024 x 768 and 4096 x
4096. Not examined when this was written: how full the parameter buffer (0x422 pages, its maximum and
default; the debugfs `render_pb_pages` only shrinks it from 0x23 up) gets at 4x; the "ZLS buffer"
of the first reading is `td.zls`, the ZLS external-Z region headers, not a depth buffer.

What is open: whether the fault is the parameter buffer running out at 4x (a DPM behaviour, as in
Q103's overflowing scenes), the ZLS buffer, or something else in the layout at that size; and the
size where 4x on four arrays first faults. If the answer turns out to be our kernel's sizing
alone, that part is split off as a kernel question.

To settle it: on a flagged context, a ladder of 4x sizes from 1024 x 768 to 4096 x 4096 (for
example 1280 x 1024, 2048 x 1536, 2048 x 2048, 4096 x 2048), with `--dump-render` and the fault
read at each; then the same size at 1x as a control, with the kept image to see which pixels are
right. A larger `render_pb_pages` cannot run: 0x422 is both the default and the maximum (the PB's
page table sits at `SGX_RENDER_PARAM_PT` 0x423000), so the knob only shrinks the buffer.

Note 2026-11-11 (round 4, an offline reading of E824's dumps and of the fork; [infer], a fit and
not a test; the reading is not held out). Page need at 4x: the non-zero pages among the 0x422 PB
pages of E824's eight dumps (k-f4, four arrays, `--tri-full`, `CR_TE_AA` 0xe0000000) and of the two
64 x 64 dumps equal 1 + ceil(2 x (W / 16) x (H / 16) / 32) in 10 of 10 (2, 2, 12, 19, 37, 14, 49,
76, 33, 193 pages; page 0 holds the object, every later page 32 full 128-byte slots; the formula is
one stream per 16 x 16 pixels twice over, twice E773's 1x count), and K2's held c1 agrees from the
register 0x0724 (0x000b000b, 11 pages, 288 x 144). By that fit E828's j4 needs 4097 pages at 4096 x
4096 against the 1024 a buffer of 0x422 pages gives when a scene overflows below P - 0x22 (E625,
E735, E773): an overflow by about 3073 pages, and the same triangle at 1x would need about 2049
[model]. So j4 would be the first 4x partial render on record, and the narrowed question is why an
overflowing scene faults at 4x where it ends in -ENOSPC at 1x (the fork has no partial renders:
`sgx_render.c` returns -ENOSPC and leaves the image undefined; E311, E438 and E412 ended that
way). "At what size does 4x start to fault" becomes where the need exceeds P - 0x22: above about
2048 x 2032 for the full triangle, with 2048 x 2048 one page over. The fault word has a precedent:
`BIF_INT_STAT` 0x90100 with `BIF_FAULT` 0x1000001x in E511's HS jobs (0x10000016, 0x10000012,
0x10000013), page 0x10000, `SB` 1, requestor bit 8, which no other record shows; page 0 of a
parameter slot is never mapped, so a 3D-side reader following a zero stream pointer would give it.
After j4's reset `CR_CLKGATESTATUS` read 0x78 and `CR_EVENT_STATUS2` 0x440 (K2's texture fault read
0x20 and 0x440), which fits a TA still waiting for pages; confound: j2's TA write fault came 54 s
earlier on that boot. 1048576 right pixels with the first wrong at (1024, 0) is one 1024 x 1024
block, a macrotile of a 4 x 4 split [infer; no image kept]. Refuted by: a 4x size with a need below
1024 pages that faults, or a small 4x overflow that ends in -ENOSPC. A held-out check (the 1x
control, a 4x size just under and just over the limit, and 1024 x 768 at P 0x80 and 0x100) is
planned for the next laptop session, not run.

Narrowed 2026-11-11 (round 4, session R4-render4x, E845 and E846; the question text above is the
narrowed one). The overflow reading of the note above is refuted held out: stage p's frozen H-PB
(every held-out size whose need passes completes) is not supported, 0 held, 2 FAILED, 4 cannot
tell: the 4x full triangle on four arrays faulted with j4's word (0x90100 at 0x10000011, `SB` 1,
`CID` 1) at 1280 x 1024 and 2048 x 1536, scenes of 321 and 769 of the 1024 usable pages, no pixel
right, health ok after each; the stage stopped at its second fault, so 2048 x 1920, 4096 x 960,
960 x 4096 and 3072 x 1280 did not run (E845). Stage o's frozen verdict is cannot tell, its 1x
control o2 frozen for the full triangle while its row ran the default one (19 pages, so it
completed); read after the run and not rescored, a 4x overflow ends in -ENOSPC without a fault as
at 1x (1024 x 768 at P 0xe2, need 193, with 0xe3 completing; 288 x 144 at P 0x23), and 4096 x 1152
(need 1153) faulted with j4's word (E846). So the fault is about the size, not the parameter
buffer. What the records bound: every four-array 4x job that completed was at most 1024 x 768
(E824, E828, E845, E846) and every one that faulted at least 1280 x 1024 (E828, E845, E846); the
onset is past 1024 wide (2048 samples), past 768 high (1536 samples), or past both, and no run
separates them. Open: which of these starts it, and what the 3D-side access at page 0x10000
(requestor bit 8) is. To settle it: 4096 x 960 and 960 x 4096 (the two cells p did not reach),
then a ladder in the dimension that faults (1088, 1152, 1216 wide at 768, or 832, 896, 960 high at
1024), with a kept image of each faulting job.

Narrowed 2026-11-12 (round 5, session R5-render4x, E866 to E869; the question text above is the
narrowed one). Not the overflow, now under a frozen verdict: a 4x scene that overflows ends in
-ENOSPC without a fault, one page short of its need, held out at 640 x 480 and 512 x 384 (H-ENOSPC4,
6 of 6 rows decided, E866). The cause depends on the context: 1280 x 1024 completed on contexts made
for 1280 x 1040 and 2048 x 2048 and 2048 x 1536 on 4096 x 4096, whose tail-pointer room (4 side^2
bytes) is four times their own, and 1280 x 1024 faulted on 2048 x 1024, whose region buffer grows
and whose room does not (H-TPC held, 4 of 4, every size rule refuted, E867). The onset on the
target's own maximum fits none of the eleven frozen rules over the 13 decided rows: 1184 x 768, 1024
x 800, 1280 x 768, 1024 x 1024, 2048 x 240 and 768 x 2048 faulted, 1024 x 512 and 256 x 1536
completed, so no width, height, count, page or area limit, and none of H-TPC's four extents of the
doubled grid (d, rs, rb against the region headers or the state page) fits; a post hoc search of 192
such extents finds none (E868). The held 1280 x 1024 fault (E869) replicated E845 with the whole
scene written (321 pages): 1212 of 12288 region headers are off the rule from td.rgn 0x7000 to
0xd804, most with word 0 intact and a zero stream offset, in macrotiles 0 to 2, and nothing below
td.rgn is non-zero [post hoc]; [infer] a zero offset sends the 3D to the request base, the fault's
page. Open: the extent a 4x job needs as a function of target and maximum, and what clears the
offsets (the TA's tail pointers or the order of the TA's writes); the 4096-wide residue (a right
block, E828, E846) stays as it was.

Planned 2026-11-12 (decision R5-8 a; a kernel item for the next boot, no kernel work this round).
Since H-TPC held in E867's reading, the kernel's tail-pointer room on a context made for 4x targets
is to be sized for the doubled tile grid: side doubled, four times the bytes
(closing5/render4x/exp-render4x-r5.md section 4). Every four-array 4x job whose context had at least
that room for its target completed, 4 of 4 (E867's m0, m1, m2, m4), and none faulted; every
own-maximum job had less [post hoc]. At 4096 x 4096 the TA data grows from 0x223000 to 0x2e3000
bytes, inside the 4 MiB slot. The change goes KUnit first in the fork, built on cachix, booted
one-shot with the user's OK; its held-out test: the own-maximum cells that faulted (E845, E868: 1280
x 1024, 1184 x 768, 1024 x 800, 2048 x 240, 768 x 2048, 2048 x 1536) complete with 0 wrong pixels
and no region header off the rule, and the completed ones stay so. If it holds, E824 and E828 get
corrections (their four-array layout lacks the tail room) and this question narrows to the extent's
rule.

Note 2026-11-12 (round 6, an offline reading, decision R6-1 a; E870; post hoc, one dump, not held
out). The form of what a 4x job needs: H-TPM, the tail pointers one dword per tile of the doubled
grid (16 x 8 pixels) at TA-data offset 4 x Z(x, y), Z-order with y on the even bits. On E869's held
dump against E867's completed m1, the 1023 headers that lost their stream offset are exactly the
1023 whose word 1 lies at an in-target tile's entry (0 extra, 0 missing; with x on the even bits
426). "Fault iff 4 x (Z(2tx - 1, 2ty - 1) + 1) passes the `td.rgn` of the context's maximum" gives
26 of 26 four-array outcomes on record, E868's included, but the planner had read all 26 before
writing it and scored 16 variants on them (2 fit, the target's or the header grid's tiles, which
no own-maximum size up to 2048 separates), so it is an offline check, not a test. What stays
open: a held-out test of that rule (rows on the rgn4 kernel where it disagrees with every
size rule, such as 1024 x 1280 completing on its own maximum, and held faults with the frozen
set of lost offsets; closing6/render4x/exp-render4x-r6.md section 2), and to what E870 leaves
unexplained: 189 word-0 losses at header-grid entries outside the target, bit 27 set on 914
headers whose entry lies in the headers (in no completed dump), and the 4096-wide right blocks
(E828, E846), which H-TPM does not give. If it holds, the room a 4x context needs is 4 x (Z(2tx -
1, 2ty - 1) + 1) bytes, at most 4 x (2 side)^2, so the planned room (side doubled, four times the
bytes) is a bound at every size.
