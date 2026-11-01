+++
id = "E408"
claim = "With CR_ISP_CTL (render details dword 3, rd:3) at the closed driver's 0xf0000 (bit 8 clear) our triangle job leaves 36352 of 65536 pixels at 256x256 and 542720 of 786432 at 1024x768 as the tool's sentinel, three runs each with the same count, and none at 64x64; 0x04c4 (rd:18) at the closed driver's 0x2046400 changes neither the image nor the time at any of the three sizes; the job time rises with the number of pokes, not with the value"
unit = "render"
method = "probes/ta/te-words.toml (te-words.sh, part B) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the triangle at 64x64, 256x256 and 1024x768 as the control, with rd:3 = 0xf0000, with rd:18 = 0x2046400 and with both through the kernel poke (--kpoke-render), three runs each (36 jobs), the job's time and the tool's diff against its reference"
tiers = ["HW"]
date = "2026-11-07"
data = ["ta-te-words"]
terms = ["CR_ISP_CTL.PROCESS_EMPTY_TILES", "CR_ISP_CTL"]
+++

**What was seen.** At 64x64 all 12 jobs drew exactly. At 256x256 the jobs with rd:3 = 0xf0000 (alone
and with rd:18) drew 36352 of 65536 pixels wrong in all three runs, the first wrong pixel (0, 0)
holding 0xdeadbeef, the tool's sentinel for a pixel nothing wrote, where the reference has the
background 0xff203040; the control and the rd:18 jobs drew exactly. At 1024x768 the same: 542720 of
786432 pixels still the sentinel with rd:3 = 0xf0000, none with the control or rd:18 alone. The
wrong images repeat bit for bit within each size (one hash per size and case).

**Times.** The control takes 6.0 ms at 64x64, 73.5 ms at 256x256 and 859 to 866 ms at 1024x768. A
poked job takes longer by an amount that follows the number of pokes at 64x64 (one poke 9.5 to 10.2
ms, two 12.8 to 13.4 ms); at 256x256 the pokes add 2 to 5 ms (one run of rd:18 took 89 ms) and at
1024x768 up to 12 ms, inside the control's own spread there, and a poke that changes nothing adds
the same. So no time effect of either value shows beyond the poke's own cost.

**What it shows.** Bit 8 of CR_ISP_CTL (`PROCESS_EMPTY_TILES`) decides whether tiles with no object
are written: with it clear they keep what the target held, so our job, whose background object
clears the target, needs it set [infer: the unwritten pixels are the tiles without a triangle, which
the count fits at 256x256 only if some tiles hold none; the tiles were not mapped]. At 64x64 no tile
is empty [infer]. Bit 25 of 0x04c4 set changes nothing our job shows.

**What it does not show.** What 0x04c4's bits 25, 8 and 19:12 hold; the pixels' tile map.
