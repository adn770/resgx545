+++
id = "E538"
claim = "With pa1 bit 25 masked in the test of four entry stubs (one per PDS #13 slot, each logging pa0, pa1 and pa2 when pa1 & 0xfdffffff is non-zero and then taking its own tail call), one GETMISCINFO kick with no job reached the general slot only (slot 0: hits flag 1; the other three slots' 12 log dwords 0) with pa0 = 2, pa1 = 0x03000000 and pa2 = 0x01061a70 in 3 of 3 runs, and a window of 50 ms of ticks before the kick logged nothing in any slot (3 of 3 windows, about 150 ticks in all); the frozen prediction pa1 & 0xfdffffff = 0x100 (E155's reversed status bit 14) failed (it is 0x01000000) and so did its falsifier 0x4000 (E146's reading)"
unit = "edm"
method = "as E531: asm/fwtask/events_m.s (68 instructions, blob sha256 9b9ddac0182b...fe194; all four slots armed with own_arm slots=0xf entry=0,1,2,3, the closed tasks 6, 1434, 2766 and 3594 taken from the replaced records; each stub loads pa0, pa1 and pa2, tests pa1 and 0xfdffffff with and.testtanz, and when non-zero stores the hits flag, pa0, the raw pa1 and pa2 of its slot to the log, idf, wdf, then its tail call); run by tools/fwtask/run_stage.py stage q033q1, tool sha256 54eb8909...e56e: the host cleared the log, waited 50 ms and read it (the quiet log), cleared it again and ran one GETMISCINFO (debugfs; answered after 211, 213 and 214 us), and read the log 50 ms later; predictions Q033_q1m and Q033_quiet frozen before stage B (predictions-1130.toml sha256 d8c677cd...27197). Runs p1130-c-events, p1130-c2-events and p1130-c3-events (the same stage under three names, one kick each, 22:36:41, 22:36:56 and 22:36:59; each reloaded and booted the armed image; the kernel log of the third holds two boots, the second run's first and its own); after each, the status registers were healthy and the tick advancing (the kick runs ran no fill or triangle gate). A firmware task, not a client pixel task. The module and its verifier as E536 (the fixed verifier was not used; it accepts events_m.s)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["firmware-tasks-kick-event-words", "vectors-usse-fwtask-p1130"]
terms = ["Event Data Master (EDM)", "CR_EVENT_OTHER_PDS_EXEC"]
+++

**Results.** [HW] In every run the log held slot 0 = [1, 0x2, 0x03000000, 0x01061a70] and nothing
else (the 12 dwords of the other slots 0). The quiet logs (ticks only) were all 0. pa2 is
0x01061a70 for the kick too, the same value as the two ticks of E532: 5 of 5 events (2 ticks, 3
kicks), in five boots. The three kicks were answered after 211, 213 and 214 us, the tick rate at the
arming 967.5, 974.1 and 999.3 Hz.

**Predictions.** Q033_quiet held (3 of 3 windows). Q033_q1m **failed**: pa1 with bit 25 masked is
0x01000000, not 0x100 or 0x4000 (the slot, 0, was as predicted). The kick differs from a tick by
bit 24 of pa1 (0x03000000 against E532's 0x02000000, which was read in other runs), a bit outside
the 24 bits PDS #13 reads (E146), so the slot does not depend on it [infer]. The quiet window
shows that no tick in it had a bit of pa1 other than 25 set (the stubs log only when one is); it
does not show that every tick has bit 25, because the stubs mask it.

**Not shown.** Events other than the kick and the tick (TA finished, end of render: Q033's Q2 needs
a job and was not run; stage E was the last stage that ran), what bits 24 and 25 mean (Q157, Q153),
whether a tick ever lacks bit 25, and whether pa2 moves with anything (Q157).
