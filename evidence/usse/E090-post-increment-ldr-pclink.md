+++
id = "E090"
claim = "ld/st with a post-increment access the base address and then advance it by the increment in dwords (two loads of [r20,#1++] read dwords 64 and 65 and leave r20 8 bytes on; [r20,#2++] reads dwords 64 and 66 and leaves it 16 bytes on; two stores of r1 and r2 land in dwords 64 and 65); ldr #7 and #8 read 0x01150000 and 0x0001000d; a value moved to pclink reads back unchanged (0x123)"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/memory.toml, probe mem-forms, a fill whose pixel program points r20 at scratch + 0x100 (the host fills dword i with 0xd0000000 + i) and runs the post-increment loads and stores, ldr of two id registers and a pclink round trip, dumping r10-r12 and the scratch dwords; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-memory"]
terms = ["CR_CORE_ID", "CR_CORE_REVISION"]
+++

**What runs.** r20 = scratch base + 0x100, then in five cases:

- `ldad r10, [r20,#1++]` and `ldad r11, [r20,#1++]`;
- `stad [r20,#1++], r1` and `stad [r20,#1++], r2`;
- `ldad r10, [r20,#2++]` twice;
- `ldr r10, #7` and `ldr r11, #8`;
- `mov pclink, r1` then `mov r10, pclink`.

**Results.**

- Two loads with increment 1: r10 = 0xd0000040 and r11 = 0xd0000041, and r20 ends at
  0x3e003108, 8 bytes past its start (0x3e003100): each load reads the current address and
  then adds one dword.
- Two loads with increment 2: 0xd0000040 and 0xd0000042, r20 ends 16 bytes on (0x3e003110):
  the increment counts dwords.
- Two stores with increment 1: scratch dwords 64 and 65 (+0x100 and +0x104) hold 0x123 and
  0x456, the values of r1 and r2, and r20 ends 8 bytes on.
- `ldr #7` gives 0x01150000 and `ldr #8` gives 0x0001000d; the numbers are registers 0x1c and
  0x20 (register `n * 4`), the core id and the core revision.
- `mov pclink, r1` with r1 = 0x123 then `mov r10, pclink` reads 0x123.

**Not shown.** That the two values are CR_CORE_ID and CR_CORE_REVISION by name rests on the
kernel's error-state dump reading the same words at 0x1c and 0x20, not on this probe. One run.
