+++
id = "E1046"
claim = "R14-bif stage refill (Q108's stale-data clause; E1029's zb-c-id depth form, 64 x 32, depth test never so the store holds the load, run twice on one context, 6 jobs, every control passed): when the host rewrites the depth buffer between the two renders (tri --refill 2:depth=0x3f400000, after render 1 loaded the buffer's index fill), render 2's ZLS load reads the host's new value in all 2048 stored dwords, with CACHECONSISTENT (PTE flag 0x8) on the depth buffer's mapping and without it; no dword of render 1's load came back; CACHECONSISTENT on the loaded buffer ends clean (no fault) and, with no refill, changes nothing (render 2 stores the index as render 1 did); frozen verdicts 'H-CC-COHERENT (1 of 1 rows decided)', 'H-NC-COHERENT (1 of 1 rows decided)', 'H-CC-NOOP (1 of 1 rows decided)' (H-CC-STALE and H-NC-STALE '0 held, 1 FAILED')"
unit = "bif"
method = "R14-bif stage refill of the question-closing pass, round 14 (decision R14-4 (a) of the round 14 decisions; round 14 plan sections 2 and 3, row 11), dataset render-closing-r14-bif; one attempt out/20261114-055414 (scores score-refill.txt; lead log fold/run-r14b.log; no stop, no lead decision), on the laptop, 2026-11-14 05:54, module srcversion B60AB0B475DD1E8972419B5 (the linux fork at 2a650d74: debugfs vm_pte_addr and vm_pte_flags; installed = loaded, both knobs 0 at the stage start and restored after every row), stock firmware, tool ~/sgxfive-test-t14 (t14, sha256 aa550b94..., built from resgx545 c58f9f9's sgxfive-test.c, sha256 9cef7a20..., TOOLSRC.sha256, by lead/build_tool14.sh: FROZEN.commits' built line; every row replayed on the library mock built from that source before the freeze, none refused), built on the session kit of resgx545 c58f9f9 (kit/run_stage.sh with run/hooks.sh: a debugfs reset before each job, the knobs written and read back before a row and restored after it, the kit's strict health fill and triangle; hook_check found every job line ok, the buffers at 0x3e001000 (base 0x3e000000) and 0x3e015000, the kernel's `vm_map 0x3e001000 +0x14000: PTE flags 0x8` line on each knob row and on no other, and the `refill: render 2 buf depth value 0x3f400000` line on each refill row); frozen before the first job: FROZEN.sha256 9a30d4f74afc814bc792e1379aa475da5aea3e045eed7627a9b3b5ce3892b6e6 (47 files), PREDICTIONS.sha256 8160847a24b9d79dc5ede979863bf7074a48fb5267e5c4efe259aa2dee3ae015, FROZEN.commits (the kit, the tool's source and the replay inputs at resgx545 c58f9f9; E1029's kept zb-c-id and zb-c-off stores and E965's tri-c-depth at data 3309b5fd); scored by the frozen score/score.py, re-run at the fold on the kept files with byte-identical output (fold/reproduce.sh, reproduce.out). Rows (tri -n 2 --keep-going --width 64 --height 32 --tri-full --tri-z 0.5,0.5,0.5 --depth --depth-ctl 0x0017500e --depth-fill index --depth-store --depth-store-fill 0x3e800000 --depth-pages 20 --depth-dump --poke blk:1=0x00000200, t14 filling every buffer again before render 2, then the refill): rf-c-plain (control: E965's knob-free tri --depth --depth-store twice), rf-c-depth (control: no knob, no refill), rf-c-unread (control: CACHECONSISTENT, render 1's control 0x0017100c that loads nothing, render 2's 0x0017500e by --depth-ctl-next, refill), rf-cc-keep (CACHECONSISTENT, no refill), rf-cc-refill (CACHECONSISTENT, refill), rf-nc-refill (refill, no knob); each store dump classed dword by dword (gen/rf.py store_class: F the index render 1 loaded, V the refill, the rest of the buffer the store's fill)"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r14-bif:out/20261114-055414/refill/", "render-closing-r14-bif:fold/", "vectors-closing-r14-bif-pte"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++
**What ran.** Q108 asked whether CACHECONSISTENT changes what a unit sees of data cached before
the host's write. The tool t14 (`tri --refill K:BUF=V`, resgx545 c58f9f9) writes V to every dword
of a buffer after render K - 1 is done and read back, just before render K's kick. Each row ran
E1029's zb-c-id form twice on one context: the depth buffer filled with its index (dword k holds
k) is loaded by the ZLS, the depth test never passes (E467), so the separate store buffer receives
what was loaded. Render 1 loads the index; on a refill row the host then writes 0x3f400000 (0.75)
over the whole depth buffer, and render 2 loads it again. The knob rows put CACHECONSISTENT (PTE
flag 0x8) on the depth buffer's mapping. Frozen: H-CC-COHERENT (flag set: render 2 reads V)
against H-CC-STALE (it reads render 1's index), H-NC-COHERENT against H-NC-STALE without the flag,
and H-CC-NOOP (the flag without a refill: render 2 stores the index); the coherent models were
favoured [infer: the host maps a buffer write-combined].

**Frozen verdict (as printed).**

- `H-CC-COHERENT (1 of 1 rows decided)`; H-CC-STALE `is not supported: 0 held, 1 FAILED, 0
  cannot tell of 1`.
- `H-NC-COHERENT (1 of 1 rows decided)`; H-NC-STALE `is not supported: 0 held, 1 FAILED, 0
  cannot tell of 1`.
- `H-CC-NOOP (1 of 1 rows decided)`.

All three controls passed: rf-c-plain (`tri: 2 renders ok`, 4096 store dwords changed in each
render, as E965's tri-c-depth), rf-c-depth (both renders' stores byte for byte E1029's kept zb-c-id
store), rf-c-unread (render 1's store byte for byte E1029's zb-c-off store, render 2's store V in
all 2048 dwords).

**Results [HW].**

| row | CACHECONSISTENT | refill | job | store 1 | store 2 | depth #2 changed |
|---|---|---|---|---|---|---|
| rf-c-depth | no | no | ok, ok | index (2048) | index (2048) | 0 (against the index) |
| rf-c-unread | yes | yes | ok, ok | 1.0 (2048) | 0x3f400000 (2048) | 0 (against V) |
| rf-cc-keep | yes | no | ok, ok | index | index | 0 |
| rf-cc-refill | yes | yes | ok, ok | index | 0x3f400000 (2048) | 0 |
| rf-nc-refill | no | yes | ok, ok | index | 0x3f400000 (2048) | 0 |

In every depth row the rest of the store buffer (18432 dwords) kept its fill, no BIF fault line
was logged, and both renders drew nothing, as the depth test never makes them (`tri: 0 of 2
renders ok`, the expected diff). The kit's health drew exactly after every row.

**What it shows.** [HW] A ZLS depth load in the second render of a context reads what the host
wrote to the buffer after the first render, whole, with or without CACHECONSISTENT on the
buffer's mapping: no stale copy of the first render's load survived to the second (H-CC-COHERENT,
H-NC-COHERENT). CACHECONSISTENT on a buffer the ZLS loads faults nothing and changes nothing the
store shows (H-CC-NOOP, and E945's "changed nothing" on the GENERAL page held out on a depth load).
So on this path the flag decides nothing that a host write between renders could show [infer:
whatever it changes is not visible at the granularity of a render on a write-combined host
mapping].

**What it does not show.** Data cached within one render (a host write during a render, or a
buffer read twice in one render); a host mapping that is not write-combined (every buffer of the
tool is); other units' reads (the texture read, the TA's and the EDM's) under the flag; WRITEONLY
and EDMPROTECT on a texture read or a depth load, the TA's own writes and the EDM's buffers, which
need faults.
