+++
id = "E452"
claim = "A write of the MADD fields of CR_CLKGATECTL2 alone (bits 13:12 and 21:20, both at 0, 1 or 3, or each at 0 alone), issued 17 to 27 ms into a loop that finishes and returning after it (loops of 2500000 iterations) or inside it (5000000), leaves 18 of 18 loops of 2500000 iterations (floating-point and integer) and 12 of 12 single-field writes finishing in 87.1 to 88.1 ms, as the 6 of 6 loops with no write do (87.2 to 87.7 ms), and the register reads the value written; the floating-point loop of 5000000 iterations hung in 2 of 9 writes and in 2 of 3 controls"
unit = "usse"
method = "probes/usse/madd-length.toml and probes/usse/madd-write.toml on the laptop (direct cable), linux fork 01cff214d7d2 with the debug option on, module srcversion FC6EB50DEF21E3A6249727F (the loaded module, read from /sys/module, equal to the installed file's modinfo; both printed by the run), sgxfive-test probe --stamp of the table's loop programs (eight instructions per iteration, six fmads or six integer multiply-adds, o0 = the counter) and debugfs kregnow 0x0004=V written by a shell 90 ms (2500000 iterations) or 130 ms (5000000) after launching the tool, the tool starting about 70 ms after the launch and its job window printed in wall-clock ns, the write stamped the same way; V = 0x00aaaaaa with bits 13:12 and 21:20 set to 0, 1 or 3 together (0x008a8aaa, 0x009a9aaa, 0x00babaaa), or 13:12 alone (0x00aa8aaa) or 21:20 alone (0x008aaaaa) at 0; nothing else is written to the register (no field at bits 11:2), the GPU reset before each run (which puts it back at 0x00aaaaaa); first the length found without writes (4 lengths, 3 runs each), then 3 runs of each write; registers read after each run"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-madd-length", "usse-madd-write"]
terms = ["CR_CLKGATECTL2.MADD0_CLKG", "CR_CLKGATECTL2.MADD1_CLKG", "CR_CLKGATESTATUS.MADD0_CLKS", "CR_CLKGATESTATUS.MADD1_CLKS"]
+++

**What runs.** E445 wrote the MADD fields while idle (no effect) and during loops of 12500000
iterations, which hang by themselves. This follow-up first finds the length at which a loop still
finishes without a write, then writes only the two MADD fields during loops of that length.

**Length (no write, usse/madd-length, three runs each; the loop's job time in ms).**

| iterations | floating-point | integer |
|---|---|---|
| 2500000 | 3 of 3 finish, 87.3 to 87.4 | 3 of 3 finish, 87.1 to 87.4 |
| 5000000 | 3 of 3 finish, 173.5 to 173.9 | 1 of 3 finish |
| 7500000 | 1 of 3 finish, 260.9 | 2 of 3 finish, 260.5 to 261.0 |
| 10000000 | 0 of 3 | 0 of 3 |

A job that does not finish is "job hung, context lost" and the GPU is reset. In the later control
runs (usse/madd-write, no write) the floating-point loop of 5000000 iterations finished in 1 of 3
runs, so no loop of 5000000 or more finishes reliably; 2500000 did in 12 of 12 no-write runs.

**Writes (usse/madd-write).** The write call began 17 to 27 ms into the 87 ms loops and returned 80
to 93 ms later (30 calls), after the loop ended; in the loops of 5000000 iterations (7 calls) it
began 60 to 67 ms in and returned 80 to 87 ms later, inside the 174 ms loop.

| written | loop | runs finishing | job time, ms | CR_CLKGATECTL2 read after |
|---|---|---|---|---|
| nothing | 2500000, fp and int | 6 of 6 | 87.2 to 87.7 | 0x00aaaaaa |
| both fields 0 | 2500000, fp and int | 6 of 6 | 87.1 to 87.7 | 0x008a8aaa |
| both fields 1 | 2500000, fp and int | 6 of 6 | 87.2 to 87.5 | 0x009a9aaa |
| both fields 3 | 2500000, fp and int | 6 of 6 | 87.1 to 88.1 | 0x00babaaa |
| MADD0 alone at 0 | 2500000, fp and int | 6 of 6 | 87.1 to 87.5 | 0x00aa8aaa |
| MADD1 alone at 0 | 2500000, fp and int | 6 of 6 | 87.1 to 87.6 | 0x008aaaaa |
| both fields 0, 1, 3 | 5000000, fp | 7 of 9 (2 hung) | 173.8 to 174.2 | as written, 0x00aaaaaa after the hung runs |

CR_CLKGATESTATUS read 0x00000020 after every run.

**What it shows.**

- Writing the MADD gates to 0, 1 or 3, together or one at a time, with the write issued in a loop
  that finishes, changes neither whether it finishes nor the time it takes, floating-point or
  integer: 30 of 30 writes at 2500000 and 7 of 7 completed at 5000000 [HW]. The 2 hung 5000000 runs are those the
  controls hang at too (2 of 3) [HW]; the write is not shown to cause a hang.
- Where in a write call the register changed is not known: at 2500000 the call returned after the
  loop ended, so the new value may have taken effect only then; the 5000000 runs returned inside
  the loop [infer, from the stamps]. So the 2500000 runs show only that a write issued in the
  loop, landing in or after its end, is harmless. For the 7 completed 5000000 runs, a value in
  place for the end of the loop is [infer]: the stamp shows that the call returned, and the
  register was read only after the run.
- The gates did not show on CR_CLKGATESTATUS during the loop (E365, E445): no field written tells the
  floating-point arithmetic from the cache traffic [HW].

**What it does not show.** The fields at bits 11:2 (a run over them froze the laptop; none was
written here), a job that loads the main cache or arithmetic units harder, a write that is certain
to land inside a loop of 2500000 iterations, and why loops of 5000000 and more hang.

**Provenance.** The sgxfive-test binary of the length runs (usse/madd-length) is the one whose
sha256 its env.toml names (7de509d3...), that of the write runs (usse/madd-write) the one named
in its env.toml (83318889...). Both were built from source not yet committed, which was later
committed in f63c7d19.
