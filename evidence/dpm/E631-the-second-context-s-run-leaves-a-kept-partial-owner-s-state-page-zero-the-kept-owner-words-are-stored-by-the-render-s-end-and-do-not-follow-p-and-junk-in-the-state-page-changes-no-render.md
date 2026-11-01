+++
id = "E631"
claim = "In one case, a kept partial-render owner of 1024x768 in 0x28 pages, the state page the owner left is zero after the second context's run, by an event of that run not separated (the 1024x768 context in 0x28 pages: 18 non-zero dwords in page 6 alone and with the render flag poked 0xc or 0x4 and no second context, 3 of 3 runs identical; read after the tool exits, page 6 holds 0 non-zero dwords after the second context's run with flag 0xc and with flag 0x4, 2 runs of each, 4 of 4, the cause (the creation, the render or the close of the second context) not separated for this owner, whose pages were not copied before the close; pages 1 to 3 (the control, OTPM and state pages) hold no owner word at all with either flag, so the owner words of the 64x64 owner are not seen here) and with flag 0x4 alone 5 dwords (0x200057, 0x2000ad, 0x20007e, 0x2000c0, 0x200087) are written into page 4, 2 of 2 (nothing in page 4 with flag 0xc); closing the partial owner without keeping it makes the second context's render fault (BIF fault status 0x90400 at 0x3241100f, `job faulted, context lost`, recovered by a reset, flags 0xc and 0x4, 2 of 2, the address one page below the ctx word 0x32412000 of the job's words, so the second context's render reaches memory next to the closed first context's, a read or a store not shown); for a 64x64 owner the kept words land by the end of the second context's render, not at the close (a copy of render_kept made after that render and before the close equals the copy made after the tool exits: 75 non-zero dwords, words 0x00200047, 0x04000417, 0x00020001 and 2 in pages 1 to 3, flag 0xc; with flag 0x4 alone the pages 1 to 3 are 0 in both copies, 71 non-zero dwords elsewhere, 2 of 2 runs each); the words do not follow the buffer: 0x04000417 at P = 0x422, 0x300, 0x200 and 0x100 (4 of 4), 0 in page 2's word 0 when the first context rendered 2 or 3 times (0x00200047 and 0x00020001, 2 stay; 2 of 2 each, repeated), and the first word follows the target size (0x00200047 at 64x64, 0x00200044 at 64x32, 0x00200042 at 32x32); the state page's first words are (count << 16 | head) and tail of the owner's 2 pages in all 8 first-context jobs; junk written into the state page (page 6 of a 1024x768 context) between a geometry kick that overflows and the next render (zeros, and the ramp 0xa5000000 + i, at 0x30 and 0x28 pages, 4 jobs) leaves the page table walk and the image identical to a control without it (4 of 4); the next render's own partial render stores the lists over the page's first 34 dwords, so a load of the lists themselves is not separated, and the other 990 of the 1024 ramp dwords stay after the render with no effect on it"
unit = "dpm"
method = "tri --ctx2 --close-first-early with render_keep armed and the first render flag poked (--kpoke-render 1:ta:7^=0xc or 0x4), the kept pages of the first context read through debugfs render_kept after the tool exits and, in the 64x64 jobs, copied after the second render and before the close (--kept-copy); a geometry kick that overflows followed by --tadata-fill-render (zeros or the ramp 0xa5000000 + i in page 6) and a second render; on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool sgxfive-test-1135 (sha256 7732b945...) for Part A and sgxfive-test-1139 (source sha256 70b09d58..., binary fdf876ea..., the 11.35 tool plus three options) for Part B; table owner (21 jobs) and follow-up b (9 jobs)"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["dpm-partial-model-batch"]
terms = ["CR_DPM_STATE_BASE0", "CR_DPM_CONTROL_BASE", "CR_DPM_TASK_STATE", "ta3d_ctl"]
+++

**What ran.** Table `owner`: Part A (8 jobs, the unchanged tool 1135, `render_keep` armed, `tri
--ctx2 --close-first-early` with the first render flag poked `--kpoke-render 1:ta:7^=0xc`: the
64x64 job of E591 and the first context varied: 1 to 3 renders, 64x64, 64x32, 32x32, P = 0x422,
0x300, 0x200, 0x100) and Part B (13 jobs, the changed tool `sgxfive-test-1139`, built on the
laptop, source sha256 70b09d58..., binary sha256 fdf876ea...: `tri --keep-overflow --ctx2`,
`--tadata-fill-render N:PAGE:VALUE[:ramp]` and `--kept-copy DIR`; the probe's depth scratch is not
implemented and no case uses it): `ow-part-*` (the first context 1024x768 on 0x28 pages, flags 0xc
and 0x4, kept and not kept, against `ow-part-solo`), `ow-kcopy-*`, `ow-fill-*` (zero and ramp,
0x30 and 0x28, against a control). Follow-up b (9 jobs: repeats of 7 cases and the two flag-poked
solo controls, written and hashed before they ran). Same laptop, kernel, module, firmware as E625;
no clock-gate register, no kreg, no trc_hazard. The 4 closes without keep and the ramps ran in the
risky script.

**Results [HW].** H192-R (declared: the second context's store replaces the state page with flag
bit 3 and leaves it with bit 2 alone): hit with 0xc, missed with 0x4: in 2 runs of each flag (4
runs: `ow-part-c-k`, `fb-part-c-k-r2`, `ow-part-4-k`, `fb-part-4-k-r2`) the page is all zero when
the kept memory is read after the tool exits, in the 2 solo controls with the flag poked it is the
solo page (identical, whole kept memory 69632 bytes, 2 of 2) so the zeroing is the second
context's and not the flag's. The kept words (Part A and E591): page 1 word 0 0x00200047, page 2
word 0 0x04000417, page 3 words 0x00020001, 2 for 64x64 at all four buffer sizes; H191-P (the OTPM
word's high half is P - 0x22) fit 1 of 1 and held out 2 of 7: the high half is 0x0400 at every P,
so it is not the buffer's size; the word is 0 in the jobs with 2 and 3 renders (the page-3 word is
kept); the first word falls to 0x44 and 0x42 with the target (64x32, 32x32). H191-L (the state
words are the owner's page list, (U << 16) | 1 and U): 8 of 8, with U = 2 in all of them, so it is
not separated from a constant. The kept copy: `ow-kcopy-c` holds the words at the end of the
second context's render (the copy before any close), identical to the copy after the tool exits
(75 non-zero dwords); with flag 0x4 alone neither copy has them (71 non-zero dwords): the store is
made by the render's end; whether at the second context's TA kick or its render's end is not
separated (an optional kernel switch that would separate them was not built). H45 (does a load
task read the state page): the page poked with zeros and with the ramp before the second kick of a
job whose two kicks overflow: the page-table walk of the pool and the image equal the control in 4
of 4 (H45-R: 8 of 8 scores, 4 jobs by two scores, and 'no load task read the junk' is as strong as
the test: the poke is overwritten in its first 34 dwords by the second kick's own partial render,
the lists being stored again, so a load of the lists themselves is not separated and only the
other 990 dwords were never reached by a store), H45-L 0 of 4. H45-R and H45-L (8 scores) were "no
data" in the frozen recompute and are scored by the corrected copy (the dataset's method). The
closes without keep: both second contexts faulted (BIF fault 0x90400 at 0x3241100f, PD 0x0, `job
faulted, context lost`), the GPU recovered at the reset and the health triangle was exact; the
64x64 owner of E462 faulted at 0x20003000 (another page). Repeats: the Part A words, the page-2
word at 0 for 2 and 3 renders, the kcopy and part cases: 7 of 7 repeated cases identical to their
first runs (follow-up b).

**Reading [infer].** For the 64x64 owner the words are written by the slot step of the next
context's render for flag 0xc (E591), at the render's end at the latest; page 3's first words are
the owner's page count and head there (8 of 8 first-context jobs, all with 2 pages, so not
separated from a constant), and the control page's word encodes the target's size class (0x47,
0x44, 0x42); the 0x04000417 is not a buffer size. The partial-render owner (1024x768, 0x28 pages)
leaves no owner word in its control, OTPM or state pages with flag 0xc and only the 5 words of
page 4 with flag 0x4: that sits badly with the owner's page list being in the state words (H191-L)
beyond the 64x64 owner and is not explained. A second context replaces a partial owner's state
page with zeros, so a model of the owner has nothing to load from it.

**Not shown.** Which kick of the second context stores the words (the kernel switch not built);
what the OTPM word is (0x0400 at P from 0x100 to 0x422 for one render, 0 for two or three); what
the 5 words in page 4 with flag 0x4 are; whether a load task reads the lists themselves.
