+++
id = "E443"
claim = "In timelines of the DPM registers 0x0700 to 0x0750 through 12 renders of the triangle and copies of it at 4096x4096 (3, 900 and 1500 vertices in 0x422 pages, 300 in 0x100, three runs each), the high halves of 0x0710 and 0x071c are 0 in every sample of all 12 runs, 0x072c reaches 0x10001 with 3 vertices, 0x40004 with 900 (three runs) and 0x50005 with 1500 (three runs) and 0x20002 with 300 in 0x100 pages (three runs), and 0x0748 reads 0xb, with bit 2 clear, in 4 of the 12 runs (the three runs of 300 vertices in 0x100 pages and one of 900 in 0x422 pages) and never in the other 8"
unit = "dpm"
method = "probes/dpm/partial-wide-timelines.toml (partial-wide-timelines.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: regtimeline 10.0 0.2 0x0700-0x0750 around probe --tri pixel --width 4096 --height 4096 --vertices N (a green pixel shader; a sample is kept when any register changed: 39 to 923 per run), render_pb_pages at 0x422 (N = 3, 900, 1500) and 0x100 (N = 300), three runs of each of the four cases (12 runs)"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["dpm-partial-wide-timelines"]
terms = ["CR_DPM_3D_FREE_LIST_STATUS2", "CR_DPM_REG_0748", "CR_DPM_3D_PAGE_COUNTS", "Dynamic Parameter Management (DPM)"]
+++

**What runs.** E438's wide scenes, with the registers sampled while the job runs (E358's
timelines covered one to three renders of one triangle and a 1024x768 render with partial renders).
The 900 and 1500-vertex jobs overflow the whole parameter buffer and recover; so does the 300 in
0x100 pages; the 3-vertex job completes.

**Results.** Per run: samples 39 to 52 (3 vertices), 432 to 442 (900), 704 to 717 (1500), 899 to
923 (300 in 0x100).

| case | 0x0710, 0x071c high halves | 0x072c maximum | 0x0724 maximum | 0x0748 values (idle 0x1f) |
|---|---|---|---|---|
| 3 vertices | 0 | 0x10001 | 0x011f011f | 0x1f, 0xf, 0xe (0x6, 0x7, 0x1d in some runs) |
| 900 vertices | 0 | 0x40004 | 0x04000400 | 0x1f, 0xf, 0xe, 0x7, 0x6, 0x1d (0xb in one run) |
| 1500 vertices | 0 | 0x50005 | 0x04000400 | 0x1f, 0xf, 0xe, 0x7, 0x6, 0x1d (0xd in two runs) |
| 300 in 0x100 pages | 0 | 0x20002 | 0x00fe00fe | 0x1f, 0xf, 0xe, 0x7, 0x6, 0xb, 0xd, 0x1d |

0x0748 bit 2 is the one bit E358 never saw clear: it is clear in the value 0xb (bits 4 and 2 clear)
in four runs, three of them the 0x100-page runs. Bit 4 clears while the TA takes pages (0xf, 0xe,
0x7, 0x6, 0xd, 0xb), bit 0 in 0xe and 0x6, bit 3 in 0x7 and 0x6, and bit 1 in 0x1d and 0xd, as
E358 found.

**What it shows.** STATUS2's high halves stay 0 through scenes whose global lists hold up to five
pages and whose low halves reach 0x421: they are not a second page; Q036's question about them rests
on jobs of this size. 0x072c's two halves rise together (0x10001, 0x40004, 0x50005 for 3, 900 and
1500 vertices) as E438's global lists do for the 900 and 1500 jobs (4 and 5 pages) [infer], but the
300 vertices in 0x100 pages reach 0x20002 where E438's list is 1 page, so the match is not general.
Bit 2 of 0x0748 is not a constant: it clears in some runs of scenes with partial renders and not in
the one-triangle runs.

**What it does not show.** What makes bit 2 clear in one run of three (the samples are not
continuous), which register the closed driver's `CR_DPM_3D_PAGE_COUNTS` is (0x0724 and 0x072c read
equal halves), or a scene whose global list holds more than five pages.

**Correction 2026-11-13:** a note, the claim stands. E1019 (round 12 offline) read the same high
halves in every kept closing-pass timeline and after-read, frozen before: 0 in 285824 of 285824
lines of 697 jobs and 1594 of 1594 after-reads, through global lists of 6, 7, 11, 13 and 18 pages.
"A scene whose global list holds more than five pages", which this record does not show, is now
read. E1019 also ranks 0x0748 bit 2's clearing with the count of partial renders [infer].
