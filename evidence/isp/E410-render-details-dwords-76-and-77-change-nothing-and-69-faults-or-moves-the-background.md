+++
id = "E410"
claim = "On the one-triangle job, the render details dwords 76 and 77 (the background object's second and third words) at every single-bit flip, 0 and 0xffffffff change nothing (68 of 68 runs, the image of the control); dword 69 (its first word, 0x32411214) with 11 of its 32 bits flipped draws the same wrong image (2860 of 4096 pixels), with the other 21 fails the job (19 faults and 2 hangs), and with 0 or 0xffffffff faults it"
unit = "isp"
method = "probes/isp/bg-words.toml (bg-words.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the control values read from tri --words (rd:69 0x32411214, rd:76 0x04000004, rd:77 0x00030000), then each bit flipped, 0 and 0xffffffff through --kpoke-render, one job each (104 jobs with the controls), 64x64"
tiers = ["HW"]
date = "2026-11-07"
data = ["isp-bg-words"]
terms = ["CR_ISP_BGOBJVALS", "hw_render_details.pds_bgnd"]
+++
 **What was seen.** rd:76 and rd:77: the 68 jobs (32 bits, 0 and 0xffffffff each) all drew the
control's image (hash 0x99385a04ee01c585, 0 wrong). rd:69: flipping bit 2, 3, 5, 6, 7, 9, 10, 11,
12, 16 or 22 gave one image for all eleven (hash 0xd0530839d87ea325, 2860 of 4096 pixels wrong, the
background pixels 0xff00ff00 where 0xff203040 belongs); flipping any of the other 21 bits, and the
values 0 and 0xffffffff, failed the job (19 bit flips faulted, bits 4 and 8 hung it, and 0 and
0xffffffff faulted: 21 BIF fault lines in the kernel log). The control after the series drew
exactly.

**What it shows.** The first word is the one the background pixel program is started from
(0x32411214; E301 reads word 23 of the render command as the background object's first PDS word);
the second and third words, as poked at the render details, do not reach the ISP in a way this job
shows [infer: the EDM writes them from other words, or the job does not read them].

**What it does not show.** What the second and third words mean to the ISP; the pixels each bit of
the first word moves the program to.
