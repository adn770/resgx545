+++
id = "E013"
claim = "A forward dataflow over the whole EDM microkernel reaches all 6637 instructions in 70 routines from 13 entry points and 21 further roots, and records every structure word (346) it reaches through a typed pointer, register (191) and secondary attribute (20) it touches; 249 branches, 379 memory accesses, 14 register addresses and 109 sources it cannot resolve are counted, not guessed"
unit = "edm"
method = "harness/ukernel-extract/edm_dataflow.py run as the table probes/firmware/edm-dataflow-11.toml on the microkernel cut from the user's firmware (dataset firmware-images), with the handler labels make_r2.sh derives from the captured boot payload; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "CAP"]
date = "2026-11-02"
data = ["firmware-edm-dataflow-11", "firmware-edm-dataflow-3d", "firmware-images", "firmware-init-payload"]
terms = ["host_ctl", "kernel_ccb"]
+++

**What ran.** Our disassembler's listing of the microkernel, split into routines at the labels
(the kernel CCB handlers of E012 and the hand-written labels), analysed forward from
instruction 0, every label with no static predecessor and then any code still unreached.
Values are constants, pointers typed by structure, values that came from a structure word,
a register or a secondary attribute (with the transforms applied since), or unknown; where
paths join and disagree the value becomes unknown. A pointer is typed where a record
establishes the word (TA3DCtl's own address, kernel CCB and HWPerf words, E002; the transfer
context's client CCB, CCB control and queue links, doc/specs/transfer.md §2.2 and E015; the
render context's client CCB, CCB control, PB descriptor, render lists and queue links, E156, E157,
E159, E161, E165, E167; the TA command's PB descriptor, render details, destination sync list
and RT data, E156, E158, E159, E161, E164; the RT data's render details, E159; the PB
descriptor's first block, E200, E201; the render details' RT data and destination sync list,
E163, E164, E165; a PB block's next block, E200, E201; the TA/3D control block's job words,
the RT data owning each DPM context slot, the TA's command, RT data, render details and
context, the 3D's RT data and render details and the PB descriptor loaded in each pipe, E158,
E159, E163, E200), by the kernel-side layouts of the GPL kernel module, or by what the firmware
itself stores in a slot. A pointer word of the client structures that no record establishes
(the TA command's dword 16 and the RT data's dword 0, among others) is not given, so the words
reached through it count as unresolved accesses. The result is a table of indices, offsets,
masks and register numbers (resgx545-data `firmware/edm-dataflow-11/edm_dataflow.tsv`; the
earlier runs, `firmware/edm-dataflow/` without the TA/3D pointer words and
`firmware/edm-dataflow-3d/` without the render details', PB block's and control block's,
stay as they were); doc/specs/edm_dataflow.md renders it with the glossary's names.

**Coverage.** 6637 of 6637 instructions reached, 70 of 70 routines, 13 entry points plus 21
roots for code no path reaches; 346 structure words, 191 registers (as many as E010's register
reach finds) and 20 secondary attributes. Unresolved: 249 branches, 379 memory
accesses through a base of unknown origin, 14 register-supplied register addresses, 109
sources. Against the run without the render details', PB block's and control block's pointer
words: 4 more structure words, 13 fewer memory accesses and 4 fewer sources unresolved, one
more branch; of the 14 words now given, 8 had been inferred from the firmware's own stores
(the render details' destination sync list and seven of the control block's job words), each
to the structure the records give, and 7 slots are left to inference (15 before). The control
block's own address (E002) adds a typing row and changes no count.

**What it shows and what it does not.** Which words and registers the firmware reads and
writes, from where and under which tests, for every path. It does not show timing, values
that arrive at run time, or what the unresolved accesses reach; E015 states the transfer
part, checked against the runs on the laptop.
