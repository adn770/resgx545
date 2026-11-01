+++
id = "E458"
claim = "With the first context closed after a render that keeps the DPM owner with render flag bit 2 alone, a render on a second context at another RT data address is exact and the kept dword 20 stays (4 of 4 runs); with bit 3 (NO_DEALLOCATE) kept, the second context's render faulted at page 0x20003000 in 6 of 6 runs, and with the first context open it was exact and cleared the words in 4 of 4; that the slot step is what stores the kept word is [infer]"
unit = "render"
method = "probes/render/kept-owner-gone-context.toml (kept-owner-gone-context.sh) on the laptop (direct cable), sgxfive-test tri -n 1 --ctx2 with --close-first-early (the first context closed between the renders) or --words-between (open), --words DIR saving debugfs render_words and buf09 as snapshots 0, 101, 201 and 1, the render flags flipped through the kernel poke ta:7^=V (--kpoke-render, --kpoke-render2), 9 cases of two runs, the GPU reset before each; sgxfive-test 6f8f2bf8, linux fork ea5482bc59a6 with the debug option on, module srcversion 9A7BCDC4FC2A2166A409EEA (loaded and installed equal, both printed by the run)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["render-kept-owner-gone-context"]
terms = ["FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE"]
+++

**What runs.** E451 read the kept words with both contexts alive. Here `tri -n 1 --ctx2
--close-first-early` renders the first context with its render flags (TA command dword 7, kernel
value 0x400) flipped through the kernel poke `ta:7^=V` (`--kpoke-render 1:ta:7^=V`), closes it (the
kernel's cleanup of the context runs), and renders the second context in the same VM (RT data at
0x32423300 against 0x32411300). `--words` saves the control block (debugfs buf09) before the first
render (snapshot 0), after it and before the close (101), after the close (201) and after the
second's render (1). With `--words-between` instead the first context stays open and only snapshots
101 and 1 are taken. Cases, two runs each (18 runs, the GPU reset before each): no flip; V = 0x4,
0x8, 0xc in the first; 0xc in both (`--kpoke-render2`); 0x4 in both; then V = 0x4, 0x8, 0xc in the
first with the first context open.

**Results** (TA3DCtl dwords 20, 21 and 25; A = 0x32411318, the first context's RT data + 0x18, B =
0x32423318, the second's; the same in both runs of each case).

| flags flipped | first context | snapshot 101 (20, 21, 25) | snapshot 201 | second context's render | snapshot 1 |
|---|---|---|---|---|---|
| none | closed | 0, 0, 0 | 0, 0, 0 | exact | 0, 0, 0 |
| 0x4 in the first | closed | A, 0, 0 | A, 0, 0 | exact | A, 0, 0 |
| 0x4 in both | closed | A, 0, 0 | A, 0, 0 | exact | A, B, 0 |
| 0x8 in the first | closed | A, 0, A | A, 0, A | faulted | not taken |
| 0xc in the first | closed | A, 0, A | A, 0, A | faulted | not taken |
| 0xc in both | closed | A, 0, A | A, 0, A | faulted | not taken |
| 0x4 in the first | open | A, 0, 0 | not taken | exact | A, 0, 0 |
| 0x8 in the first | open | A, 0, A | not taken | exact | 0, 0, 0 |
| 0xc in the first | open | A, 0, A | not taken | exact | 0, 0, 0 |

The 6 faults (0x8 and 0xc in the first and 0xc in both, two runs each) are all BIF fault status
`0x90004` at `0x200030c1` in the kernel log: page 0x20003000, list 1 (CID 1), the second context's
directory. The first context's job completed in all 18 runs; the tool stopped at the second's fault
and did not check the first render's pixels in those 6. The 12 runs that did not fault checked both
renders: 24 of 24 exact (0 wrong inside, outside and at the edges, guard 0). No recovery failed
(kernel.log is authoritative for the logged counts: the six faults at its lines 109 to 687, no
"recovery failed"; output.txt lost most dmesg lines). The run's cleanup lines carry flags 0x1 in the
6 faulted runs and 0x0 in the 12 that did not fault, which fits a lost context.

**What it shows.**

- Render flag bit 2 alone keeps the first context's owner in dword 20 through the close of the
  context and through a render on a second context at another address, which is exact (4 of 4
  closed runs and 2 of 2 open runs) [HW]. With both contexts keeping it, the second's owner takes
  dword 21 and the first's stays in 20 (2 of 2, as E451).
- Bit 3 (alone, or with bit 2) keeps both words, dwords 20 and 25, through the close of the context
  (snapshots 101 and 201 are equal, 6 of 6) [HW]. With the first context open, the second context's
  render clears both words and is exact (4 of 4 runs): between the renders the words held A, after
  the second's render they read 0, so the clearing is the second render's [HW] (E451 read them only
  after the pair).
- With the first context gone, the same second render faults at page 0x20003000 (6 of 6) and the
  close does not clear the words. That page is, for a context of up to 64x64, its TA data's DPM
  state page (E310); that the slot step stores the kept owner of a context whose memory is gone to
  that page is [infer] (Q106).

**What it does not show.** Why the render faults (Q106), a third context, a first context closed
with its render still queued, and the DPM registers beside the words (read after the second render
only, and not compared; Q106).

**Provenance.** linux fork commit ea5482bc59a6 with the debug option on, module srcversion
9A7BCDC4FC2A2166A409EEA (the loaded module, read from /sys/module, equal to the installed file's
modinfo; both printed by the run), sgxfive-test sha256
6f8f2bf8295d302f50594b02b92989a72a127adc36b0a8cf245cbd14c53da4f5 (built from this phase's overlay
source, named in each env.toml), the laptop over the direct cable.
Revised after these runs: the series was rebuilt on tip 6ee9501832af, which clears armed pokes on
load and reset (commit 40), moves the submission's poke calls into one function,
sgxfive_submit_xfer_pokes() (40), makes alias_skip refuse bits 16-31 with -EINVAL (42) and rewords
comments and commit messages (40 to 42); the module of these runs is the one built from
ea5482bc59a6. The paths this run used did not change [infer]: git diff ea5482bc59a6 6ee9501832af
leaves the render poke path (ta:7^=V) and the context close as they were, and kept-owner-gone-
context.sh resets the GPU before each case and arms its pokes after, so the clear on reset had none
to drop.
