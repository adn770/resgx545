+++
id = "Q003"
question = "which event (if any) does a bus-interface fault raise, and what do the fault-request bits of CR_BIF_INT_STAT name, and what clears a latched fault in CR_BIF_INT_STAT and CR_BIF_FAULT while leaving the bus usable?"
unit = "transfer"
kind = "hw"
value = "medium"
phase = 4
evidence = ["E021", "E024", "E317", "E318", "E319", "E320", "E354", "E355", "E357", "E444", "E203",
            "E313", "E362", "E363", "E395", "E457", "E476", "E573", "E631", "E722", "E729", "E764",
            "E765", "E766", "E767", "E789", "E826"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT", "misc_info"]
+++

In E021 a fill aimed at a page the context's directory maps read-only writes nothing and never
completes; no SGX interrupt came (the host enables only SW_EVENT, E006). Held without recovery
(E317, E319, one run each) render faults behave the same way: the interrupt counters do not move
and `CR_BIF_INT_STAT` keeps the fault until a reset. Its low bits differ by what faulted: bit 3
for the TA's read of an unmapped stream page (0x90008), bit 10 for the EDM's write to a read-only
page (0x80400, E319; again for the PB builder's write, E362), bits 10 and 16 with 18 for a
background program's fetch at a low address (0xd0400) and bit 13 for one in the pixel PDS heap
(0x92000, E363); bit 5 for E021's transfer write; bit 19 is set when idle.

Narrowed by E357 (one fault sampled from before its kick): the fault raises no bit of
`CR_EVENT_STATUS` or `CR_EVENT_STATUS2` of its own other than `CR_EVENT_STATUS2` bit 7, which sets
right after it, as it does for a TA that hangs without a fault. `CR_BIF_FAULT`'s bits 3:0 name the
faulting directory list (E360).

Narrowed by E444 (debugfs kregnow writes the host enables while a fault is held, 14 held faults of
three kinds): the bits that follow a TA read fault and a background-program fetch fault,
`CR_EVENT_STATUS2` bits 7 (`TRIG_TA`) and 6 (`TRIG_3D`), are host events (alone they raise the host
interrupt once enabled), but bit 7 is the TA trigger's and not the fault's alone (E357); the EDM's
write fault sets none. `CR_EVENT_STATUS` bit 29 (`TIMER`) and `CR_EVENT_STATUS2` bit 10
(`DCU_INVAL_COMPLETE`), set when idle, are host events too. The EDM's write to a read-only page
leaves the status registers as they are idle.

Open: which requester each of bits 15:0 of `CR_BIF_INT_STAT` names beyond those seen; bits 16 and
18; whether a fault of another unit (the 3D's own fetches, the texture unit, a transfer) sets
another status bit; what raises bits 7 and 6 of `CR_EVENT_STATUS2` besides a hang.

Known from the former Q028 (E024, E317-E319, E354, E355): on a fault the kernel stops and resets
the core, boots the firmware again in place and later jobs run exactly (E024). Held without
recovery (debugfs `hold_recovery`), a faulted job leaves the fault in `CR_BIF_INT_STAT`, and a
faulted or hung job wedges the EDM: GETMISCINFO is not answered, other contexts' jobs do not run and
the tick's count stays still (E317-E319); that the stall is the EDM's task waiting on the faulted
bus is a reading of the still count (E317) [infer]. A debugfs reset written while the hold is set
recovers the held job with blame, once, the held job failing with its detector's error and not
running again (E354), and a cleanup that fails while held keeps the hold (E355).

Open, from the former Q028: which part of the reset a latched fault needs to clear
`CR_BIF_INT_STAT` and `CR_BIF_FAULT` (the core reset alone, with the bus interface's registers
rewritten, or the firmware boot after it), and what leaves the bus wedged for another context's
jobs, seen through the registers alone: `CR_BIF_INT_STAT`, `CR_BIF_FAULT`, `CR_BIF_CTRL` and the
status registers before and after each step. Which steps the kernel's recovery should take is the
kernel's design and is not the target.

To settle it: the same enables over faults of the other requesters (a transfer to a read-only page,
a texture fetch from an unmapped page, a 3D store to one), the status registers read and the
interrupts counted for each; and, after a held fault, the debugfs register writes one reset step at
a time (kregnow) with the bus interface's registers read after each and a job on another context
after the last.

Folded in 11.21: Q028 is retired into this question, which is not an answer to it. Q111 holds the
other event sources and what sets each status bit.

Requestor table, 2026-11-09 (a compilation of the words the records already hold, not a new
measurement; `FAULT_REQ` is bits 15:0 and `FAULT_TYPE` bits 18:16, glossary G0772 and G0773). The
word is `CR_BIF_INT_STAT` at the fault, type is bits 18:16, req the bit set in 15:0:

| word | type | req bit | what faulted | record |
|---|---|---|---|---|
| 0x80020 | 0 | 5 | a transfer's pixel write to a read-only page | E021, E024 |
| 0x90020 | 1 | 5 | a transfer job (3 of E024's 4 faults; which was which is in E024) | E024 |
| 0x90002 | 1 | 1 | a texture fetch past the probe's scratch [infer] | E722 |
| 0x90004 | 1 | 2 | a render's access past the end of the TA data | E203, E313, E729 |
| 0x90008 | 1 | 3 | the TA's read of an unmapped stream page | E317, E318, E444 |
| 0x80400 | 0 | 10 | the EDM's write to a read-only page | E319, E362, E457 |
| 0x90400 | 1 | 10 | buffers 6 to 11 left out; a partial owner closed unkept | E457, E631 |
| 0xd0400 | 5 | 10 | a background program's fetch at a low address | E363 |
| 0x91000 | 1 | 12 | buffer 0 (0x30000000) left out; a placed program's `lapc` | E573, E476 |
| 0xd1000 | 5 | 12 | every buffer id left out (0xffff) | E457 |
| 0x92000 | 1 | 13 | a PDS program's fetch in the pixel PDS heap | E363 |
| 0xd2000 | 5 | 13 | PDS store faults | E395 |

Bits seen in 15:0 are 1, 2, 3, 5, 10, 12 and 13; not seen are 0, 4, 6 to 9, 11, 14 and 15. Type 0
appears with a write to a read-only page and type 1 with an unmapped page [infer]; type 5 (bits 18
and 16) appeared with a fetch of the background program at a low address, a PDS store, and the
case where every buffer id was left out. Bit 19 is set in every word and when idle. The words name
the requestor of the faulting access, not a list or a context; the table does not say which bit a
fault of the 3D's own fetches or of the ZLS would set, since none has faulted. The rows marked
[infer] carry the reading of the record's author, not a separate test of the bit. The question
stays open: bits 16 and 18 beyond the types, the unseen requestors, and what clears a latched
fault.

Note 2026-11-10 (a reading of the published kernel logs, not a new measurement). The requestor table
above says that bits 0, 4, 6 to 9, 11, 14 and 15 of FAULT_REQ were never seen. The kernel logs of
resgx545-data hold BIF fault words with bit 7: 0x90080 (ta/points, usse/output-room-rd,
render/hold-fault) and 0xd0080 (usse/output-room-rd); bit 8: 0x90100 (ta/mtile-fields,
ta/mtile-fields-risky, ta/te-psg, ta/te-words-repeat); bit 9: 0x90200 (zls/control-bits); and type-5
forms with bit 1, 0xd0002 (texture/sampler-bits), and bit 3, 0xd0008 (usse/output-room-vdm, S1's
g-e4 and S1b's g-e4w, the last two from a bit-25 index list header, E737, E756). So bits 7, 8 and 9
are seen. Which requestor each names is not established (the log line carries the word and the
address), and the statement that no ZLS access has faulted rests on zls/control-bits, whose jobs
faulted at 0x90200 with bits of the ZLS control word set (E411's data) and are not identified as a
ZLS fetch. Bits 0, 4, 6, 11, 14 and 15 are still not seen.

Narrowed in S3 (2026-11-10, laptop session S3 of the question-closing pass, dataset
render-closing-s3; one run each). Frozen verdict: `Q003 E1: partly: e1-tex HE, e1-xfer-ro HE, a6
(TA write) had no data` (a6 never ran). The two E444 controls reproduce word for word (E764), which
opened the gates. A held texture fault, S1's 16-page L2e2 job, reads `CR_BIF_INT_STAT` 0x90002 and
`CR_BIF_FAULT` 0x3e017001 and `CR_EVENT_STATUS` 0x20000000 with `CR_EVENT_STATUS2` 0x440 at 2.8 s
and 3.8 s, clear after the debugfs reset (E765); the transfer's write fault of E021 (debugfs
`xfer_ro`, no hold needed) reads 0x80020 and 0x32200001, writes nothing, and the same status 0x440
(E766). Neither fault raises a status bit of its own (the frozen HE), unlike the EDM's write fault,
which leaves 0x400 (E444). So of "whether a fault of another unit sets another status bit", the
texture unit's fetch and a transfer's write are answered: bit 6 and no other, no bit 7. Not
answered: the 3D's own stores, the ZLS, a held TA-write fault (a5 and a6 did not run), and the
type-1 transfer fault (0x90020).

Post hoc, from the timeline rows (not frozen, nothing was predicted): in the three held render
faults and the transfer's, `CR_EVENT_STATUS2` bit 7 (TA read) or bit 6 (background fetch, texture
fetch, transfer write) sets 121.1 to 124.1 us after the fault word appears, with `CR_EVENT_STATUS2`
0x400 in between (sampling about every 4.3 us), so the bit follows the fault and is not raised with
it (E764, E765, E766). What sets it, hardware or the firmware's reaction, is open, and bears on
Q082. Also post hoc and [infer]: at the kernel's reset of each of three held render faults
`CR_BIF_INT_STAT` and `CR_BIF_FAULT` read clear (0x80000 and 0) in the first row of the reset,
6.8 to 11.3 ms before the status registers are host cleared and before the kernel writes the clear
bit of `CR_BIF_CTRL` (E767); the kernel's order is halt (deinit script and soft reset), then the
clears. That reads as the halt leaving the fault reading zero, a lead for "what clears a latched
fault"; whether the latch is cleared or only reads zero while the block is in reset, and whether the
clear bit alone clears it without the halt (a kernel change), is not shown. Status: narrowed.

Note 2026-11-10 (a reading of the published kernel logs, made before the round 2 runs; not a new
measurement; it adds names to the seen-bits note above and changes no table row). [infer] The
requestor of bit 7 (words 0x90080 and 0xd0080) is the ISP's fetch of the background object or
primitive block: the page of the fault moves with a kpoke of the descriptor that locates the
background object (rd:18, `0x04c4`) by the bit moved shifted by 4, in the PARAMETERS range
0x10465 to 0x10664 and the GENERAL page 0x3e000. Bit 8 (0x90100) is the TE's parameter-buffer
access: 204 of 204 faults at PARAMETERS page 0x10000, with the TE descriptor pokes (ta:143
`CR_TE_MTILE1`, ta:147 `CR_TE_PSG`). Bit 9 (0x90200) is the ZLS load or store: faults at six
GENERAL pages (0x3e016, 017, 01e, 02e, 04e, 08e) that move with the control bits' rd:11 poke
(bits 5 to 11, the page doubling with the bit). These readings rest on the address and the poke
alone and no job whose requestor is known by another route has been run. Type 5 (bits 18 and 16),
seen with bits 1, 3, 7, 10, 12 and 13, appears whenever the faulting address is far outside the
mapped slot, so it reads as an address outside the directory's range, and type 1 as an unmapped
page within it. Bits 0, 4, 6, 11, 14 and 15 are still not seen. After the faults of bits 7 and 9
the status reads 0x440, and after bit 8 0x400 or 0x440 (129 of 204 left idle status with the TE
faults). Both the type and the names are [infer] and the question stays open.

Narrowed 2026-11-10 (R2-pixel, E789; the TA-write row of the S3 note above, held out, one run).
The held 4x job a6 (320 x 400 at `CR_TE_AA` 0xe0000000 in a context made for 320 x 400) faulted with
`CR_BIF_INT_STAT` 0x90004 and `CR_BIF_FAULT` 0x20008061, the page the layout model gave, and read
`CR_EVENT_STATUS` 0x20000000 and `CR_EVENT_STATUS2` 0x480: no status bit of its own beyond the
bit 7 a TA fault leaves (the frozen HE, extra bits none; HF refuted), a control passing. So of
"whether a fault of another unit sets another status bit" the TA's write joins the texture unit's
fetch and a transfer's write (E765, E766): none of the three leaves a bit of its own. Still not
answered: the 3D's own stores, the ZLS, the type-1 transfer fault (0x90020), which requestor each
bit names (the names above rest on the address alone), and what clears a latched fault (E767).

Narrowed 2026-11-10 (K2 stage k-bif, E826; not retired; frozen verdict cannot tell, 4 of 4 held rows
OTHER, n0 passed). On held faults of three requesters (TA read twice, TA write, texture fetch) a
write of the fault's set bits to `CR_BIF_INT_STAT` changed nothing (4 of 4); setting `CR_BIF_CTRL`
bit 4 made the registers read clear at the kernel's read after the write (4 of 4) and, in the
runner's later snapshots, both clear in 2 rows and one of them clear in 2; clearing the bit again
brought both back (4 of 4); the registers stayed latched through a 2.5 s watch and the reset cleared
them (both reset lines 0x80000 and 0, E767's lead held). So no hypothesis fits (H-W1C, H-CLR, H-RST
each contradicted by one reading). Open: whether a clear lasts with the requester no longer stalled,
the order inside the reset, the 3D's own and ZLS faults, the type-1 transfer fault.

Note 2026-11-11 (round 4, decision R4-3: Q140's health-triangle clause goes here; a reading of kept
kernel logs and of K2's netconsole log, not a new measurement; [infer], one boot for the replay).
After a 0x90004 fault (requestor bit 2, the TA's write: a render's access past the end of the TA
data, and the 1x DPM context faults `dpm/ctx-table-*` at 0x10000051) the state is not clean:
"SGX recovery failed: -110" (the EDM boot's "no INIT_COMPLETE after 500 ms", then a register dump
and -ETIMEDOUT) follows a 0x90004 fault 51 times of 157 over 543 kernel logs of resgx545-data and
follows none of the other fault words (0x90002, 0x90008, 0x90080, 0x90100, 0x90200, 0x90400, 0x91000,
0x92000, 0xd0002 to 0xd2000, 0x80400: about 1180 faults; closing4/rank/faultseq.out). In K2 the
failing health triangles faulted at the previous job's address: 0x20006061 twice after c1 and
0x20008061 twice after k-bif f2 (4 of 4), a page the health triangle's own layout does not reach
even with four arrays, and after k-bif's f1, f1r (0x90008), f3 (0x90002) and R3-rgn4's j4 (0x90100)
the next health triangle passed. The -110 dumps of K2 (BIF_INT_STAT 0x000d0004, BIF_FAULT
0x1000b050 then 0x10002050: requestor bit 2, `SB` 5, a page of the PARAMETERS heap, `CID` 0) show a
fault inside the boot itself. [infer] A pending TA region-header write survives the soft reset and
is issued again when the TA next runs, through whatever directory is then current; the -110 is the
same state seen by the boot. This bears on "what clears a latched fault" (E767, E826: the reset
leaves the fault registers reading zero while a TA write is still pending). Not explained: why two
replays in K2 and one on R3-rgn4's boot, and what ends them. Refuted by: a health fault at the
health context's own first unmapped page after a job that faulted elsewhere, or a -110 after a
fault word other than 0x90004.
