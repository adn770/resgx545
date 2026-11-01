+++
id = "E325"
claim = "The closed GLES1 and GLES2 stacks' RT data set is a 0x88-byte KERNEL_DATA object: the 0x18-byte header (the pending count's address, executed count 0, dword 2 = 8, no out-of-memory signal or partial render, dword 5 = 2) and two 0x38-byte RT data, which the client uses scene by scene in turn with two render details; each RT data holds the HW render context's address in dword 0, render details 0, dwords 2 and 3 = 1 and 0xc0, the shared background object, a DPM state of its own, the shared DPM control and OTPM, the TE tail pointer cache and its size 0x100 in dwords 8 and 9, one render target, a region-header stride of 0, a status word of its own and state 0x10; our kernel's set has the same header but dword 5 = 1 and one RT data whose words follow the same rules"
unit = "render"
method = "every 3D capture of the closed GLES1 and GLES2 stacks under the harness (the render, isp, texture and usse capture tables, 373 runs), the set (render details word 54, TA command dword 16) read at each kick and at exit with harness/ukernel-extract/kick3d.py's hw_rt_data_set layout and the object list of each snapshot; the RT data each kick names (TA command dword 17) by run; against our own stack's render_words of one triangle (render-pending-counts, case one-render), read with tools/usse-asm/render_words.py"
tiers = ["CAP", "HW"]
date = "2026-11-03"
data = ["render-state-variations", "render-draws-frames-pb", "render-register-gaps", "isp-registers", "isp-line-width", "texture-textures", "texture-samplers", "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs", "usse-shaders", "ta-target-sizes", "render-pending-counts", "render-closed-compare"]
terms = [
    "hw_rt_data_set.executed_count", "hw_rt_data_set.num_out_of_mem_signals",
    "hw_rt_data_set.num_spm_renders", "hw_rt_data.bgobj_dev_vaddr",
    "hw_rt_data.dpm_state_dev_vaddr", "hw_rt_data.dpm_control_dev_vaddr",
    "hw_rt_data.otpm_dev_vaddr", "hw_rt_data.num_rts", "hw_rt_data.region_header_rt_stride",
    "hw_rt_data.rt_status_dev_vaddr", "hw_rt_data.state", "hw_rt_data.hw_render_details_dev_vaddr",
    "hw_render_details.count_rt_data_set", "cmd_ta.hw_rt_data_dev_vaddr",
    "misc_info_struct_sizes.sizeof_hw_rt_data_set", "CR_TE_TPC_ADDR", "CR_TE_PSGREGION_ADDR",
    "CR_ISP_REGION_HEADER_BASE", "CR_ISP_PARTIAL_REGION_BASE", "hw_rt_data_set.num_rt_data",
    "hw_rt_data.hw_render_context_dev_vaddr", "hw_rt_data.te_tpc_dev_vaddr",
    "hw_rt_data.te_tpc_bytes", "cmd_ta.hw_rt_data_set_dev_vaddr",
]
+++

**What runs.** The closed client builds its RT data set once per render target at context
creation; the TA command names the set (dword 16) and one RT data (dword 17), the render
details the set (word 54) and the same RT data (word 55). No firmware runs under the harness,
so the words are the client's.

**Results.** The set of the window surface, the same at every kick and at exit of every run:

| bytes | word | closed | ours (one render) |
|---|---|---|---|
| header +0x00 | pending count address | a 4-byte KERNEL_DATA object | our kernel's |
| +0x04 | executed count | 0 | 1 after the render |
| +0x08 | dword 2 | 8 | 8 |
| +0x0c, +0x10 | out-of-memory, partial renders | 0, 0 | 0, 0 |
| +0x14 | dword 5 | 2 | 1 |
| RT data at +0x18, +0x50 | dword 0 | the HW render context | our context page |
| | render details | 0 | 0 |
| | dwords 2, 3 | 1, 0xc0 | 1, 0xc0 |
| | background object | one, shared by both | ours |
| | DPM state | 0x88-byte TA data objects, one each | ours |
| | DPM control, OTPM | one 0x40-byte and one 0x50-byte object, shared | ours |
| | dwords 8, 9 | the TE tail pointer cache (`CR_TE_TPC_ADDR` of the kicks), 0x100 | our tail pointer cache (the TA command's too), 0x100 |
| | render targets, region-header stride | 1, 0 | 1, 0 |
| | status word | a 4-byte object each | ours |
| | state | 0x10 | 0x10 |

- The scenes take the RT data in turn: a context's first scene names the second RT data
  (set + 0x50) and one render details object, its second scene the first RT data (set + 0x18)
  and a second render details object, in every run with two frames or a flush that ends a scene
  (frames2, depth_f2, draws2_flushb2 and the rest; E324). With the RT data the scene's other
  words change too: the destination sync list, the pixel-event program, the background
  object's primary program word and its word list, and the two 0x300-byte region-header
  buffers swap roles, the scene's `CR_ISP_REGION_HEADER_BASE` (and `CR_TE_PSGREGION_ADDR`)
  being the other scene's `CR_ISP_PARTIAL_REGION_BASE` (render details word 10). The background
  object and the TE tail pointer cache are shared.
- A render to a texture gets a set of its own (at another address, with the same layout).
- The TE tail pointer cache object is 0x100 bytes, the size dword 9 holds; the DPM control is
  0x40 bytes and the OTPM 0x50.
- The header's dword 2 is 8 in every 64x64 run and in ours; the RT data's dwords 2 and 3 are 1
  and 0xc0 in every 64x64 capture and in ours.
- The set's object is 0x88 bytes: misc_info's RT data set size (0x50) is one header and one RT
  data, and the closed client allocates a header and two.

**What it shows.**

- RT data set dword 5 is the number of RT data the set holds (2 for the closed client, 1 for
  ours), and the RT data follow the header at a 0x38-byte stride [CAP][HW].
- RT data dword 0 is the address of the HW render context the RT data belongs to [CAP][HW].
- RT data dwords 8 and 9 are the TE tail pointer cache the TA kick loads (`CR_TE_TPC_ADDR`) and
  its size [CAP].
- The closed driver double-buffers the RT data and the render details per scene, so a scene's
  TA can run while the previous scene renders on the other RT data; our kernel's single RT data
  makes each scene wait for the previous render.
- Our fresh run (render-closed-compare, one render, exact) reads the same: header dword 2 = 8,
  dword 5 = 1, RT data dword 0 = 0x32411000 (the context the kernel's cleanup trace names), dwords
  2 and 3 = 1 and 0xc0, dwords 8 and 9 = 0x20000000 (the kernel's tail pointer cache) and 0x100;
  a scene of two kicks and two renders on that one RT data are exact too.
- Header dword 2 (8), RT data dwords 2 and 3 (1 and 0xc0) and dword 9 (0x100) are size words:
  over 222 target sizes they are the tiles across the macrotile grid, the blocks per macrotile,
  a macrotile's region-header bytes and the tail pointer cache's bytes (E331) [CAP].
