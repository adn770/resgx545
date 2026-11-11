+++
id = "E837"
claim = "R4 stage e3p, the status bits (r4-events, the same two jobs as E836; Q166, Q111): in b0 (the fill without the skip, control) CR_EVENT_STATUS read 0x20000000 in 9 of 9 watch reads from the slot 3 entry to 54 ms (bit 18 never set) and STATUS2 0x400; in b1p (slot 3's end-of-render pass skipped once, the watch started when the page showed the slot 3 entry, 4.76 ms after the fill began) CR_EVENT_STATUS read 0x20040000, PIXELBE_END_RENDER (bit 18) set, in 7 of 7 reads from 0.01 to 54.5 ms, STATUS2 0x400 throughout; after the tick had stopped, a host write of bit 15 (0x8000) to CR_EVENT_HOST_CLEAR (0x0134, debugfs kregnow) left bit 18 set at 1 and 3 ms, and a write of bit 18 (0x40000) cleared it, 0x20000000 at 1, 3 and 20 ms; frozen verdict 'H-LEVEL consistent (1 row groups), H-PULSE REFUTED; H-W consistent (2 row groups), H-ALL REFUTED, H-NONE REFUTED' on one B1P job (H-LEVEL held out, the clears a fit to E823's one job), the two replicates not run"
unit = "platform"
method = "R4 session r4-events stage e3p (round 4, decision 9), dataset edm-closing-r4-events, attempt out/a1, the jobs, task, module and firmware of E836 (run 2026-11-11 20:56:46 Mac time; the stage ended by its stop rule at b1p, the lead did not resume, so b1p-r2 and b1p-r3 did not run); per job, from the moment a bounded wait (2 ms steps, at most 4 s) saw the slot 3 entry in the page (E823's first read had come before the render's end and voided its rows), CR_EVENT_STATUS and CR_EVENT_STATUS2 read through the debugfs regs file as fast as it reads for 50 ms (9 reads in b0, 7 in b1p, about 7 to 13 ms apart); in b1p, after the tick check and the stop's signature, the host's CLEAR by debugfs kregnow 0x0134= bit 15, the status read 1 and 3 ms after it, then bit 18, the status read 1, 3 and 20 ms after it (no bit 29, no CLEAR2, no firmware str); predictions frozen in predictions/e3p.tsv before the run (bit18_in_watch held out; bit18_after_bit15 and bit18_after_bit18 labelled fit, after E823's one job; replicates for both); scored by the frozen score/score_r4e.py e3p (out/a1/score-e3p.txt, scorekit from resgx545 5a13042), re-run on the kept files on 2026-11-11 with byte-identical output; the status words of the watch and the clears are the kept records' (out/a1/e3p/b0.json and b1p.json, watch and clears)"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["edm-closing-r4-events:out/a1/e3p/"]
terms = ["CR_EVENT_HOST_CLEAR", "CR_EVENT_STATUS", "CR_EVENT_STATUS.PIXELBE_END_RENDER"]
+++
**What ran.** E823 read, post hoc in one stopped job, `CR_EVENT_STATUS` bit 18 held from 7.3 ms
to the end of a 50 ms watch with slot 3's end-of-render handler skipped, cleared by a host write of
bit 18 to `CR_EVENT_HOST_CLEAR` and not by one of bit 15; its frozen rows were cannot tell
because the first watch read came before the render ended. Stage e3p starts the watch at the slot
3 entry and freezes H-LEVEL (bit 18 set in every watch read until acknowledged) against H-PULSE
(never read set), and for the clears H-W (the bits written are cleared: bit 15 leaves bit 18, bit
18 clears it), H-ALL (any write clears: bit 15 clears it) and H-NONE (no write clears it). E823's
job is the fit for the clears; the replicates were to test them held out.

**Frozen verdict (as printed).** From `SUMMARY: e3p: ...; H-LEVEL consistent (1 row groups),
H-PULSE REFUTED; H-W consistent (2 row groups), H-ALL REFUTED, H-NONE REFUTED; ... Q166/Q111 rows:
fit: 4 held, 2 FAILED, 0 cannot tell/void; refuted ['H-ALL', 'H-NONE']; held out: 4 held, 2
FAILED, 0 cannot tell/void; refuted ['H-PHAS-ANY (...)', 'H-PULSE']; control: 10 held, 0 FAILED,
0 cannot tell/void` (out/a1/score-e3p.txt; the H-PHAS-ANY rows are E836's).

**Results [HW].** `CR_EVENT_STATUS` / `CR_EVENT_STATUS2`, ms from the slot 3 entry seen:

| job | watch reads | after bit 15 to 0x0134 | after bit 18 to 0x0134 |
|---|---|---|---|
| b0 | 0.01, 6.92, ..., 54.20 ms: 0x20000000 / 0x400 (9 of 9) | not written | not written |
| b1p | 0.01, 13.33, ..., 54.46 ms: 0x20040000 / 0x400 (7 of 7) | 1 ms 0x20040000, 3 ms 0x20040000 | 1, 3 and 20 ms 0x20000000 |

In b1p the tick had stopped (E836): the writes came after the stop's signature, about 2.2 s into
the job, and bit 18 was still set at the stop's signature (0x20040000).
STATUS2 read 0x400 (`DCU_INVAL_COMPLETE`, idle) in every read of both jobs; bit 29 (`TIMER`) was set
in every read.

**What it shows.** With slot 3's end-of-render handler skipped, bit 18 is set from the first read
after the slot 3 entry to the end of the watch and is still set about two seconds later: a level
that stays until it is cleared (H-LEVEL, held out, 1 job; with E823 two jobs, the first ended
`idf, wdf, nop.end` and stopped at once, this one with the phase end). A host write of bit 18 to
`CR_EVENT_HOST_CLEAR` clears it and a write of bit 15 does not (H-W, a second job after E823's
fit; H-ALL and H-NONE refuted on it). [infer] In ordinary jobs the 4 to 6 us pulses of bit 18
(E547) are the closed handler's acknowledgement through this register.

**What it does not show.** The held-out replicates of the clears (b1p-r2 and b1p-r3 did not run),
so H-W for `CR_EVENT_HOST_CLEAR` rests on two jobs, one fit and one labelled fit here, both on a
stopped EDM; bits other than 15 and 18 (Q166); whether a write of bit 18 alone clears others that
are set (none other than 29 and 18 was set); the other bits' level or pulse (Q111).
