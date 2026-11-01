+++
id = "E707"
claim = "A program equal to E572's eotst-e1 but for the address immediate (a `mov.skipinv r1` and one `stad [r1,+#0], r2` between the two emits, 32 temporaries) completed here, the store landed, where E572's run of it faulted (at 0x340042 or 0x340043): E572's fault was not reproduced; of 10 variants of the form (mov flag, store before or between the emits, 32 or 8 temporaries, one store), 8 completed and 2 faulted, the two with `mov.skipinv` and 8 temporaries (BIF fault 0xd0400 at 0x1, not E572's 0x340042; the value landed first in both), and none of the three frozen models (8 of 10, 6 of 10 and 4 of 10 right) predicted the control to complete; what differs from E572's run is listed in the record and none of it was tested"
unit = "usse"
method = "table eot-store (10 jobs, risky as declared, 2 faults each followed by a reset and a health triangle that drew: probe --temps N --tri pixel --pixels --width 64 --height 64 --slot pixpds=pds_iter_xy.bin:12 --slot vtxuse=vtx_coords.bin --vtx-coords 2 --slot eot=program, the fault word and address from the kernel journal), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, equal in the ten scripts), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-1140 (sha256 bd55ffe69cf310f574f019ac3cbe3cccf0464d2e2addf0e47f940570440ffa76), debugfs reset, kpoke, hold_recovery and render_pb_pages only (no kreg, no kregnow, no clock-gate register written), run-all-1141ta.sh: 157 jobs in ten tables run in one pass (ten scripts, rc 0 each; the exit=1 at the end of the log is the runner's last test, not a failure), one process per job, a marker per job in the kernel log (157 of 157, in case order), every raw output and dump gzipped with its raw sha256 (741 files, every one equal to the sha256 printed at the run); predictions-declared.tsv (sha256 0641f37b18588b3da43d5cca8a6465221b0d634f23b636e495b10e6426d12b12) and the 82-file manifest (sha256 0817d98ea3d381aea4cf0e8135a09dfbe80da150a765ef762a6c06d100d6bc84) frozen before the first job (freeze1141ta.sh verify: files verified after the run); scored by analysis/post_1141ta.py (standard library, written after the run, not frozen) because the frozen recompute_1141ta.py cannot read the capacity dumps (it looks for NAME.param.bin.gz, the tool wrote NAME.<program>.param.bin.gz) nor the o4 rows (it reads `row N:` at line start, the tool prints `probe pix_pa0: row N:`); the frozen scorer also scored the two dpm-oom jobs that did not run (oom-1400-0x422 and oom-1300-0x422, refused by the tool, rc 2) as passes, which post_1141ta.py counts as void, and the reader of the eot-store table was replaced as well (a text regex became the job's rc; it gives the same 6, 8 and 4 of 10); the frozen predictions and scripts are unchanged (freeze1141ta.sh verify); plan.md is not in the 82-file manifest and was written (14:07:55) after it (14:06:18), so its criteria are attested by file times only, as is the freeze as a whole (local file times and the run log's clock, no external stamp); the output of post_1141ta.py is kept beside it"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vdm-verification-1141ta"]
terms = []
+++
**What ran.** E572's second form (a store between the two emits of the end-of-tile task, r1 as the
address) against three factors, as a 2 x 2 x 2: the flag of the `mov` that makes the address
(`.skipinv` or plain), the position (between the emits, or before the first), the pixel task's
temporaries (32 or 8), plus E130's form (r4, plain, before, 8 temporaries) and the plain end-of-tile
task as controls. Each program has one store of r2 to its own offset of the scratch (0x5CAF0010,
0x20, ... 0x90: the marker), `idf` and `wdf` after it. The two 'before' (pre) cells put `mov r1,
address` ahead of the first emit, and the emit reads r1 as the PBE word 1 (the host patches r0 to r3
with the PBE words): in those cells the position is confounded with a changed emit word, a flaw of
the design that the frozen predictions did not allow for. The cell (skip, between, 32) is the text
of E572's eotst-e1 program: compared byte for byte (usse-asm output, 88 bytes) it differs only in
the address immediate. It was frozen as the control that must fault; all three models predicted it
(HS: every skipinv program, HP: every between-the-emits one, HT: every 32-temporary one).

**Results.** [HW] Faults: eots-skip-mid-t8 and eots-skip-pre-t8 (rc 3 `job faulted, context lost`,
`BIF fault 0xd0400 at 0x1 (PD ...) stalls job N, recovering`; the stored 0x001f8000 landed at the
program's offset). Completed (8): all four 32-temporary programs, the plain 8-temporary pair, E130's
form and the plain end-of-tile task; their stores landed (0x001f8000 for skipinv, 0x5d6f8b86 with 32
temporaries and 0x1137003e with 8 for a plain `mov`: the register r2 holds different values). Some
listings hold a word that is not the job's own (eots-skip-pre-t32 0x5d6f8b86 at +0x20, the offset of
the previous job's store; eots-skip-pre-t8 0xa0a1a2a3 at +0x60, where the previous job's store was
0x1137003e): unexplained, so only the word at the job's own offset is read. Scores: HS 8 of 10
(missed the control and skip-pre-t32), HP 6 of 10, HT 4 of 10; the three missed the control. A fit
after the run, not frozen and with 3 factors on 10 jobs: the fault happens iff the `mov` is skipinv
and the temporaries are 8.

**What it shows.** [HW] A program equal to E572's eotst-e1 but for the address immediate completes
with this kernel module (B21FDA82) and tool (1140), where E572 ran its three single-store programs
(this one and two of g43) on module 5AD04F33 and tool 1126 and saw 3 of 3 fault at 0x340042 or
0x340043 (44 of 44 with its other stores). E572's fault is not reproduced; the data do not say why.
What differs between the two runs, none of it tested here: the address immediate (the first
candidate: E572's fault words were page-like, 0x340042 and 0x340043, the kind of value an address
immediate would change); the module (5AD04F33 against B21FDA82); the tool (1126 against 1140); the
earlier jobs of the script (E572's followed other faulting jobs); the memory the stores landed in.
No run was made on the old module or tool, so nothing here attributes the difference to the kernel
or the tool. The 0x1 faults of the 8-temporary skipinv programs are a different
fault from E572's (an address of 1 for the store's 0x5CAF0050, rather than a page address of the
0x34 or 0x74 kind). Whether the 0x1 fault is the store's or an emit's (the pre cell of the pair has
the changed emit word above), and whether it stays with the two factors, is not shown (two jobs, no
repeat).

**Not shown.** Why E572's faults are not seen here; the program with E572's own address immediate; a
run on the old module or tool; a repeat of the 2 faults (two jobs, two programs: the fit 'the fault
happens iff the `mov` is skipinv and the temporaries are 8' is three factors on 10 jobs, after the
run); E572's 11 and 10 stores between the emits (not run). The premise of Q183 (a `stad` in the
end-of-tile task faults) is therefore open (Q274).
