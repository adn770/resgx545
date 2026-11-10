+++
id = "E146"
claim = "PDS #13 (40 instructions, 24 data dwords) tests one event word and starts one of four EDM tasks, three fast paths for exact event groups and a general task for everything else; PDS #14 (14 instructions, 12 data dwords) tests one request word and starts one of three tasks by request-bit group, in priority order"
unit = "edm"
method = "PDS images #13 and #14 of the cut firmware (04_pds13.bin, 05_pds14.bin), disassembled with our pds-dis at the data sizes in the BUFFERS table (6 and 3 rows of 4 dwords), read with the PATCHES table unpacked by tools/fwcutter/fwformat.py; the ukernel disassembled with usse-dis only at the instruction that starts PDS #14; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "infer"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["CR_EVENT_OTHER_PDS_EXEC", "CR_EVENT_OTHER_PDS_DATA", "CR_EVENT_STATUS", "ta3d_ctl", "CR_EVENT_STATUS.DPM_INIT_END", "CR_EVENT_STATUS.DPM_CONTROL_STORE", "CR_EVENT_STATUS.DPM_STATE_STORE", "CR_EVENT_STATUS.DPM_CONTROL_CLEAR", "CR_EVENT_STATUS.ISP2_ZLS_CSW_FINISHED", "CR_EVENT_STATUS.OTPM_INV", "CR_EVENT_STATUS.TPC_FLUSH", "CR_EVENT_STATUS.DPM_CONTROL_LOAD"]
+++

**What was read.** The two stored images are templates: the data segment comes first (the data
rows of E003's layout, 24 dwords for #13 and 12 for #14), then the instructions (40 and 14; the
file sizes 256 and 104 bytes add up exactly). The data dwords the loader patches are listed in
the firmware file's PATCHES table (E003): for #13 the four task code words and the constants 2,
0x100 and 0x200; for #14 the three task code words, three more constants of 2 or 0x200 and the
two request masks 0x4000f and 0x120080. A code-word patch holds an instruction index of the
ukernel plus a fixed addend (E003); the byte offset in the ukernel image is the index times 8.
A "mask test" below is "AND with a data constant, then test for zero".

**Results.**

*PDS #13.* It has two parts.

- It first passes three input values on to the task it will start, unconditionally: the
  program's `ir0` and `ir1` inputs and the timer, to three destination words held in its data
  (0, 0x100, 0x200, the last two patched by the loader). So every task #13 starts sees the same
  three values as secondary attributes [infer: the destination words are not decoded here].
- It then forms `m` = `ir1` masked to its low 24 bits, and decides among four doutu starts, each
  followed by a halt. The tests run in this order: if `m` has bit 8 set (0x100), go to the
  general task. Else for each of three groups, if `m` holds any bit of the group, the fast path
  is taken only when `m` holds no bit outside the group and `ir0` is 0; otherwise it goes to the
  general task. The groups, from unpatched data constants of the image:

| group mask | fast-path task (instruction index, byte offset in the ukernel) |
|---|---|
| 0x00400090 (bits 22, 7, 4) | 3594, 0x7050 |
| 0x00000200 (bit 9) | 1434, 0x2cd0 |
| 0x00300400 (bits 21, 20, 10) | 2766, 0x5670 |
| anything else, including `m` = 0, bit 8, a mix of groups or `ir0` not 0 | 6, 0x30 |

  Exactly one task is started per run of the program. The task indices are those of E003's four
  `CODE_WORD` patches of #13; the loader writes #13's address and data size to
  `CR_EVENT_OTHER_PDS_EXEC` and `CR_EVENT_OTHER_PDS_DATA` (E002, E003, E008).
- The bit positions of the three groups and of the bit-8 case coincide with the fields of
  `CR_EVENT_STATUS`: 22, 7 and 4 are `CR_EVENT_STATUS.DPM_INIT_END`,
  `CR_EVENT_STATUS.DPM_CONTROL_STORE` and `CR_EVENT_STATUS.DPM_STATE_STORE`; 9 is
  `CR_EVENT_STATUS.DPM_CONTROL_CLEAR`; 21, 20 and 10 are
  `CR_EVENT_STATUS.ISP2_ZLS_CSW_FINISHED`, `CR_EVENT_STATUS.OTPM_INV` and
  `CR_EVENT_STATUS.TPC_FLUSH`; 8 is `CR_EVENT_STATUS.DPM_CONTROL_LOAD`. That `ir1`
  carries `CR_EVENT_STATUS` bits unchanged, rather than a word of the firmware's own whose
  positions happen to agree, is an inference [infer]; the program only shows the positions.

*PDS #14.* It passes `ir0` and the timer to two destination words (0 and 0x200) for the task,
then decides on `ir0` alone, again one doutu start per run, in this priority order:

| test on `ir0` | task (instruction index, byte offset) |
|---|---|
| any bit of 0x0004000f | 3700, 0x73a0 |
| else any bit of 0x00120080 | 1492, 0x2ea0 |
| else (including `ir0` = 0) | 2792, 0x5740 |

Unlike #13 the groups are not exclusive: a request word with bits from both masks starts only the
first task, and a word with bits outside both starts the third. The three code words are E003's
`CODE_WORD` patches in #14 (rows 0, 1 and 2). So `ir0` is a request mask grouped three ways; its
bits (0x0004000f, 0x00120080) are not the positions of #13's groups, so they are a numbering of
the firmware's own.

*The start of #14.* The ukernel instruction that starts #14 is the `emitpds` E003 locates (PDS
control word and address patched at instructions 5983 and 5986). Before it, the code reads
TA3DCtl dword 31 through `sa0` (E002), ORs a request mask held in `r16` into it, writes it back,
and skips the start when the OR changed nothing. Which register becomes `ir0` is read from the
operand order of the `emitpds` only [infer].

**What of the hypothesis holds.** Both programs are event or request dispatchers started through
the PDS of E002/E003; #13 selects among four tasks and #14 among three, with the masks and task
offsets named above. That #13 dispatches events (bit positions of `CR_EVENT_STATUS`) and #14
runs requests posted through TA3DCtl dword 31 holds as a reading of the programs.

**Not shown.** What the seven tasks do; that the three #14 tasks do the same work as the three
#13 fast paths, and that they clear the bits they were handed; which code posts which request
bit and what each request bit means; how the general task re-posts several events as requests;
what `ir0` and `ir1` of #13 are at run time (nothing here runs the program); the semantics of
the three destination words beyond their values; why the work is a separate task rather than
inside the event program.

**Correction 2026-11-10:** The table of dispatch groups above stands as a reading of the code, but
the positions its reading of ir1 gives them do not: the first event a firmware task logged for a
fill's end of render arrived in slot 3 with pa1 bit 4 in 3 of 3 fills (E747, frozen witness, held
out), not in slot 0 with bit 18, and the frozen bit sets of E155's reversed order explained 132 of
the 138 job events logged against 88 of the same-position order. So the bits of the group masks are
status bits 22 minus the bit, as E155 reads them: pa1 bits 22, 7 and 4 are status bits 0, 15 and 18,
bit 9 is status bit 13, bits 21, 20 and 10 are status bits 1, 2 and 12; the names that this record's
terms give them (DPM_INIT_END, DPM_STATE_STORE and the others at their own positions) are not their
names. The dispatch rule itself (bit 8 and the three groups, with ir0 = 0 for a fast path) held on
all 138 entries (E747).
