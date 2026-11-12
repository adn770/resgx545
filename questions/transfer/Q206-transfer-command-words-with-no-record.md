+++
id = "Q206"
question = "what do the words of a transfer job that no record explains do: the 17 register words of the command beyond the render box (words 12 and 13) and the alpha-inversion bit, the words of the tasks the programs start, and the values the builder writes?"
unit = "transfer"
kind = "hw"
value = "medium"
phase = 12
evidence = ["E004", "E019", "E020", "E265", "E272", "E043", "E044", "E126", "E620", "E876", "E884", "E909"]
terms = ["PIXEL_EVENT.END_OF_TILE"]
+++

The pipeline simulator's transfer model (E620) computes a job only when every word it reads is the
builder's or one a record explains, and refuses the rest. The sweeps flip every bit of the
command's words, of the secondary, primary and pixel-event programs' data and of the background
object, one at a time (13679 scenes of fills and copies); 4506 of them are refused under this
question, and most of those changed nothing in the image (4227 of the 4506; 234 recorded a fault
and 45 a hang).

What this question covers is the command's and the tasks' words: the fixed words 1 to 5, 7, 8, 10,
11 and 16 of the command, a set coefficient group (word 17 and above, 3150 scenes), the tag's
layer count, the render box's extent, the pixel shader's output, a task's code base register and
the end-of-tile task's U1 bits no record explains. What it does not cover: a PDS program or input
the simulator does not know is Q207, which tile an end-of-tile task names is answered (E876,
E884: the place its U1 tile fields name, in half-tile units; both fields at once, E909), and a
job that may not complete, or an access outside the scene's memory, is Q003 (with Q076). The hangs and
faults the hardware recorded under refused scenes are not a reason the model uses: it refuses by
the scene's words alone.

Decision of the phase: no table of which word flips change nothing, fault or hang is kept in the
model, because such a table would be a fit to the sweep it is checked against (D6). What would
settle it: the meaning of each register the words load, from the 3D state specs (phase 10), and
for the task words a statement of which fields the end-of-tile and shader tasks read; the faults
are Q003's territory.

Status: open. Open items it covers: the fixed words of the command, the tasks' U0 and U1 values,
and the alpha-inversion bit's other effects (E268 measured modes 0 to 3 only).

Note 2026-11-12 (round 6, E884). The question of which tile the end-of-tile task's U1 fields name
was answered on the fill (held out at 128 x 64 and 256 x 32) and retired; the transfer model now
stores each tile at the place its U1 names and no longer refuses those scenes (the 1534 sweeps of
the fill and the data-word pokes that move a tile, reported fitted). One clause of that question
moves here: where a tile goes when its U1 moves it on both axes at once. Every run so far moved
one field alone (E044, E126, E876, E884), so the model refuses such a U1 under this question. A
fill or copy with both fields poked together would settle it.

Note 2026-11-12 (round 7, R7-geo stage xf, E909). The both-fields clause of the note above is
answered, held out: with the x and y tile fields of the fill's end-of-tile U1 poked together on a
128 x 64 fill, each axis places its tile by its own field, (2t | f) >> 1 on each, nothing past the
target (H-INDEP 8 of 8; only the x field acting or only the y field 0 of 8). The transfer model
places such a tile and no longer refuses it under this question. The question stays open for the
command's fixed words, the tasks' other U0 and U1 bits and the alpha-inversion bit.
