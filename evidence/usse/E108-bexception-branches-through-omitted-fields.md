+++
id = "E108"
claim = "bexception branches like ba and br through the fields its form leaves out: with the target field n it jumps to instruction n, with bit 38 set it jumps by n from itself, and its predicate field (58:56) gates it; with the fields at 0, as the assembler writes it, it jumps to instruction 0, which is how it hung a fill"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/branch.toml, the eight usse-branch-bexc2 probes (client fill on bexc_path.s, one case a probe), one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-branch"]
terms = []
+++

**What runs.** The fill's program tells three outcomes apart by the pixel. Instruction 1 branches
over instruction 2, so only a jump back to instruction 2 ends with `0x0C0C0C0C`. Instruction 4
sets p0 false and instruction 5 is the case. Falling through from 5 ends with `0x0B0B0B0B`, and a
jump to instruction 10 ends with `0x0D0D0D0D`. Nothing in the program depends on the temporaries
a task starts with. The controls are `ba #2`, `br #5` and `ba #10`. The `bexception` cases are
raw 64-bit words, `0xF808000000000000` with the field set: target 2, target 10, bit 38 and
target 5 (`0xF808004000000005`), and the predicate field set to p0 (false) and !p0 (true) with
target 10 (`0xF90800000000000A`, `0xFD0800000000000A`).

**Results.** Each case gives one value over all 2048 pixels:

| instruction 5 | pixel |
|---------------|-------|
| `ba #2` | 0x0c0c0c0c, back to 2 |
| `br #5` | 0x0d0d0d0d, to 10 |
| `ba #10` | 0x0d0d0d0d, to 10 |
| bexception, target 2 | 0x0c0c0c0c |
| bexception, target 10 | 0x0d0d0d0d |
| bexception, bit 38, target 5 | 0x0d0d0d0d |
| bexception, predicate p0 (false), target 10 | 0x0b0b0b0b, falls through |
| bexception, predicate !p0 (true), target 10 | 0x0d0d0d0d |

The baseline triangle before and after each case was exact.

**What it shows.** In this fill `bexception` branches as `ba` does with its target field, as
`br` does with bit 38 set (the target counts from the instruction itself: target 5 at
instruction 5 reaches 10), and it obeys the predicate field. With every field 0 it targets
instruction 0, the `phas`, so the task restarts and never ends **[infer]**, which fits the hang
of E100. What the form's extra bit adds to a plain branch does not show in a fill.
