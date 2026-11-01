+++
id = "E323"
claim = "The closed GLES1 and GLES2 stacks registers a 0x44-byte HW render context image whose dword 2 it names as the page directory's physical address (the registration's offset 8, which the kernel patches); in every capture the context holds CONTEXT_FLAGS 0x21 (NEW and OWN_PB), priority 0, the client CCB and its control, no submitted command, its PB descriptor, in dword 7 the address of a 0x40-byte parameter-heap object at the DPM page table's base plus 0x40000, empty render lists and queue links, and the process's PID; only the PID and, with the PB size, dword 7 change between runs, and our kernel's context differs only in OWN_PB, the page directory and the PID"
unit = "render"
method = "every 3D capture of the closed GLES1 and GLES2 stacks under the harness (the render, isp, texture and usse capture tables, 373 runs), the context read at each kick and at exit with harness/ukernel-extract/kick3d.py's hw_render_context layout; the registration's arguments from the bridge log (SGX_REGISTER_HW_RENDER_CONTEXT); against our own stack's render_words of one triangle (render-pending-counts, case one-render, and the fresh render-closed-compare (case one-render: words before and after the render, the registers 0x0400-0x0560 read after it; cases two-kicks and two-renders)), read with tools/usse-asm/render_words.py"
tiers = ["CAP", "HW"]
date = "2026-11-03"
data = ["render-state-variations", "render-draws-frames-pb", "render-register-gaps", "isp-registers", "isp-line-width", "texture-textures", "texture-samplers", "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs", "usse-shaders", "render-pending-counts", "render-closed-compare"]
terms = [
    "hw_render_context.context_flags", "CONTEXT_FLAGS.NEW", "CONTEXT_FLAGS.OWN_PB",
    "hw_render_context.priority", "hw_render_context.ccb_base_dev_vaddr",
    "hw_render_context.ccb_ctl_dev_vaddr", "hw_render_context.submitted_commands",
    "hw_render_context.hw_pb_desc_dev_vaddr", "hw_render_context.pid",
    "hw_pb_desc.page_table_base", "hw_render_context.pd_dev_paddr",
    "hw_render_context.param_obj_dev_vaddr",
]
+++

**What runs.** The closed stack registers its render context once, at eglCreateContext:
SGX_REGISTER_HW_RENDER_CONTEXT passes the context image, its size (0x44) and the offset of the
word the kernel patches with the page directory's physical address (0x8); the harness copies
the image into KERNEL_DATA and writes its mock page-directory address (0x1000) there. The
transfer context is registered the same way (size 0xb4, offset 0x8).

**Results.** The context in the base run, the same at both kicks and at exit (no firmware runs
under the harness, so these are the words the client and the kernel write):

| dword | name | closed | ours, before / after the render |
|---|---|---|---|
| 0 | `context_flags` | 0x21 (NEW, OWN_PB) | 0x1 / 0x0 |
| 1 | `priority` | 0 | 0 |
| 2 | (page directory) | 0x1000, the harness's | a page address, per run |
| 3, 4 | CCB, CCB control | the CCB and its control | ours |
| 5 | `submitted_commands` | 0 | 0 |
| 6 | PB descriptor | the context's | ours |
| 7 | | parameter heap object, page table + 0x40000 | page table + 0x40000 |
| 8-15 | render lists, queue links | 0 | 0 |
| 16 | `pid` | the process's | 0 |

- Across every run of the tables named only the PID changes, and dword 7 with the PB size: at
  the default size it is 0xc0463000, with PBSize=1048576 or 8388608 0xc00a3000; in both it is the
  DPM page table's base (`hw_pb_desc.page_table_base`) plus 0x40000, the address of a 0x40-byte
  object the client allocates in the parameter heap right after the 0x40000-byte page table
  and before the background object. The object reads 0 in every snapshot.
- Our kernel's context (render-pending-counts, one render): dword 7 has the same rule (page
  table 0x10423000, dword 7 0x10463000); dword 2 is a page-aligned address that differs between
  our runs, where the closed stack's registration puts the page directory's physical address.
- Our fresh run on the laptop (render-closed-compare, one render, the image exact) agrees: dword 0
  is 0x1 before the render and 0 after, dword 2 0x0bcba000 (another page address than in
  render-pending-counts), dword 7 0x10463000 with the PB descriptor's page table at 0x10423000
  (+0x40000), the PID 0; the kernel's cleanup trace names the context at 0x32411000, the address
  our RT data's dword 0 holds (E325).

**What it shows.**

- Render context dword 2 is the page directory's physical address: the closed client names it
  as the word the kernel patches with it, and our kernel's value there is a page address
  [CAP][HW].
- The closed client sets `CONTEXT_FLAGS.OWN_PB` on its context (it allocates its own PB
  descriptor and parameter buffer), ours does not; both set `NEW`, which our render clears.
- Dword 7 is the address of a 0x40-byte parameter-heap object placed after the DPM page table,
  in both stacks; what the firmware keeps there is not shown by a capture, since the harness
  runs no firmware.
- The client leaves the render lists, the queue links and the submitted-command count at 0:
  the firmware fills them.
