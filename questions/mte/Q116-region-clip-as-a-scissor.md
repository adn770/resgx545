+++
id = "Q116"
question = "what does the MTE state's region clip (enable bit, first and last 32-pixel tile column, first and last 16-pixel tile row) do to the objects and the clear when it covers part of the target, and what does it do beyond a scissor?"
unit = "mte"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E340", "E347", "E348", "E1060"]
terms = []
+++

A state block with the clip bit in its presence word carries two clip words: an enable in bit 31 of
word 0, the first and last 32-pixel tile columns in its bits 30:16 and 15:0, and the first and last
16-pixel tile rows in word 1, counted from the bottom of the target (E347, E348, from the closed
driver's captures). The closed driver gives a clear's block the clip of the whole target, a draw's
block the clip only when its viewport does not cover the target, and implements a scissor not with
the clip but with extra mask-fill objects of ISP pass type 3 before the draw (E340, E348).

The clip words are read from the closed driver's captures only.

Open: whether the clip drops the tiles outside it for objects and clears alike, whether its bounds
are inclusive as read, what the enable bit alone does, and whether a pixel inside a partly covered
tile but outside the scissor is touched (the closed driver's mask fills suggest the clip works in
whole tiles only [infer]).

To settle it: `probe --tri` with `--blk-add` adding the clip words to the triangle's state block
over sizes from 64x64 to 256x256 with the clip bounds stepped, the written pixels counted against
the tile ranges (with `--pixels`), the enable bit varied alone.

2026-11-14 (E1060, r16-mte rclip, 13 of 13 held-out rows, both controls passing): the clip keeps
the object in whole 32 x 16 tiles, both bounds inclusive, rows counted from memory row 0 (GL's
bottom under E348's positive y scale); the background object writes the tiles it drops (no pixel
left at the target's fill, so no partly covered tile is cut: unlike a scissor); bit 31 clear turns
it off; E348's whole-target clear clip leaves the image as without it. Every open clause is
decided by held-out rows [the clear read as a full-target object and the background, infer];
proposed for retirement (R16-6 a).
