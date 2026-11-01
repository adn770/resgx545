+++
id = "E054"
claim = "Of the kernel-built words of the triangle job's TA and render-details commands, changing a layout word (ta:143, 144, 146, 147, rd:74, rd:75) faults the job for most bits, ta:5 hangs for bits 0 and 2, 0 and 0xffffffff, ta:154 at 0 removes the triangle, and the 12 register words that are zero in the job (ta:155, 156, 158 to 166, 168) change nothing at any value tried; ta:167 faults for bit 8 and for 0xffffffff; two cases (ta:147 bit 20, ta:154 bit 1) differ between the two fresh runs"
unit = "ta"
method = "kernel-poke sweep of probes/render/kernel-words.toml (tri-kernel, run twice, the second being the follow-up run) and the zero-word runs of probes/ta/zero-words.toml (register readback and value dumps) on the laptop, linux fork with the debug option on: the 64x64 triangle job, 34 values per word (each bit flipped alone, 0 and 0xffffffff)"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-kernel-words", "ta-zero-words", "render-kernel-words-followup"]
terms = [
    "cmd_ta.dpm_reg_074c", "cmd_ta.mte_rhw_min", "cmd_ta.mte_rhw_clamp", "cmd_ta.use_reg_0a04",
    "cmd_ta.use_reg_0aa0", "cmd_ta.ta_reg_02b0", "cmd_ta.ta_reg_02b4", "cmd_ta.ta_reg_02d0",
    "cmd_ta.ta_reg_02d4", "cmd_ta.reg_0324", "cmd_ta.reg_0364", "cmd_ta.reg_0368",
    "cmd_ta.reg_0370", "cmd_ta.reg_0374", "cmd_ta.te_reg_02a8",
]
+++

**What runs.** The kernel builds the TA command (words `ta:N`) and the render details (words `rd:N`)
of the triangle job itself, and a `kpoke` armed before the job changes a word in the command the
kernel builds. The sweep (2313 cases, 1600 s) gives each word 34 values; the kernel poke applied in
every case. It ran twice, 1600 s and 1622 s, and of the 2313 cases the two runs differ in two
(below). The zero-word script loads the words that the job leaves zero with 0xffffffff and reads
back the register each one goes to (`--regs`), and dumps the render memory after each of the values
1, 0x80000000 and 0xffffffff for words ta:152 to ta:168. The baseline draws 1062 triangle pixels and
3034 background (hash 0x99385a04ee01c585).

**Results.**

- Layout words. `ta:143` faults for bits 14, 17, 18, 19, for 0 and for 0xffffffff; `ta:144` for
  bits 14 and 17 to 20, 0 and 0xffffffff; `ta:146` for bits 4 and 8 to 17, 0 and 0xffffffff;
  `ta:147` for bits 0, 1, 19, 22, 0 and 0xffffffff, and bit 20 in the follow-up run only (the first
  run gave the baseline image). Every other bit of these words changes nothing. `rd:74` and
  `rd:75` fault for each of the bits 2 to 31 (30 cases a word); their bits 0 and 1 and the
  values 0 and 0xffffffff do not fault. The faulting jobs lose the context.
- `ta:5`: bits 0 and 2, 0 and 0xffffffff hang the job, the other bits change nothing.
  `ta:6` and `ta:8` change nothing at any value.
- `ta:154`: bit 0 faults, the value 0 completes with no triangle pixel (4096 background, 936
  pixels differ from the baseline, hash 0xfc5ff15e0434a325, the image of E060's removed
  triangle), and bit 1 faulted in the first run and gave the baseline image in the follow-up run.
- The register words `ta:155`, `ta:156`, `ta:158` to `ta:166` and `ta:168`: no value changes
  the image, 34 values each, both runs. The registers they load read back, after a job with
  0xffffffff, the implemented bits only: 0x0a04 0xfffffff0, 0x0aa0 0xffffffff, 0x02b0
  0xff000000, 0x02d4 0x03ffffff, 0x02d0 0xfffffffc, 0x02b4 0x000000ff (the baseline job
  already reads that), 0x0324 0xfffffff0, 0x0368 0x00007fff, 0x0364 0xffffffff, 0x0370
  0xffffffff, 0x0374 0xffffffff, 0x02a8 0x000ff000, for ta:155, 156, 158 to 166 and 168 in that
  order. After an ordinary job all of them read 0 except 0x02b4.
- `ta:167`: bit 8 and 0xffffffff fault the job, in both runs; its other 32 values change
  nothing. In the value dumps, `ta:152` and `ta:153` (the two floats before the zero words) at
  1, 0x80000000 and 0xffffffff complete (`job: ok`), as does every word of ta:155 to ta:168 at
  those values except ta:167 at 0xffffffff; those runs compare no pixels.

**Not shown.** Why the layout words fault is not looked at. The variable cases: `ta:147` bit 20
and `ta:154` bit 1 each gave a fault in one run and the baseline image in the other, so no class
is stated for them. The visibility counters stayed at 0 in all runs.
