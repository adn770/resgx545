+++
id = "Q020"
question = "what does a douta in the triangle's primary pixel program do, when its markers never reach the USE task and the readback is the memory table's inputs for markers A in both runs, and other values for markers B in the first?"
unit = "pds"
phase = 7
evidence = ["E125"]
terms = []
+++

From the fill's secondary program `douta` reaches `sa0` to `sa15` (E125). From the triangle job's
primary pixel program (state word 4 at 0x130004) the same sixteen writes do not arrive as markers.

- Markers A: the task stores 0x00000002, 0x22222222, 0x33333333 and on up to 0xeeeeeeee, 0xffffffff
  and 0x11111110 in `sa0` to `sa15`. None is a marker. The same in both runs.
- Markers B: in the follow-up run the same sixteen values as markers A; in the first run 0x00000002
  in `sa0` and fifteen other values (0x14000200, 0x0100d975, ... 0x01555620), none a marker.
- The 1062 triangle pixels are 0x0da7a000 and the other 3034 are 0xff203040 in every case, so the
  shader ran.

The values 0x22222222 to 0xffffffff and 0x11111110 in `sa1` to `sa15` are, attribute for attribute,
the sixteen inputs B to P that the programs of the memory table pass to `sa1` to `sa15` with
`douta` (E142); `sa0` holds 0x00000002 where the table has the input A, 0x11111111. No fit beyond
this match of values is made. The first value, 0x00000002, is not explained.

Open: why the task reads the memory table's inputs and not the markers that the fill probes of the
same table left in the same attributes (E125); whether `douta` in a primary program writes the
task's `sa` registers at all, or writes elsewhere (a different bank, or the task's `pa`); whether
the task started by the primary program reads `sa` from the same place as one started by a
secondary program; what the first run's markers B values are.

To settle it: in the primary program, pass the markers by `douta` and also by `douti` and `doutt`
to a task that stores `sa0` to `sa15`, `pa0` to `pa15` and `o0` to `o15` to scratch; repeat each
case ten times in a fresh context, once after a job that wrote known values and once after a
fill that wrote the memory table's inputs, to tell stale contents from a fixed constant. Vary the
control word's attribute index (bits 19:8).
