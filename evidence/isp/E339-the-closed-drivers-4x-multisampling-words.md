+++
id = "E339"
claim = "A multisampled texture render of the closed driver, asked for 2 or 4 samples, moves seven register words, and bit 48 of one instruction of the end-of-render program's second task, against the same render single-sampled: CR_ISP_MSAA mode 2 (0x80000002), CR_ISP_MULTISAMPLECTL and the TA's CR_MTE_MULTISAMPLECTL 0xeaa26e26 (samples at (6, 2), (14, 6), (2, 10), (10, 14) sixteenths), CR_TE_AA 0xe0000000 (bits 31:29), CR_TE_MTILE1 and CR_TE_MTILE2 0x00802002 (0x01004004 single-sampled) and CR_TE_MACROTILE_STRIDE 4 (0x10); CR_ISP_SAMPLE_POS stays 0, and alpha to coverage and sample coverage move no word; a multisampled texture with a depth attachment is refused (incomplete) and renders single-sampled"
unit = "isp"
method = "the render-register-gaps capture (render to a 64x64 texture with 0, 2 and 4 samples, and 4 with a depth attachment) and the isp-registers capture (4 samples with alpha to coverage, sample coverage 0.5 and its inverse), read with harness/ukernel-extract/diff3d.py and state3d.py: the texture render's TA command and render details against the single-sampled texture render"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-register-gaps", "isp-registers"]
terms = [
    "CR_ISP_MSAA", "CR_ISP_MSAA.MODE", "CR_ISP_MULTISAMPLECTL", "CR_MTE_MULTISAMPLECTL",
    "CR_ISP_SAMPLE_POS", "CR_TE_AA", "CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE",
]
+++

**What runs.** tri's `fbo=64x64 fbosamples=N` renders the triangle into a 64x64 texture through a
multisampled framebuffer (the closed driver's `IMG_multisampled_render_to_texture`), then draws
the texture into the pbuffer. Kicks 0 and 1 are the texture's scene, kicks 2 and 3 the pbuffer's.

**Results.** `diff3d.py` of the texture's two kicks, 4 samples against none:

| word | single-sampled | 4 samples |
|---|---|---|
| `CR_TE_AA` | `0x20000000` | `0xe0000000` |
| `CR_TE_MTILE1`, `CR_TE_MTILE2` | `0x01004004` | `0x00802002` |
| `CR_TE_MACROTILE_STRIDE` | `0x10` | `0x4` |
| `CR_MTE_MULTISAMPLECTL` (TA command) | `0x88` | `0xeaa26e26` |
| `CR_ISP_MULTISAMPLECTL` (render details) | `0x88` | `0xeaa26e26` |
| `CR_ISP_MSAA` | `0x80000000` | `0x80000002` |

Besides these, in both kicks, only bit 48 of one instruction of the end-of-render program's second
USSE task differs; not `CR_TE_SCREEN` (`0x3001`), not `CR_ISP_SAMPLE_POS` (0), not the ISP words,
not the other programs and not the end-of-tile words (E333). 2 samples give
the words of 4, word for word. Alpha to coverage and sample coverage 0.5, plain or inverted, give
4 samples' words with no difference at all. With a depth attachment the framebuffer is incomplete
(`GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE`), and its render is single-sampled.

**What it shows.**

- The closed driver's only multisample mode is 4x as a 2x2 block (`CR_ISP_MSAA.MODE` 2, §11.7),
  with the enable bit set as in every render [CAP].
- Its sample positions are bytes 0 to 3 of `CR_ISP_MULTISAMPLECTL`, x in bits 3:0 and y in bits
  7:4: (6, 2), (14, 6), (2, 10) and (10, 14) sixteenths of a pixel, a rotated grid; the TA's
  `CR_MTE_MULTISAMPLECTL` gets the same word [CAP; the byte layout from §11.7's runs].
- The TE's macrotile words halve (`0x01004004` to `0x00802002`) and its macrotile stride drops from
  16 to 4 while the screen word stays: the TA tiles the doubled sample grid in the same 64x64
  screen [CAP; the reading: infer].
- `CR_TE_AA` gains bits 31 and 30 beside 29; §11.7 saw bits 31 or 30 without 29 remove a
  triangle, and here all three come together [CAP].
- Alpha to coverage and sample coverage are not render-level state in these captures: if the
  driver honours them it does so in the pixel program or not at all [CAP; Q089].
