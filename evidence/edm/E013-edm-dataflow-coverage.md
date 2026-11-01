+++
id = "E013"
claim = "A forward dataflow over the whole EDM microkernel reaches all 6637 instructions in 70 routines from 13 entry points and 21 further roots, and records every structure word (170) it reaches through a typed pointer, register (191) and secondary attribute (20) it touches; 299 branches, 554 memory accesses, 14 register addresses and 204 sources it cannot resolve are counted, not guessed"
unit = "edm"
method = "harness/ukernel-extract/edm_dataflow.py run as the table probes/firmware/edm-dataflow.toml on the microkernel cut from the user's firmware (dataset firmware-images), with the handler labels make_r2.sh derives from the captured boot payload; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "CAP"]
date = "2026-10-31"
data = ["firmware-edm-dataflow", "firmware-images", "firmware-init-payload"]
terms = ["host_ctl", "kernel_ccb"]
+++

**What ran.** Our disassembler's listing of the microkernel, split into routines at the labels
(the kernel CCB handlers of E012 and the hand-written labels), analysed forward from
instruction 0, every label with no static predecessor and then any code still unreached.
Values are constants, pointers typed by structure, values that came from a structure word,
a register or a secondary attribute (with the transforms applied since), or unknown; where
paths join and disagree the value becomes unknown. A pointer is typed where a record
establishes the word (TA3DCtl's kernel CCB and HWPerf words, E002; the transfer context's
client CCB, CCB control and queue links, doc/specs/transfer.md §2.2 and E015), by the
kernel-side layouts of the GPL kernel module, or by what the firmware itself stores in a slot.
The structures only the client builds (the TA command and what it points at) have no layout
here, so the words reached through them count as unresolved accesses. The result is a table
of indices, offsets, masks and register numbers (resgx545-data
`firmware/edm-dataflow/edm_dataflow.tsv`); doc/specs/edm_dataflow.md renders it with the
glossary's names.

**Coverage.** 6637 of 6637 instructions reached, 70 of 70 routines, 13 entry points plus 21
roots for code no path reaches; 170 structure words, 191 registers (as many as E010's register
reach finds) and 20 secondary attributes. Unresolved: 299 branches, 554 memory
accesses through a base of unknown origin, 14 register-supplied register addresses, 204
sources.

**What it shows and what it does not.** Which words and registers the firmware reads and
writes, from where and under which tests, for every path. It does not show timing, values
that arrive at run time, or what the unresolved accesses reach; E015 states the transfer
part, checked against the runs on the laptop.
