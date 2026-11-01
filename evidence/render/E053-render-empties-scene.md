+++
id = "E053"
claim = "Rendering a scene empties it for the next kick: a third render whose triangle lies off the target and that appends to the closed scene (FIRST_KICK clear) stores only the 4096 background pixels, as the control does, whether the closing render carried BIT2, NO_DEALLOCATE or both and whether the third kick sets NO_DPM_CONTEXT_LOAD; all eight cases agree in both rounds"
unit = "render"
method = "hand-run script probes/render/templates/scenes.sh (closed-scene-rerender) on the laptop, linux fork with the debug option on: sgxfive-test tri -n 3 --geometry 1, render 2 moved 12 pixels, render 3 moved 200 pixels (off the target), kernel pokes of ta:1 and ta:7, two rounds"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-scenes"]
terms = ["GEOM_FLAGS.FIRST_KICK", "FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE", "GEOM_FLAGS.NO_DPM_CONTEXT_LOAD"]
+++

**What runs.** Render 1 is a geometry kick, render 2 closes the scene (the render flags as
given), and render 3 draws its triangle off the target, so no new geometry is tiled, as a new
scene or as a kick that appends to the closed one (`ta:1^=0x1`, FIRST_KICK clear). If the
closed scene were kept, render 3 would store renders 1 and 2's triangles, counted as "other" or
"outside". The eight cases: a new scene (the control), appending after a plain close, after
BIT2 (`ta:7^=0x4`), NO_DEALLOCATE (`^=0x8`) and both (`^=0xc`), and with the third kick also
setting NO_DPM_CONTEXT_LOAD (`ta:1^=0x9`, bit 3) after a plain close, BIT2, and both.

**Results.** In every case render 2 stores both triangles (1548 triangle pixels, 459 of them
outside its own reference) and render 3 stores 0 triangle pixels, 4096 background, 0 other
and 0 wrong pixels. The second run gave the same lines in every case, and the kernel's
poke list was empty after each run.

**Not shown.** This is the same question as E052 with no new geometry, and it still does not say
what BIT2 and NO_DEALLOCATE keep when a scene is rendered again without the kernel's clean-up of
the render target data words in between.
