+++
id = "E367"
claim = "idiv's repeat count is enc[47:44] + 1 (1 to 16; enc[47], outside every field before, is its high bit): iteration k divides src1 + k by src2 + k, writes the quotient to dst + k and the remainder to dst + k + 1, which the next iteration's quotient overwrites, a divisor 0 giving 0xffffffff for both; the 21 cases in which no iteration reads a register an earlier one writes match this exactly, and in the 9 in which one does every such read saw what an iteration ten or more before wrote and the old value where the writer ran nine or fewer iterations before"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/idiv-enc47.toml (div_dump.s: r1-r9 the inputs, r10-r29 preset and stored; idiv as a raw word with enc[47] and the repeat field enc[46:44] set or clear, other destinations and sources, three input sets: quotients 3 to 23 with distinct remainders, the same with divisors 0, and the 11.7 run's inputs) and idiv-enc47-repeat.toml (div_dump48.s, 48 temporaries: counts 9 to 16 into r18 on, r10-r40 stored, two input sets), each followed by wdf; readbacks compared with the model offline; one run each, 30 cases"
tiers = ["HW"]
date = "2026-11-03"
data = ["usse-idiv-enc47", "usse-idiv-enc47-repeat"]
terms = []
+++

**What runs.** idiv r10, r1, r2, drc0 with the inputs r1-r9 chosen so that r(k) / r(k+1) gives
the quotients 3, 5, 7, 11, 13, 17, 19, 23 (the last 24: its remainder exceeds the divisor) with
distinct remainders, then the same with r3 and r6 zero, then the 11.7 run's inputs with r9 =
0xed7.

**Results.**

- With enc[47] alone, nine iterations: r10-r17 the quotients 3 to 0x18, r18 the quotient of r9
  by r10's old value (0), r19 its remainder (9). With the field at 1, 3 and 7: ten, twelve and
  sixteen iterations. The 11.7 run's eight changed destinations (E295) are the same nine
  iterations over its inputs: r12 = 0x80 is r3 / r4, r17 = 0x8976a is r8 / r9.
- Into r18 on, sixteen counts over two input sets (one with 0xffffffff, 0x80000000 and a zero
  divisor), and nine iterations into r12, the plain count, `.repeat2` and `.repeat4` and the
  zero divisors at one iteration: every register stored is as the model gives it (21 cases).
- Where an iteration's source is an earlier iteration's destination (nine cases, from r10 or r3
  on): the read of r12 at iteration 11 gave 2, the remainder iteration 1 wrote, and that of r13
  its preset; the model in which a read sees the writes of iterations ten or more before it and
  the old value otherwise gives all nine readbacks; one in which a read sees every earlier write
  gives none of them, one in which it sees none gives six.

**Not shown.** `idiv` with a `pa` destination repeated; whether the ten-iteration distance is a
property of the unit or of the instances in flight (one fill size). The decoder prints the
count (`idiv.repeat9` to `.repeat16`) and the simulator runs it; a source an earlier iteration
writes stops the simulator, and so does a repeated `idiv` into `pa`.
