+++
id = "E067"
claim = "0x0418, 0x04dc, 0x04e8, 0x0520 and 0x0800, held through a plain copy, the every-value copy, a UYVY copy through colour-space set 0 and a fill, change no pixel: 34 values of each (every implemented bit flipped, 0 and ~0) in each of the four jobs; on a textured 3D triangle 70 pokes of the same registers, every implemented bit and 0 and ~0, give the unpoked image (up to five of them may not have been applied)"
unit = "isp"
method = "four sweeps of probes/isp/render-only-registers.toml through the kernel's kreg debugfs file (host copy, copy --every-value, the UYVY copy, fill), 171 jobs each, the registers sampled around every job, on the laptop with the linux fork and the debug option on; one run; and the textured_triangle function of the hand script render-only-registers.sh with its probe programs staged (the textured 3D triangle, 70 kernel pokes)"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-render-only-registers"]
terms = [
    "CR_ISP_LINE_SAMPLE_POS", "CR_ISP_REG_04DC", "CR_ISP_REG_04E8", "CR_ISP_SAMPLE_POS",
    "CR_REG_0800",
]
+++

**What runs.** A register written through kreg stays across the job that follows. For each of the
five registers the sweep writes every bit of the mask the read-back showed implemented (flipped from
the held value), 0 and ~0: 34 values a register, 170 jobs, plus the baseline. The four host jobs are
a plain RGBA8888 copy, the every-value copy, a UYVY copy (texture type and transfer words poked to
set colour-space set 0) and a 64x32 fill, which has no texture and is the control.

**Results.** 170 of 171 jobs in each sweep give the baseline image (the 171st is the baseline
itself): no value of any of the five registers changes what a copy samples, converts or writes, or a
fill. The baseline hashes are 0x9b1c0be484ac0d25 (copy), 0x88c655df5891e325 (every-value),
0xb6067a95fa98de2d (UYVY) and 0xb60c6095080bd325 (fill). The job changed a held register in 0 of the
34 cases of every register in every sweep, and the visibility counters stayed at 0.

The read-back, the same in the four sweeps, gives each register's implemented bits and what it held
before the case:

| register | held | bits that took a write |
|---|---|---|
| 0x0418 | 0x00000001 | 0x00000001 |
| 0x04dc | 0x00000000 | 0x00000007 |
| 0x04e8 | 0x00000100 | 0x00000101 |
| 0x0520 | 0x00000000 | 0xffffffff |
| 0x0800 | 0x00000030 | 0x00ffff3f |

**Textured 3D triangle.** The same registers were then poked, through the kernel's render-details
poke (rd:26, rd:21, rd:51, rd:19, rd:22), around a textured 3D triangle (sampling, wrap and the
twiddled fetch): bit 0 of 0x0418, bits 0 to 2 of 0x04dc, bits 0 and 8 of 0x04e8, all 32 bits of
0x0520, the 22 implemented bits of 0x0800, and 0 and ~0 of each: 70 jobs. The unpoked image was
hashed twice and agrees; no poked job gave another hash. The loop does not report a refused poke,
and the script's error output holds five "Invalid argument" lines from the kernel's poke file that
no case is attributed to, so up to five of the 70 may have run unpoked.

**What it does not show.** The held value of 0x0418 is 1 here; what the register holds outside a
render depends on the renders run before in the boot. The textured triangle result is one image hash
per job, not a pixel comparison, and a texture format or filter other than that probe's was not
tried. Nothing here says what the registers do in a render (E066, E068).
