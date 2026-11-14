+++
id = "E1086"
claim = "r19-flag stage fl (3 jobs, t18b, module E0CC40275493F8AEAD8180B, the flagged session with the user's OK, 2 planned rows, no fault and no hang): on a 1024 x 768 scene whose geometry kick overflows once at P = 0x28 and whose closing render has N = 0x100 pages and does not overflow, filling the state page (page 6 of the TA data, 18 non-zero list dwords after the kick) with the ramp 0xa5000000 + i just before the closing render's kick (the kernel logged the fill applied) changed nothing: both junk rows ended ok with the same last target hash (0xed1bce7108aded25, 0 of 786432 pixels wrong) as the unfilled control, the same parameter buffer and the same TA data except page 6, whose 1024 ramp dwords all stayed (the render stored nothing over them); H-NOLOAD held on the fit row and its held-out replicate, 2 of 2, against H-LOAD-FAULT, H-LOAD-HANG and H-LOAD-CORRUPT"
unit = "dpm"
method = "r19-flag (render/closing-r19-flag), stage fl of the question-closing pass, round 19, the flagged session (a planned fault or recovered hang possible; the user's OK given, closing19/DECISIONS-R19.md R19-3 a: fl-junk only, `#limit 2` counting only its two planned rows, a control that can fail, strict health after each job, a stop at an unplanned fault or failed recovery, on_stop end), plan closing19/plan/rank-round19.md section 5; the builder folded it; on the laptop (travel cable), kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (fork 456404fcffe5: render_final_pb_pages), stock firmware, tool t18b (sha256 58e79855..., built from resgx545 ec50498, source sha256 70aa910e...), t10 for the health tool; table fl: fl-ctl (safe control, no fill), fl-junk-a (fit) and fl-junk-b (held-out replicate), each `tri --width 1024 --height 768 -n 2 --geometry 1 --final-pb-pages 0x100 --keep-going --keep-overflow --wait-ms 20000 --dump-render $W --dump-each --words $W --regs 0x0600-0x0750` with the debugfs knob render_pb_pages 0x28 (restored after each job), the junk rows with `--tadata-fill-render 2:6:0xa5000000:ramp`; attempt out/20261114-225916 (rc 0; score-fl.txt); freezes: FROZEN.sha256 7545a4d906956e398dca1869b3e74de85713b3a95f89ddda559725b7eb25e5fd, PREDICTIONS.sha256 (fl.tsv, the frozen readings and models), FROZEN.commits (kit copies of resgx545 6809cddd, t10 and t18b built lines); the runner expects SRCV_EXPECT E0CC40275493F8AEAD8180B; no stop in the logs, no failed recovery"
tiers = ["HW"]
date = "2026-11-14"
data = ["render-closing-r19-flag:out/20261114-225916/fl/", "render-closing-r19-flag:fold/"]
terms = ["CR_DPM_STATE_BASE0", "CR_DPM_TASK_STATE"]
+++
**What ran.** One stage, three jobs, after the round's safe sessions. The form is E631 Part B's on
the module's final-render knob: render 1 is a geometry kick that overflows the 0x28-page parameter
buffer once and leaves the scene open (one partial render, E625; 0x0624 read 0x06 after it), render
2 closes the scene on N = 0x100 pages, so it does not overflow and, unlike E631's, no longer
stores its own lists over page 6 before anything could read them. `fl-ctl` is the safe control
(no fill); `fl-junk-a` and `fl-junk-b` fill page 6 of the TA data (the state page of a 1024 x 768
context, E627, E631) with the ramp 0xa5000000 + i through the kernel's `tadata_fill`, armed before
render 2 and taken by its kick. Frozen: **H-NOLOAD** (the final is the control's: ok, same target
hash), **H-LOAD-FAULT** (a BIF fault), **H-LOAD-HANG** (a recovered hang), **H-LOAD-CORRUPT** (ok,
a different image) [infer]; fl-ctl frozen to read job ok, one overflow, 0x0624 = 0xde (N - 0x22,
the module's threshold update, round 19's r19-k0) and lists in page 6 before the fill.

**Frozen verdict (as printed).** attempt 20261114-225916, stage fl (run.log): `SUMMARY: fl:
H-NOLOAD: no task reads the state page's lists: the junk changes nothing (image of the unfilled
twin) (2 of 2 rows decided)`. Rows: H-NOLOAD held on `fl-junk-a` and `fl-junk-b`; H-LOAD-FAULT,
H-LOAD-HANG and H-LOAD-CORRUPT FAILED on both. fl-ctl PASS (job ok, ovf 1, thr 0xde, lists yes).

**Results [HW].** All three jobs ended `job: ok`, rc 0, strict health clean after each, no `SGX
recovery failed` and no fault or hang in any kept kernel slice. The control: the kick overflowed
once (`tri 1024x768 #1: overflowed`), 0x0624 0x06 after render 1 and 0xde after render 2, the
final 0 of 786432 pixels wrong (hash 0xed1bce7108aded25), page 6 after the kick 18 non-zero
dwords. Both junk rows: the kernel logged `tadata_fill page 6 ramp from 0xa5000000 applied`, the
same overflow and thresholds (0x06, 0xde), the same final hash and 0 pixels wrong, a final of
805 ms (control 814 ms). fold/compare_tadata.out: the dump after the kick (before the fill) is
byte for byte the control's; the dumps after render 2 and at the end differ from the control's in
page 6 only, all 1024 dwords of the ramp still there (the control's 18 list dwords there are
likewise unchanged by the final), and the parameter buffer is equal in all three dumps of both
rows. The two junk rows agree in everything (the replicate read the same). The scorer re-run is
byte for byte (fold/reproduce.out).

**What it shows.** [HW] The closing render of a scene whose partial render stored lists in the
state page does not read them back: with those 1024 dwords replaced by a ramp of page numbers
past any page table (E631's junk) before its kick, it neither faulted nor hung nor drew
differently, and stored nothing into the page, 2 of 2. This closes E631's blind spot (the next
kick's own partial render used to overwrite the first 34 dwords), so the "no load task read the
junk" reading of E631 now holds for a final that does not overflow; the zero fill of round 19's r19-dpm is the other half of Q045's load clause [infer]. It is consistent with 0x0740 reading
0 in every job (E256, E574): no load task is issued [infer].

**What it does not show.** Whether a load is issued by a final that itself overflows (it would
store over the page first), by a kept second context's first render (Q191, Q192), or at a
different P or target size; what the 18 list dwords are (Q045's state-page statistic is r19-dpm's ldb).
