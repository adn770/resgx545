+++
id = "E305"
claim = "CR_TE_PSG reads 0x01400000 after every unpoked job (the kernel's 0x00400000 with bit 24, which the TA kick ORs in); with bit 21 set in the TA command's word the register keeps it and the TA sets bit 29 of word 0 of every target region's header, changing nothing else of its output and no pixel; bit 24 already set changes nothing; the word at 0 makes the job fault; CR_DPM_STATE_CONTEXT_ID reads 0 after one render, two renders and a scene of two kicks; one run"
unit = "ta"
method = "probes/ta/te-psg.toml on the laptop, linux fork with the debug option on: its script te-psg.sh runs sgxfive-test tri with CR_TE_PSG (0x0218) or CR_DPM_STATE_CONTEXT_ID (0x0630) read back after the job (--regs, read-only) for one render, two renders and two kicks; then one render with the TA command's te_psg word (ta:147, a kernel poke) at 0x01400000, 0x00600000, 0x01600000 and 0, the register read back and the render memory dumped (--dump-render); dumps compared with pbdump.py --diff"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["ta-te-psg"]
terms = ["CR_TE_PSG", "cmd_ta.te_psg", "REGION_HDR.FLAGS", "CR_DPM_STATE_CONTEXT_ID"]
+++

**What runs.** The kernel writes 0x00400000 to the TA command's te_psg word on a scene's last
kick and 0 otherwise. The TA kick ORs in bit 24, and bit 21 when the RT data's state bit 8 is
set (E158); our RT data never has bit 8, so bit 21 is set here through the command instead.

**Results.**

| te_psg in the command | CR_TE_PSG after | job | TA's output against the control |
|---|---|---|---|
| 0x00400000 (control) | 0x01400000 | ok | |
| 0x01400000 | 0x01400000 | ok | byte for byte the same |
| 0x00600000 | 0x01600000 | ok | word 0 bit 29 set in the 8 target region headers |
| 0x01600000 | 0x01600000 | ok | as 0x00600000 |
| 0 | 0x01000000 | faults, every pixel at the sentinel | |

With bit 21 the eight headers of the 64x64 target (regions with and without a stream) gain
0x20000000 in word 0; the parameter buffer and every other TA data dword are unchanged, and the
image is the control's. CR_TE_PSG reads 0x01400000 after the unpoked jobs of one render, two renders
and two kicks, and CR_DPM_STATE_CONTEXT_ID 0 after the same three.

**What it shows.** Bit 21 of CR_TE_PSG makes the TA mark every region header of the target with
`REGION_HDR.FLAGS` bit 29; what the mark does in the 3D, with an RT data whose state bit 8 is set,
is not shown. Bit 24 is set on every kick, so its effect cannot be seen by setting it. The command's
word at 0 faults the job; that it faults for want of bit 22, which the kernel sets on a scene's last
kick, is a reading [infer: one value, 0, which clears every bit]. The DPM slot register is 0 once
the job is over, so whether its bit 1 is the 3D's slot is not readable after a job.
