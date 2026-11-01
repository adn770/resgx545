+++
id = "E351"
claim = "Every one of the 47 distinct vertex programs the closed GLES compilers emitted in the 595 captured runs opens, past its leading phas and nop, with and.testtanz of two zero immediates into p0, then p0 ldad ... drc0 (a load that never runs), then wdf drc0; so do 27 of the 28 secondary programs and 11 of the 12 state-copy programs, and none of the 114 primary pixel programs or the 225 end-of-render programs; the 93 programs with wdf are these 85 and 8 primary programs that wait after a texture sample, and the one vertex program with a second wdf (vs_texture) waits after its own texture sample"
unit = "usse"
method = "the 13 3D capture tables of 11.11 (604 runs, 595 with programs), unpacked with harness/ukernel-extract/cap3d.py and scanned with opscan3d.py --guard: every USSE program state3d.py reaches, deduplicated by content and kinded by the path that reaches it, its instructions as tools/usse-dis prints them matched against the three-instruction opening; names and counts only"
tiers = ["CAP"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb",
    "isp-registers", "isp-line-width", "ta-target-sizes", "texture-textures",
    "texture-samplers", "texture-formats", "texture-streams", "usse-shaders", "usse-inputs",
    "usse-gles1-programs",
]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** `opscan3d.py --guard` over the unpacked runs of all 13 tables. A program counts as
guarded when the first instructions after its leading `phas` and `nop` are, in this order:
`and.testtanz` writing `p0` from two zero immediates, `p0 ldad` with `drc0`, and `wdf drc0`. A
program is counted once per kind of path that reaches it (state3d.py's paths), however many runs
hold it.

**Results.**

| kind (path) | programs | guarded |
|---|---|---|
| vertex (`vdm.b<i>.vtx.usse<n>`) | 47 | 47 |
| state copy (`vdm.b<i>.pds.usse<n>`) | 12 | 11 |
| secondary (`mte.sec`, `spec.sec`) | 28 | 27 |
| primary (`mte.pri`, `spec.pri`) | 114 | 0 |
| end of render (`eor.usse<n>`; 216 also end of tile) | 225 | 0 |

The unguarded state-copy and secondary program is one program, the one that is also the
background object's secondary program. Every run with programs holds a guarded vertex program.

**The `wdf` count of E350.** The 93 programs with `wdf` are the 47 vertex, 27 secondary and 11
state-copy programs, whose `wdf` is the guard's, and 8 primary programs, whose `wdf` follows a
texture sample. Of its 94 uses, the one beyond one per program is the second `wdf` of the vertex
program of the shader corpus's `vs_texture`, after its own texture sample. No vertex program
lacks the guard.

**What it shows.**

- The closed compilers open every vertex program, and every secondary and state-copy program but
  the background object's, with a load predicated never to run and a wait on its data fence
  [CAP]. A program written by hand that copies this opening matches the closed output.
- The opening belongs to the vertex, state-copy and secondary programs and to no primary or
  end-of-render program. That the
  wait keeps a vertex task from reading `pa0`-`pa3` before the PDS's attribute DMA has landed
  fits this split, but no run has started a vertex program without the opening, so the reason is
  an inference [infer].
