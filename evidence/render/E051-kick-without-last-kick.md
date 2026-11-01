+++
id = "E051"
claim = "A TA kick without LAST_KICK leaves its render waiting (the job hangs and the context is lost); with one job per render, a cleared FIRST_KICK on the second render, FRAG_FLAGS.BIT2 or NO_DEALLOCATE on the first, or both, leave the second render's image its own triangle only, and a cleared BIT10 changes nothing; both runs agree"
unit = "render"
method = "hand-run script probes/render/templates/scenes.sh on the laptop, linux fork with the debug option on: sgxfive-test tri -n 2 on one render context, the second triangle moved 12 pixels right and down, kernel pokes before render 1 or 2 (ta:1 the TA kick flags, ta:7 the render flags), two runs"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-scenes"]
terms = ["GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.LAST_KICK", "FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE", "FRAG_FLAGS.BIT10"]
+++

**What runs.** The tool renders twice on one render context and draws the second triangle 12
pixels right and down. A pixel of render 1's triangle left in render 2's image would count as
"wrong outside" its reference. The script arms `kpoke` just before a render: `ta:1^=0x1` clears
FIRST_KICK of the TA kick, `ta:1^=0x2` clears LAST_KICK, `ta:7^=0x4` flips BIT2 of the render
flags, `^=0x8` NO_DEALLOCATE, `^=0x400` BIT10. Seven cases, two runs.

**Results.** Every case below was run in both runs with the same result.

| render 1 | render 2 | outcome |
|---|---|---|
| as is | as is (control) | each image its own triangle: 1062 and 1046 pixels, 0 outside |
| as is | FIRST_KICK clear | same as control |
| BIT2 | FIRST_KICK clear | same as control |
| NO_DEALLOCATE | FIRST_KICK clear | same as control |
| BIT2 and NO_DEALLOCATE | FIRST_KICK clear | same as control |
| LAST_KICK clear | FIRST_KICK clear (not reached) | render 1 hangs, the context is lost |
| BIT10 clear | as is | same as control |

So a kick without LAST_KICK leaves the render waiting for the last kick. When every job ends
with its render, nothing in BIT2 or NO_DEALLOCATE on one render, and no cleared FIRST_KICK on
the next, carries the first triangle into the second image. The scenes of several kicks are in
E052 and the re-render of a closed scene in E053.

**Not shown.** These runs say what BIT2, NO_DEALLOCATE and BIT10 do not do when each job ends
with its render. What they keep or change in a scene left open is not visible here. The
hang case was not repeated beyond the two runs.
