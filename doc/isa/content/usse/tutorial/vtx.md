<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## A vertex shader in two phases

The first triangle's vertex shader gets one vertex, already in
clip
space, in `pa0`-`pa3`, copies it to the outputs `o0`-`o3`, and hands it on twice: to the
vertex cache, then, once vertex culling has seen it, to the MTE. Those are two phases of one
task, the second waiting for `vcull`:

<!-- @prog use_vtx.s -->

- **`phas #7, ...`** names the next phase's first instruction, index 7 here. The index counts
  from the code base the task runs from, so the driver adds where it places the program.
- **The predicated load and `wdf`.** `and.testtanz` with two zero immediates sets `p0` false;
  `p0 ldad` therefore never loads, but it gives `wdf drc0` an access to wait for. The closed
  compilers open every vertex program this way, right after `phas` and `nop`, and every
  secondary and state-copy program but one; no primary or end-of-render program (E351). That
  the wait keeps the task from reading `pa0`-`pa3` before the PDS's attribute DMA has landed is
  the reading this source follows **[infer]**.
- **`mov.repeat4 o0, pa0`** is four moves in one instruction, `o0 = pa0` to `o3 = pa3`: a
  repeat advances every register operand by one per iteration (*Repeats* in the guide).
- **`emitvcbvtx`** ends phase 0; phase 1 is `emitmtevtx` with `.end`.

Run as a vertex task (`--task vertex`; a pixel task hangs on `vcull`, and the simulator refuses
it), the simulator runs the first phase only and does not model the cull decision that starts the
second. With a vertex in `pa0`-`pa3` it ends at the vertex cache emit:

<!-- @sim --task vertex --set pa0=1 --set pa1=2 --set pa2=3 --set pa3=4 prog=use_vtx.s -->
