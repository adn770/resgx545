+++
id = "E235"
claim = "CR_ISP_CTL's threshold applies to the plain triangle of pass type 0 only among the pass types run here: with the object's ISP1 value at 0 or 63 and the threshold at 1 or 63, pass types 2, 4, 5 and 6 draw in all 16 cases, while pass type 0 draws only with the value at 63"
unit = "isp"
method = "the probes isp-valid-id-vidpass-p<T>-c<C>-i<I> of probes/isp/valid-id.toml, the plain 64x64 triangle (pix_op.s, green) with ISP0 pass type T in 0, 2, 4, 5 and 6, render command word 12 = 0x000f0100 | C for C in 1 and 63 and ISP word 1 bits 31:26 = I in 0 and 63 (20 cases), one probe a case, fenced, on the laptop with the linux fork and the debug option on, one run (no follow-up run)"
tiers = ["HW"]
date = "2026-11-02"
data = ["isp-valid-id"]
terms = ["CR_ISP_CTL", "ISP1", "ISP0.PASS_TYPE"]
+++

**Results.** A case draws the 1062 pixels of the triangle over 3034 of the background, or none.
Every probe completed and every baseline before and after one was clean.

| pass type | C = 1, I = 0 | C = 1, I = 63 | C = 63, I = 0 | C = 63, I = 63 |
|-----------|--------------|---------------|---------------|----------------|
| 0 | not drawn | drawn | not drawn | drawn |
| 2 | drawn | drawn | drawn | drawn |
| 4 | drawn | drawn | drawn | drawn |
| 5 | drawn | drawn | drawn | drawn |
| 6 | drawn | drawn | drawn | drawn |

**What it shows.** The comparison of E233 applies to pass type 0, and to type 1 by E232. Types 2,
4, 5 and 6 ignore the threshold and their own ISP1 value at the four combinations run. Whether
they use ISP word 1 bits 31:26 for anything else is not shown.

**Not shown.** Pass types 1, 3 and 7 in this table (type 1 is in E232), other
values than 0 and 63, and other state. The data come from one run.
