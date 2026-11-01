+++
id = "E327"
claim = "The closed GLES1 and GLES2 stacks' PB descriptor at the default size holds no flags, 0x422 pages in dword 1, the free list (pages << 16 | 1) and the TA allocation word ((pages - 1) << 16) both initial and current, the page table's base, zero allocated, local and global counts, thresholds TA 0x432 (pages + 16), ZLS 0x400, global 0x400 and PDS 0x300, and its one PB block, which holds the page count, the free-list word, the descriptor's own address and no next block; PBSize=1048576 and 8388608 give 98 pages (TA threshold 114, ZLS and global 64, PDS 0), smaller PBSize values fail eglInitialize, MaxParamBufferSize changes nothing and ZLSThreshold=0 zeroes the ZLS threshold; our kernel's descriptor before its first render is the default one word for word but for the addresses"
unit = "dpm"
method = "every 3D capture of the closed GLES1 and GLES2 stacks under the harness (the render, isp, texture and usse capture tables, 373 runs; track3d.txt's PBSize, MaxParamBufferSize and ZLSThreshold app hints), the descriptor and its block read at each kick and at exit with harness/ukernel-extract/kick3d.py's hw_pb_desc and pb_block layouts; against our own stack's render_words of one triangle (render-pending-counts, case one-render), read with tools/usse-asm/render_words.py"
tiers = ["CAP", "HW"]
date = "2026-11-03"
data = ["render-state-variations", "render-draws-frames-pb", "render-register-gaps", "isp-registers", "isp-line-width", "texture-textures", "texture-samplers", "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs", "usse-shaders", "render-pending-counts", "render-closed-compare"]
terms = [
    "hw_pb_desc.pb_flags", "hw_pb_desc.initial_stack_top", "hw_pb_desc.initial_dpm_ta_alloc",
    "hw_pb_desc.page_table_base", "hw_pb_desc.allocated_page_count",
    "hw_pb_desc.current_stack_top", "hw_pb_desc.dpm_ta_alloc", "hw_pb_desc.local_page_count",
    "hw_pb_desc.global_page_count", "hw_pb_desc.ta_threshold", "hw_pb_desc.zls_threshold",
    "hw_pb_desc.global_threshold", "hw_pb_desc.pds_threshold", "hw_pb_desc.first_block_dev_vaddr",
    "pb_block.page_count", "pb_block.first_page", "pb_block.next_block_dev_vaddr",
    "cmd_ta.ta_threshold", "GEOM_FLAGS.PB_THRESHOLD_UPDATE", "hw_pb_desc.page_count",
    "pb_block.stack_top",
]
+++

**What runs.** The closed client allocates its parameter buffer, its DPM page table and its PB
descriptor at eglCreateContext and names the descriptor in every TA command. Since no firmware
runs under the harness, the words read are the client's. The track3d runs set the PB size
(PBSize: 64 KiB to 8 MiB, with 256 draws or one), the maximum (MaxParamBufferSize: 512 KiB to
2 MiB) and ZLSThreshold=0 as app hints.

**Results.** The descriptor (dwords 0-14) and its block, the same at every kick and at exit of
a run:

| word | default (371 runs) | PBSize 1 MiB, 8 MiB |
|---|---|---|
| `pb_flags` | 0 | 0 |
| dword 1 | 0x422 | 0x62 |
| `initial_stack_top`, `current_stack_top` | 0x04220001 | 0x00620001 |
| `initial_dpm_ta_alloc`, `dpm_ta_alloc` | 0x04210000 | 0x00610000 |
| `page_table_base` | 0xc0423000 | 0xc0063000 |
| `allocated_page_count`, `local_page_count`, `global_page_count` | 0 | 0 |
| `ta_threshold` | 0x432 | 0x72 |
| `zls_threshold` | 0x400 (0 with ZLSThreshold=0) | 0x40 |
| `global_threshold` | 0x400 | 0x40 |
| `pds_threshold` | 0x300 | 0 |
| block: `page_count`, dword 1 | 0x422, 0x04220001 | 0x62, 0x00620001 |
| block: `first_page` | 0xf0001000 (the descriptor) | the same |
| block: `next_block_dev_vaddr` | 0 | 0 |

- The parameter buffer is the parameter heap's first object, 0x422000 bytes (0x422 pages) at
  the default size and 0x62000 with the two PBSize values; the 0x40000-byte page table follows
  it, so its base moves with the size.
- PBSize=786432 and every smaller value fail eglInitialize with EGL_BAD_ALLOC: no kick, no
  capture. MaxParamBufferSize at 2 MiB, 1 MiB and 512 KiB leaves the descriptor as the default.
- In every TA command the four threshold words are 0, and `GEOM_FLAGS.PB_THRESHOLD_UPDATE` and
  every PB_FLAGS bit are clear: the client loads the thresholds through the descriptor only.
- Our kernel's descriptor before its first render (render-pending-counts): dwords 0-3 and 5-13
  equal the default closed ones (0x422 pages, the same free-list words and thresholds), dword 4
  and dword 14 are our addresses. After the render the firmware has moved the current free list
  (0x04220003) and the allocated and local counts (2). Our fresh run (render-closed-compare)
  reads the same: dwords 1-3 0x422, 0x04220001, 0x04210000 and dwords 10-13 0x432, 0x400, 0x400,
  0x300 before the render, the page table at 0x10423000, and after it 0x04220003 and 2, 2.

**What it shows.**

- PB descriptor dword 1 is the page count of the parameter buffer, and the initial free list is
  the count in its high half with 1 in its low half; the TA allocation word starts one page
  below the count [CAP].
- The TA threshold is the page count plus 16 at both sizes; the ZLS, global and PDS thresholds
  are 0x400, 0x400 and 0x300 at the default size and 64, 64 and 0 at 98 pages, which no single
  rule over two sizes pins [CAP].
- The block's third word holds the descriptor's own address in the closed client's block, not a
  page of the buffer; our kernel's block holds the same (the linux fork's PB block writer puts
  the descriptor's address there) and its renders are exact, so the reading of
  `pb_block.first_page` as a first page the page-table builder fills does not fit either
  stack's value [CAP].
- Our default PB is the closed driver's default, threshold for threshold [CAP][HW].
- How PBSize maps to 98 pages for both 1 MiB and 8 MiB is not shown.
