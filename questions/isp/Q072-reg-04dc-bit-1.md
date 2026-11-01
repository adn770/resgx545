+++
id = "Q072"
question = "what does bit 1 of CR_ISP_REG_04DC do to a punch-through pass, when it hangs every one tried and changes no opaque or translucent pass?"
unit = "isp"
phase = 11
evidence = ["E068", "E073", "E213", "E222", "E290", "E416"]
terms = ["CR_ISP_REG_04DC"]
+++

No value of the render-constant ISP registers changes a copy, a fill, a textured triangle (E068)
or 42 overlapping triangles (E073). Bit 1 hangs every punch-through case tried (E213, E222), and
with five overlapping copies, depth less with writes, it changes neither the kept copy nor the
visibility count in an opaque or a translucent pass (E290).

What is open (3d.md §11.9): why the punch-through pass alone stops. An up-front depth test would
keep the same pixels in those passes, so E290 cannot rule it out.

To settle it: bit 1 on a punch-through pass whose shader only discards (no feedback), and on one
whose feedback ends before any depth is written, one case a probe; a translucent pass whose shader
writes depth (depthf) with the bit set.

Narrowed in 11.15 (E416, three runs each): with bit 1 set (0x04dc = 2 and 3) the punch-through pass
hangs in 24 of 24 jobs, whether the shader only discards, always fails the alpha test, or runs
pcoeff alone; with the bit clear all 12 complete. So the hang is not the depth write; what the bit
does besides hanging stays open. Not run: a translucent pass with a depth-writing shader with the
bit set. Status: narrowed, not answered.
