+++
id = "E232"
claim = "Any of CR_ISP_CTL bits 5:0 set (the values 1 to 8, 16, 32 and 63) removes a triangle of ISP0 pass type 0 or 1 (opaque and translucent) and leaves pass types 2, 4, 5 and 6 drawn exactly, in all 72 cases of one run; the value 0 draws all six"
unit = "isp"
method = "the probes isp-valid-id-upass-p<T>-c<V> of probes/isp/valid-id.toml, the plain 64x64 triangle (pix_op.s, green) with ISP0 pass type T in 0, 1, 2, 4, 5 and 6 (ISP0 0x01d00200 for type 0, the type field changed for the others) and render command word 12 = 0x000f0100 | V for V in 0 to 8, 16, 32 and 63, one probe a case, fenced, on the laptop with the linux fork and the debug option on, one run (no follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-valid-id"]
terms = ["CR_ISP_CTL", "ISP0.PASS_TYPE"]
+++

**What runs.** 72 probes, six pass types by twelve values. Command word 12 is CR_ISP_CTL; in
our renders it is 0x000f0100 (E231), so V is the value of its bits 5:0.

**Results.** A case draws all 1062 pixels of the triangle over 3034 of the background, or none
(only the background, 0xff203040 over 4096 pixels).

| ISP0 pass type | V = 0 | V = 1 to 8, 16, 32, 63 |
|----------------|-------|------------------------|
| 0 | drawn | not drawn (11 of 11) |
| 1 | drawn | not drawn (11 of 11) |
| 2, 4, 5, 6 | drawn | drawn (11 of 11 each) |

Every probe completed and every baseline before and after one was clean (0 of 4096 pixels).
Pass types 3 and 7 were not run.

**What it shows.** The value does not act as a threshold on the pass type: pass type 0 vanishes
at V = 1 while pass type 6 survives V = 63. The bits act by pass type: they turn off types 0
and 1 and leave 2, 4, 5 and 6 as they are. One reading is a per-render switch that drops the
ordinary hidden-surface objects; another is a validation value that objects of types 0 and 1
must meet (E233) **[infer]**. This record does not tell them apart.

**Not shown.** Pass types 3 and 7, other pass types' behaviour with state other than the plain
triangle, and values other than the twelve. The data come from one run.
