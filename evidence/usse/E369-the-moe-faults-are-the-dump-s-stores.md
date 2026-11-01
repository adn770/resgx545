+++
id = "E369"
claim = "The MOE sequences that faulted fault through the probe template's own stores, not through moest: the three moest-state sequences completed in all 30 of ten interleaved runs, with mixed pixels; smbo #1, #0, #0, #0 before the moest selectors faulted one run of three, and smoa mirror on source 0 (or on all four operands) before a repeated mov faulted every run (6 of 6); each fault is a bus interface fault at an address outside the scratch; smoa #-1, #-2, #511, #-512 alone, each moest selector alone after it and each operand's offset alone complete"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/moe-faults.toml: the three moest-state sequences of E087 ten times each, interleaved (dump.s); smoa #-1, #-2, #511, #-512 alone, then with each moest selector 0-15 alone, and with each operand's offset alone; smr 4 then smoa #0 with each of the four modes on each of the four operands before mov.repeat8 r20, r1 (wide_dump.s), and the all-mirror case five times; smbo with one value at a time before the sixteen selectors, three runs; the driver's log lines per table; one run, 86 cases"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["usse-moe-faults"]
terms = []
+++

**Results.**

- *Ten runs.* `smoa #1, #2, #3, #4, none, repeat, clamp, mirror`, `smoa #-1, #-2, #511, #-512,
  mirror, clamp, repeat, none` and `smbo #1, #2, #3, #4`, each followed by the sixteen `moest`
  selectors, completed in all 30 jobs. The pixels are mixed in each.
- *Split.* `smoa #-1, #-2, #511, #-512` with mode none completes alone and with any single
  `moest` selector after it (17 cases); an offset on one operand at a time completes (4); the
  sixteen selectors alone, and after `smoa #0` x4, complete.
- *Mirror.* After `smr #4`, mirror on operand 1 (source 0) faults the job; mirror on source 1
  (the mov's source) gives values from outside the presets in r20 (0x00000ed7 on 354 pixels
  and others); clamp or mirror on the destination leaves r20 at its preset; all four mirrored
  faults five runs of five. The other modes and operands complete.
- *smbo.* `smbo #1, #0, #0, #0` then the selectors faulted the first of three runs and gave
  mixed pixels in the other two; values 2, 3 and 4 on the other operands completed every run.

Every fault is logged as a bus interface fault (0xd0400) at an address outside the scratch
(0x236001-0x23600e, 0x11137011, 0x494b6003), the job stalled and recovered.

**Templates.** dump.s (the ten-run, split and smbo tables) stores through r29, set after the
case's instructions; wide_dump.s (the mirror table) stores through r47, set after them as well,
while r46, the register its header names, holds the address of scratch dword 64 and is not the
stores' base (the header is right about r46 and does not name r47; it is a landed file and is
left as it is). No case changed the stores' base register itself, so the mechanism below is read
from which cases fault, not shown.

**Reading [infer].** The MOE state stays in force for the rest of the task (E087), so it acts on
the template's instructions after the case's own: `smbo`'s first value moves the write of the
store's base register (r29 in dump.s) one register on, so the sixteen stores take their address
from whatever r29 held before, which faults or not by what an earlier job left there; mirror on
source 0 sends the stores' address operand (r47 in wide_dump.s) to another register. `moest` plays
no part; the mixed pixels are the same template effect on the final `mov.end o0` (E370).

**Not shown.** Which register the mirrored source 0 reads; the fault's requestor; the base
register's value at the stores (no probe read it back or changed it directly).
