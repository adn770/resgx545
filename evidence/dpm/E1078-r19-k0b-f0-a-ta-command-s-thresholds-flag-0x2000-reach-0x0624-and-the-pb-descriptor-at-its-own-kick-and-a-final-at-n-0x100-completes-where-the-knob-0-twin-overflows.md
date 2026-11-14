+++
id = "E1078"
claim = "r19-k0b stage f0 on module E0CC40275493F8AEAD8180B (12 jobs on t18b: a geometry kick at P, the closing render on its own PB of N pages through render_final_pb_pages, whose TA command carries flag 0x2000 and N's thresholds in dwords 10 to 13): the four controls passed (0x0624 after the job N - 0x22: 0x1de at P 0x422 N 0x200, 0xde at P 0x28 N 0x100, the latter's kick overflowing); the EDM applies the command's thresholds at that kick: in every row 0x0624 takes N - 0x22 at the closing render's kick, before it ends, and the PB descriptor's dwords 10 to 13 read (list + 0x10, N - 0x22, N - 0x22, PDS) after it (H-STORE 12 of 12, H-NOSTORE 0 of 12, H-IGN 14 of 26); the next scene's first job puts P's back (f0-back: render 3 at 0x6 overflows, H-STICK 0 of 4); H-UPD held 48 of 52, its 4 misses f0-down's predicted overflow at N 0x30 (0x0624 0xe with 19 pages held: the closing render took no new page, so no abort was due); H-LATE's 26 of 26 are values it shares with H-UPD, and post hoc its claim that the render follows P fails: the knob-0 twin (E1077's kg, P 0x28) overflows in the closing render, the same render at N 0x100 does not; the longer list leaves the geometry kick as it was (H-GEO0 1 of 1)"
unit = "dpm"
method = "r19-k0b (render/closing-r19-k0b), stage f0 of round 19's S1 (cited/closing19/DECISIONS-R19.md, R19-1 a and R19-2 a: f0-down medium, last, soft; cited/closing19/plan/rank-round19.md section 2b), built on the session kit (resgx545 main 50606dc, data 95df71e98), frozen before the run (FROZEN.sha256 b0977a4e8fc32bca1d9996feb35a3e9a2675ba27ca28178f9e250ee27a8dcdf1), dataset render-closing-r19-k0b; attempt out/20261114-224248 (score-f0.txt; gated on k0 and kg, E1077), 2026-11-14 22:45, run by the lead with the kit's driver over the travel cable, on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B, fork 456404fcffe5, stock firmware), tool ~/sgxfive-test-t18b (sha256 58e7985504d0d3311155d94627da8b8473335d9a843f5610e44731864315b21e, resgx545 ec50498, recipe lead/build_tool18b.sh) under ~/regtimeline (079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803) over r13-dpm's registers and 0x0620, 0x0668: tri --width 1024 --height 768 -n 2 (f0-back -n 3) --geometry 1 --final-pb-pages N --keep-going --keep-overflow --wait-ms 20000 --dump-render --dump-each --words --regs 0x0600-0x0750, P by debugfs render_pb_pages (restored to 0x422), the tool writing render_final_pb_pages itself (declared at 0, read back 0 after each job), cells (P, N): f0-same (0x422, 0x200) and f0-up (0x28, 0x100) twice each as controls, f0-up-h1 (0x30, 0x60), f0-up-h2 (0x24, 0x422), f0-back (0x28, 0x100, a third render opening a new scene) and f0-down (0x100, 0x30, last, soft, the plan's 0x28 moved to 0x30 for the library mock's overflow rule) twice each, held out; the module's dmesg line 'render context: PB P, final kicks' PB N, list max(P, N) pages' at each row. No stop, fault or hang; the frozen scorer re-run on the kept files is byte-identical (fold/score-f0.txt). Post hoc (after the score was read): fold/timeline.py and fold/timeline.out (when 0x0624 takes N - 0x22 and the pages after it), and the comparison with E1077's kg rows (fold/NOTES.md)"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r19-k0b:out/20261114-224248/f0/", "render-closing-r19-k0b:out/20261114-224248/kg/", "render-closing-r19-k0b:fold/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)"]
+++
**What ran.** The kernel of fork 456404fcffe5 gives the render that closes a scene a geometry kick
opened its own PB size N: the context's free list holds max(P, N) pages, and that render's TA
command sets flag 0x2000 with dwords 10 to 13 = (list + 0x10, N - 0x22, N - 0x22, PDS(N)), which
our reading of the EDM (doc/specs/edm_dataflow.md) says it stores into the PB descriptor and loads before
the kick's TA; the next scene's first job sets P's back. Never run before. Frozen: H-UPD (applied
at that kick, the render follows N), H-IGN (ignored), H-LATE (stored, loaded only at a later
kick), H-STORE against H-NOSTORE (the descriptor), H-STICK (N kept into the next scene), H-GEO0
against H-LIST (the longer list changes the geometry kick).

**Frozen verdict (as printed).** `out/20261114-224248/score-f0.txt`: CONTROL f0-same-1, f0-up-1,
f0-same-2, f0-up-2 PASS; "SUMMARY: f0: H-UPD: H-UPD holds is not supported: 48 held, 4 FAILED, 0
cannot tell of 52"; "H-IGN ... 14 held, 12 FAILED"; "SUMMARY: f0: H-LATE: H-LATE holds (26 of 26
rows decided)"; "SUMMARY: f0: H-STORE: H-STORE holds (12 of 12 rows decided)"; "H-NOSTORE ... 0
held, 12 FAILED"; "H-STICK ... 0 held, 4 FAILED"; "SUMMARY: f0: H-GEO0: the longer list leaves the
geometry kick as it was (1 of 1 rows decided)".

**Results [HW].** 0x0624 after the job and pb:10-13 per cell: f0-same 0x1de, (0x432, 0x1de, 0x1de,
0xde); f0-up 0xde, (0x110, 0xde, 0xde, 0); f0-up-h1 0x3e, (0x70, 0x3e, 0x3e, 0); f0-up-h2 0x400,
(0x432, 0x400, 0x400, 0x300); f0-back 0xde after render 2, then 0x6 after render 3; f0-down 0xe,
(0x110, 0xe, 0xe, 0); every replicate the same. The geometry kick overflowed (1 partial render) at
P 0x28, 0x30, 0x24 and not at 0x422, 0x100; no closing render overflowed; f0-back's render 3
overflowed at 0x6 (raised to 0x26 in it, as at P alone). The timeline (fold/timeline.out): 0x0624
takes N - 0x22 at the closing render's kick, with 19 pages held at f0-same and f0-down and 0 to 7
after a partial render, and the page count then peaks at 19 or 20 with no partial render. The
geometry kick of f0-up (list 0x100, TA threshold 0x110) equals E1077's kg kick (list 0x28,
0x38): 0x0624 0x6, overflow, TA3DCtl dwords 35, 37, 38 0x4, 0x10006, 0x20. The 4 H-UPD misses:
f0-down's ovf2 and nparts (frozen: the final overflows), read 0 and 0. Not predicted: f0-up's
closing image is exact (diff 0), not short of the partial render's tiles.

**What it shows.** The thresholds of a TA command with flag 0x2000 reach the DPM at that kick: 0x0624
reads N - 0x22 from the closing render's kick on, not after it (H-LATE's mechanism fails on the
timing), and the EDM writes them into the PB descriptor (H-STORE). They govern that render [infer,
post hoc]: E1077's kg rows, the knob-0 twin of f0-up (the same P 0x28 kick, the same two
triangles), overflow in the closing render at 0x0624 0x6 (raised 0x26), while f0-up's closing
render at 0xde completes. The next scene's first job's command puts P's thresholds back (f0-back).
A threshold below the pages already held does not abort a render that allocates no further page:
f0-down's second triangle is the first's and took no new page (0x0724 stayed 0x13), so f0-down
does not test the abort, and its frozen prediction rested on an assumed 5 more pages [infer].

**What it does not show.** An abort caused by a lowered threshold (f0-down could not show one); the
order of the descriptor store and the register load inside the kick (both are read after it or
sampled at about 8 us); whether the EDM reads dwords 10 to 13 without flag 0x2000 (never set
otherwise); the TA threshold's role (0x0620 not scored); scenes other than this triangle.
