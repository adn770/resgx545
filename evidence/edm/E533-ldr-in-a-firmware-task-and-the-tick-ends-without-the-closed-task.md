+++
id = "E533"
claim = "ldr in a firmware task of our own reads the registers as the host does (CORE_ID 0x01150000 and CORE_REVISION 0x0001000d in 2 of 2 runs, and CR_TIMER a count that is not the initial fill value 0xdeadc0de: 0xc782bb2b and 0xd5cd8747), and, after a general-slot task of ours that wrote sa64, sa100, sa127, sa20, sa24, r20, r21, i0, i1, p0 to p3 and pclink and ended with nop.end, without jumping to the closed task, the EDM's tick stopped: in the one run of item 12 (stage 8, stopped on its own trigger) HostCtl dword 12 stayed at 1190 and USE0_SERV_EVENT at 1195 over three reads 20 ms apart, the command the task had armed for the next event never ran (the task both skipped the closed task and wrote many registers in that one run, so which of them stopped the tick is not separated), and one debugfs reset rebuilt the stock firmware, which ticked at 967.1 Hz after the reset and passed the stock gate (0 of 2048 and 0 of 4096 pixels differing, 971.6 Hz)"
unit = "edm"
method = "as E531 (srcversion 7ED723C25D78D7FCB3C08C1, own_arm slots=0x1 entry=0 trc=8): stage 4, asm/fwtask/ldr.s (command 1: ldr of dwords 7, 8 and 81, wdf, stad; 282 bytes), runs p1129-s4-ldr and p1129-s4b-ldr, one command each, run id 41 in both; and stage 8, item 12, asm/fwtask/state.s (786 bytes), run p1129-s12 (arm record, one pair, stop record) and p1129-post-s12-stock. Task 1 (command 1) wrote sa64, sa100, sa127, sa20, sa24, r20, r21, i0, i1, p0 to p3 and pclink, stored the command 2 for the next event and the state flag, and ended with nop.end; the design assumed that the next tick would start our wrapper again. The stage stopped on its own trigger (the tick not advancing in three reads) and the tool kept its pair record (s12-pair1.json, in the data) and the log (kernel.log); its pair-first-regs.txt, -status.txt, -own_res.json and -dmesg.txt were written to the laptop's own output directory, not to the data repository, so they cannot be cited here; one reset followed. The stage was not repeated and none of the persistence cases ran. Data kept as found: p1129-s4-ldr is the first stage 4 run (its files, jsonl, summary and page, agree on one command, and it has no verdict file or kernel log: the tool stopped after the command) and p1129-s4b-ldr the rerun; whether an earlier run of the same name was overwritten cannot be told from the data. A firmware task, not a client pixel task"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["firmware-tasks-ldr-and-persistence"]
terms = ["Event Data Master (EDM)", "CR_EVENT_TIMER"]
+++

**ldr.** [HW] `ldr r, #7` and `#8` returned 0x01150000 and 0x0001000d, the values the host reads
(hw_spec 5.1); `ldr` of `CR_TIMER` (dword 81) returned 0xc782bb2b and 0xd5cd8747 in the two runs (a
count, checked only against 0 and the initial fill value 0xdeadc0de; the host reads during the run
were not bracketed). Only these three registers were read by an `ldr`; the two of E534 were read
there.

**The tick.** [HW] After task 1 (done, command 2 armed) neither `HostCtl` dword 12 nor
`USE0_SERV_EVENT` moved: no event ran. That one task did two things at once: it skipped the closed
general task (it ended with `nop.end`) and it wrote the `sa`, `r`, `i`, `p` and `pclink` registers
above; the run does not separate skipping the closed task from clobbering state the closed task or
the PDS needs, nor from something our command-1 path left undone [infer: the `EVENT_TIMER` write of
E155's tick handler is what the closed task does, which was not run here, and is one candidate]. The
stage's design assumed the next tick would start our wrapper again, so the pair of tasks of item 12
and Q124 was not measured by that design. The recovery was one debugfs reset (the only one in the
kept kernel logs of the phase), `own_arm` back to off, ticks at 967.1 Hz, the stock gate exact,
`BIF_FAULT` 0 and `EVENT_STATUS2` 0x400; the reset's log also holds the line "error state captured
in /sys/class/devcoredump". The stock check after it (p1129-post-s12-stock) is exact at 971.6 Hz.

**Not measured.** What survives between firmware tasks (S1 to S4), `p0` to `p3` and `pclink` (Q124),
whether two tasks overlap (item 11), the largest allocation (item 13), and the event words of a host
kick and of a job (Q033): the stage stopped before any of them. A writer that jumps to the closed
task after its writes, and a task that skips it without writing, are different experiments, not run
here (Q152).
