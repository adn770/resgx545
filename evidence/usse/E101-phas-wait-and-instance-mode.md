+++
id = "E101"
claim = "phas's wait none lets a pixel shader's next phase run at once, with the temporaries the first phase wrote (1062 of 1062 pixels under parallel, 1060 under perinstance); perinstance does not run instances one at a time (the unlocked counter ends at 16 under parallel and 48 under perinstance, with 16 and 48 distinct values over 1062 pixels); a pixel shader hangs waiting on vcull in both modes, and waiting on pt it writes no counter or temporary value; the vertex shader draws alike waiting on vcull or none, in either mode, and hangs waiting on pt under parallel"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/phases.toml, the twelve usse-phases-phas-pix probes (the triangle's pixel shader as two phases, pix_phas2.s) and the five usse-phases-phas-vtx probes (the vertex shader's first phas, vtx_wait.s), one probe a case, one run; the pixel probes also wait on pt with no punch-through feedback"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-phases"]
terms = []
+++

**What runs.** The pixel shader's first `phas` takes the wait (none, pt, vcull) and the mode
(parallel, perinstance). Phase 0 writes `0x00a5a500` to r5. Phase 1 copies r5 to r6, adds 1 to
scratch dword 0 (which starts at `0xd0000000`) by an unlocked load, add and store, and writes
as the pixel either the value it stored (r2, the "count" probes) or r6 (the "temp" probes).
With lost updates, pixels repeat a counter value. The vertex shader probes put the case in the
first `phas` of the triangle's vertex shader. The triangle covers 1062 pixels.

**Results.** Pixel shader, wait none:

| mode, output | pixels written | counter dword after |
|--------------|----------------|---------------------|
| parallel, r2 | 1062, 16 distinct values 1 to 16, 17 to 139 pixels each | `0xd0000010` |
| perinstance, r2 | 1062, 48 distinct values 1 to 48, 2 to 58 pixels each | `0xd0000030` |
| parallel, r6 | 1062 of `0x00a5a500` | |
| perinstance, r6 | 1060 of `0x00a5a500`; (row 33, columns 36 and 37) kept the background | |

Wait pt: all four cases (either mode, either output) draw no counter value and no `0x00a5a500`;
334 (parallel, r2), 304 (perinstance, r2), 334 and 334 (the r6 probes) pixels inside the covered
set hold `0xff00ff00` and the rest is background. Wait vcull: all four cases ended `job hung,
context lost (Connection timed out)`. Vertex shader: wait vcull with parallel, vcull with
perinstance, none with parallel and none with perinstance each draw the triangle exactly (1062
pixels of `0xff00ff00`, 3034 of background); pt with parallel hangs the job. Every baseline
triangle before and after a probe, hangs included, was exact. No visibility counter counted.

**What it shows.**

- Wait none: the next phase follows at once and the temporary r5 carries into it in every pixel
  of the parallel run.
- The unlocked counter loses most updates in both modes and ends higher under perinstance
  (48 against 16), so the instances that read it together came in smaller groups. That is
  not one instance at a time. In the perinstance temp run two pixels were not written at all
  (they kept the background); what that says about the mode is not settled.
- The pt cases show a green that equals the colour the preceding baseline triangle leaves
  **[infer]**: phase 1 never wrote those pixels, which were presumably emitted with the output
  registers phase 1 never set. The count (334 or 304) varies between probes.
- vcull belongs to the vertex shader and pt to a pixel shader's punch-through feedback: a pixel
  shader waiting on vcull hangs, and so does a vertex shader waiting on pt under parallel, but a
  pixel shader waiting on pt does not hang (it draws 0xff00ff00 pixels). With one triangle and no
  culling the vertex shader needs no wait; E121 tests it with a culled triangle.

**Not shown.** The pt wait with perinstance on the vertex shader is not in the table. One run.
