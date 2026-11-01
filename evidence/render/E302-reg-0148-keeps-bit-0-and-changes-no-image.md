+++
id = "E302"
claim = "Render details dword 9, which the 3D kick loads into CR_REG_0148, changes no image at 0xffffffff or with any one of its 32 bits set, in the triangle job and over five overlapping copies; after the job the register reads 1 when bit 0 was set and 0 otherwise; the transfer command's word for the register changes neither a fill nor a copy at any of 34 values; one run"
unit = "render"
method = "probes/render/reg-0148.toml on the laptop, linux fork with the debug option on: its script reg-0148.sh runs sgxfive-test tri with render details dword 9 (rd:9, a kernel poke; the kernel writes 0) at 0xffffffff and at each bit alone, CR_REG_0148 read back after each job (--regs, read-only), an unpoked control before and after; its probe runs the probe's triangle with four copies at rd:9 = 0, 0xffffffff, 0x0000ffff and 0xffff0000, every pixel read back; with the transfer command's tq:16 sweep of transfer-kernel-words (34 values on a fill and a copy)"
tiers = ["HW"]
date = "2026-11-02"
data = ["render-reg-0148", "transfer-kernel-words"]
terms = ["CR_REG_0148", "hw_render_details.reg_0148", "transfer_cmd.reg_0148"]
+++

**What runs.** The 34 values of the word on the library's triangle job, each job's image compared
with the CPU reference and the register read after it; four values over the five-copy job; and,
already in the data, the 34 values of the transfer command's word 16, which loads the same
register on fills and copies.

**Results.** Every triangle job completes with no pixel differing from the reference. The
register reads 0x00000001 after the jobs with bit 0 set (bit 0 alone and 0xffffffff) and
0x00000000 after every other job, the controls included. The five-copy images are those of the
word at 0: 2998 background and 1098 triangle pixels in each of the four. The transfer sweep's
report gives tq:16 unchanged in all 34 cases on the fill and on the copy.

**What it shows.** Only bit 0 of the word reaches the register (as the register census found,
E252), and neither it nor any other bit changes what these jobs draw. Which unit the bit acts
on is not shown by these jobs.
