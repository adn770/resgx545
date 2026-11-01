+++
id = "E324"
claim = "The closed GLES2 stack submits every frame as at least two TA kicks on one client CCB: a first kick (GEOM_FLAGS 0x71 on a context's first frame, 0x61 after; FRAG_FLAGS 0) whose control stream holds the frame's draws and is not the scene's last, then a closing kick (GEOM_FLAGS 0x62, FRAG_FLAGS.BIT10, CR_TE_PSG bit 22) whose stream is only the end-of-scene state blocks and the terminate; a glFlush adds a middle kick (0x60) holding the draws since the last kick; the stream base advances by each kick's stream length, the TA status update 0 carries that offset and update 6 the kicks so far; with FlushBehaviour=2 the flush ends the scene itself (0x73 and FRAG_FLAGS.BIT10) and the next render of the frame carries FRAG_FLAGS bit 14 and frame number 1"
unit = "render"
method = "the render-draws-frames-pb capture (track3d.txt: draws, flushes and frames, 29 runs) and the render-state-variations capture (variations3d.txt, 64 runs) of the closed GLES2 stack under the harness on the laptop as capture host, read with harness/ukernel-extract/state3d.py (the TA command of each kick); the kick count of every run of the thirteen capture tables (their runs.txt), kickwalk.py (the VDM control stream each kick starts) and kick3d.py (the SGX_DOKICK bridge input of each kick)"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-draws-frames-pb", "render-state-variations", "render-register-gaps", "isp-registers", "isp-line-width", "texture-textures", "texture-samplers", "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs", "usse-shaders", "ta-target-sizes"]
terms = [
    "GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.LAST_KICK", "GEOM_FLAGS.INVALIDATE_USE_CACHE",
    "GEOM_FLAGS.INVALIDATE_PDS_CACHE", "GEOM_FLAGS.INVALIDATE_DATA_CACHE", "FRAG_FLAGS.BIT10",
    "cmd_ta.geom_flags", "cmd_ta.frag_flags", "cmd_ta.frame_num", "CR_TE_PSG",
    "CR_VDM_CTRL_STREAM_BASE",
]
+++

**What runs.** tri draws one constant-colour triangle into a 64x64 pbuffer and calls glFinish
(base); the track3d runs add draws (2, 4, 64), glFlush between draws (with the FlushBehaviour
app hint unset, 1 and 2), two frames (eglSwapBuffers between, with and without a clear in the
second), and depth or stencil buffers kept across frames. Every kick is recorded at the
SGX_DOKICK bridge call with its TA command and a snapshot of every device object.

**Results.** One frame, no flush: two kicks, both issued inside glFinish (none at glDrawArrays
or eglSwapBuffers). Of the 595 runs of the thirteen capture tables that kick at all, 549 make
exactly two kicks; the others are the flushes, the second frames, the renders to a texture
(each texture target's scene a pair of its own) and some texture uploads.

Per kick, the bridge input's first-kick and last-in-scene words, the TA
command's flags, and the control stream the kick's `vdm_ctrl_stream_base` starts:

| run | kick | bridge first, last | GEOM_FLAGS | FRAG_FLAGS | stream offset, blocks |
|---|---|---|---|---|---|
| base | 0 | 1, 0 | 0x71 | 0 | 0x0, 8 |
| base | 1 | 0, 1 | 0x62 | 0x400 | 0x5c, 3 |
| draws2, draws4, draws64 | 0 | 1, 0 | 0x71 | 0 | 0x0, 9, 11, 71 |
| draws2_flush | 1 | 0, 0 | 0x60 | 0 | 0x5c, 6 |
| draws4_flush | 1 to 3 | 0, 0 | 0x60 | 0 | 0x5c, 0x98, 0xd4; 6 each |
| frames2 | 2, 3 | 1, 0; 0, 1 | 0x61, 0x62 | 0, 0x400 | 0x70, 0xcc |
| draws2_flushb2 | 0 | 1, 0 | 0x73 | 0x400 | 0x0, 8 |
| draws2_flushb2 | 1 | 0, 1 | 0x63 | 0x4400 | 0x5c, 6 |

- The closing kick's stream is the same three blocks in every run: a secondary-attribute
  state block, the state block with the last-task bit and the MTE emit, and the terminate. The
  draws' blocks sit only in the earlier kicks (one index list per draw; the clear is drawn as a
  state block and an index list of its own).
- `CR_TE_PSG` is 0x400000 (bit 22) on every closing kick and 0 on the others; with a depth or
  stencil buffer, exactly the kicks with the ZLS flags add bit 25 (0x2000000 and 0x2400000).
- The second frame's first kick has GEOM_FLAGS 0x61: `INVALIDATE_USE_CACHE` (0x10) is set on
  the context's first kick only; `INVALIDATE_PDS_CACHE` and `INVALIDATE_DATA_CACHE` (0x60) on
  every kick, the middle ones included.
- A first kick's stream holds 7 + n blocks for n draws, the terminate included (8, 9, 11 and 71
  for 1, 2, 4 and 64 draws); without the clear (noclear) it holds 6.
- The stream base runs on through the frames in one 0x1000-aligned buffer of the GENERAL heap:
  each kick starts where the previous one ended (0x0, 0x5c, 0x70, 0xcc in frames2).
- The bridge input's seven TA status updates and three 3D status updates are the same
  addresses in every kick; update 0's value is the stream offset the kick's own stream ends at
  (0x5c after kick 0, 0x70 after kick 1, 0xcc and 0xe0 in the second frame), update 6's is the
  number of kicks so far (1, 2, 3, ...), and the 3D updates' third value is the number of frames
  (1, then 2); the other values grow with the vertex and state data each frame adds.
- The closing kick alone names the 3D sync object (h3DSyncInfo) in its bridge input, and
  carries the 3D transfer-queue sync addresses in its shared block.
- Two frames alternate two RT data and two render details: the first scene's kicks name the
  set's second RT data (set + 0x50) and one render details, the second scene's the first RT data
  (set + 0x18) and another (E325).
- `frame_num` is 0 in every kick of every run except the second render of draws2_flushb2,
  where it is 1. That render's FRAG_FLAGS add bit 14 (0x4000), which no other run sets.

**What it shows.**

- The closed driver ends each scene with a kick that adds no geometry: the scene's last TA
  command (LAST_KICK, BIT10) is a separate, nearly empty kick. Our stack's one-kick render (a
  single kick both first and last) is a valid form the closed driver also uses when a flush ends
  the scene (FlushBehaviour=2, GEOM_FLAGS 0x73) [CAP].
- `INVALIDATE_USE_CACHE` marks the context's first kick, not every first kick of a scene [CAP];
  why the closed driver invalidates the USSE code cache only there is not shown.
- The TA status updates are how the client learns the TA's progress through its buffers: the
  first counts control-stream bytes, the seventh kicks [CAP]; the EDM writes them at the TA's
  end (the bridge carries the values, the harness completes them).
- What FRAG_FLAGS bit 14 does on a render that continues a frame already rendered once is not
  shown; it fits loading the previous colour (the background object's reload), which the record
  of that topic covers.
