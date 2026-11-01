+++
id = "E331"
claim = "Over 222 render-target sizes from 1x1 to 4096x4096 the closed GLES2 stack's tiling words and size words all follow one rule: 32x16-pixel tiles; n = 4 macrotiles across and down from w x h >= 640 x 480 pixels (640x475 still 2, 640x480 and 4096x75 already 4), else 2; a macrotile spans the tiles over n rounded up to whole 4-tile blocks; CR_TE_SCREEN, CR_TE_MTILE1 (bit 31 for n = 4), CR_TE_MTILE2 and CR_TE_MACROTILE_STRIDE (16 per 4x4-tile block) as tiling3d.py gives them; and in the RT data set the tiles across all macrotiles (header dword 2), the blocks per macrotile (RT data dword 2), a macrotile's region headers (0xc0 per block, dword 3), the tail pointer cache (4 bytes over the square of the power of two that covers the larger macrotile span, dword 9 and the cache object's size) and the region-header buffer (0xc0 per block per macrotile); widths or heights above 4096 fail eglCreatePbufferSurface"
unit = "ta"
method = "the ta-target-sizes capture (sizes3d.txt: 225 pbuffer sizes, 222 that make kicks) of the closed GLES2 stack under the harness, each run's first TA command, RT data set and RT data, and the sizes of the region-header and tail-pointer-cache objects, read with harness/ukernel-extract/state3d.py, kick3d.py and kickwalk.py, and compared with tiling3d.py's layout(w, h); the twelve other capture tables for the 4x multisampled exception; our kernel's rule (linux fork sgx_render_layout) and our library's (userspace/libsgxfive/src/render.c, sgxfive_tiling) compared on the same sizes"
tiers = ["CAP"]
date = "2026-11-03"
data = ["ta-target-sizes", "render-register-gaps", "isp-registers"]
terms = [
    "CR_TE_SCREEN", "CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE", "CR_PPP_SCREEN",
    "CR_TE_TPC_ADDR", "CR_ISP_REGION_HEADER_BASE", "hw_rt_data.num_rts", "CR_TE_AA",
    "hw_rt_data_set.tiles_across", "hw_rt_data.blocks_per_mtile", "hw_rt_data.mtile_region_bytes",
]
+++

**What runs.** One triangle into a pbuffer of each size of sizes3d.txt: 32x16 to 4096x4096
(s*), heights 16 to 4096 at width 64 (h*), widths at height 64 (w*), odd and mixed sizes and
the limits (m*), and the sizes around the four-macrotile threshold (t*). 222 make two kicks;
4097x16, 16x4097 and 8192x16 fail eglCreatePbufferSurface with EGL_BAD_MATCH.

**Results.** For every one of the 222 sizes all nine words below equal tiling3d.py's layout(w, h)
(0 mismatches), and the target's size is `CR_PPP_SCREEN`'s (w - 1) | (h - 1) << 16:

| word | where | rule |
|---|---|---|
| `CR_TE_SCREEN` | TA command | (tiles down - 1) << 12 \| (tiles across - 1) |
| `CR_TE_MTILE1`, `CR_TE_MTILE2` | TA command | the macrotile size in blocks (31:24), the second and third boundaries in tiles (19:12, 11:0); bit 31 of MTILE1 for n = 4 |
| `CR_TE_MACROTILE_STRIDE` | TA command | 16 per 4x4-tile block of a macrotile |
| tiles across | RT data set dword 2 | n x the macrotile's width in tiles (8 to 128) |
| blocks per macrotile | RT data dword 2 | the macrotile's 4x4-tile blocks (1 to 128) |
| macrotile region headers | RT data dword 3 | 0xc0 per block (0xc0 to 0x6000) |
| tail pointer cache | RT data dword 9, the object's size | 4 x side x side, side the power of two that covers n x the larger macrotile span (0x100 to 0x40000) |
| region-header buffer | the object `CR_ISP_REGION_HEADER_BASE` names | 0xc0 per block per macrotile, n x n macrotiles (0x300 to 0x60000) |

Samples: 1x1 and 64x64 give the smallest layout (n = 2, one block a macrotile, 0x300 of
region headers); 640x475 gives n = 2 with 12 blocks a macrotile; 640x480 gives n = 4 with 4;
4096x74 n = 2, 4096x75 n = 4 (area 303104 against 307200); 1366x768 gives `CR_TE_MTILE1`
0x83018024, `CR_TE_MTILE2` 0x3018024, stride 0x90, tiles across 48, 9 blocks, 0x6c0, a
0x4000-byte tail pointer cache; 4096x4096 gives 0x88040060, 0x100800c0, 0x800, 128, 128
blocks, 0x6000, 0x40000 and 0x60000.

- Every other TA register and render-details word holds its 64x64 value at every size
  (`CR_TE_AA` 0x20000000, `CR_ISP_CTL` 0xf0000, 0x04c4 0x2046400, and the rest of E328 and
  E330), apart from the scene's buffer addresses.
- Under 4x multisampling the rule does not hold: a 64x64 multisampled texture target has
  `CR_TE_MTILE1` and `CR_TE_MTILE2` 0x802002 and a stride of 4 (the rule's 0x1004004 and 0x10)
  with `CR_TE_SCREEN` unchanged (render-register-gaps, isp-registers; only that size captured).
- Our kernel's layout (the linux fork's sgx_render_layout) and our library's tiling words
  (libsgxfive sgxfive_tiling) compute the same rule, so every word above is what our stack
  writes for the same size.

**What it shows.**

- The size rule is settled for single-sampled targets over 1x1 to 4096x4096: the TA's screen,
  macrotile and stride words, and the RT data's size words, are functions of the size alone,
  with the four-macrotile threshold at exactly 640 x 480 pixels of area [CAP].
- RT data set dword 2 is the tiles across the macrotile grid, RT data dword 2 the blocks per
  macrotile, dword 3 a macrotile's region-header bytes, dword 9 the tail pointer cache's bytes
  [CAP].
- How 4x multisampling changes the macrotile words over sizes is open (Q086).
