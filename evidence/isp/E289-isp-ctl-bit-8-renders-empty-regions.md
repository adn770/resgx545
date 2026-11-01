+++
id = "E289"
claim = "With CR_ISP_CTL bit 8 clear the 3D skips every 32x16 region the TA left without a control stream, except the scene's last region, leaving its pixels unwritten: 1 region at 96x64, 12 at 128x128, 33 at 256x128, none at 64x64; bits 24 and 19:16 flipped from 0x000f0100 change no pixel at any of the four sizes; one run"
unit = "isp"
method = "probes/isp/isp-ctl.toml on the laptop, linux fork with the debug option on: the library triangle on targets of 64x64, 96x64, 128x128 and 256x128, the target filled with 0xdeadbeef before each render, render-details word 3 (it loads CR_ISP_CTL, a kernel poke) at the job's 0x000f0100, with bit 8, bit 24 or one of bits 16-19 flipped, and 0; every pixel read back, the unwritten pixels counted by region; one run"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-isp-ctl"]
terms = ["CR_ISP_CTL", "CR_ISP_CTL.PROCESS_EMPTY_TILES", "hw_render_details.isp_ctl"]
+++

**What runs.** The triangle job at four sizes, eight values of 0x0414 each. `CR_ISP_CTL` takes
bits 24, 19:16, 8 and 5:0 (E249); bits 5:0 are the valid-ID threshold (E233).

**Results.** At 0x000f0100 and with bit 24 or one of bits 16-19 flipped, every pixel is written:
the triangle (1062, 1620, 4284 and 8640 pixels) and the background. With bit 8 clear, and with
the word at 0:

| target | pixels left 0xdeadbeef | 32x16 regions |
|---|---|---|
| 64x64 | 0 | 0 of 8 |
| 96x64 | 512 | 1 of 12 |
| 128x128 | 6144 | 12 of 32 |
| 256x128 | 16896 | 33 of 64 |

Each unwritten area is a whole 32x16 region with no triangle pixel. Some regions with no triangle
pixel are still written: the scene's last region, and regions the TA's region test binned the
triangle into without a covered pixel (E180).

**What it shows.** Bit 8 makes the 3D process the regions that have no stream; clear, it skips them
and their pixels keep what the target held, so the background object is not drawn there. The last
region of the scene is processed either way (at 64x64 it is the only empty one). That is Rogue's
`CR_ISP_CTL.PROCESS_EMPTY_TILES` (C0713, C0714), and it answers the first half of Q029 [infer:
"except the last region" from three sizes]. Bits 24 and 19:16 do nothing visible here.
