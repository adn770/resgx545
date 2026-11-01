+++
id = "E050"
claim = "Of the kernel-built render flags word of the triangle job (ta:7), bit 0 hangs the job, bits 1 and 4 complete it with no pixel written, bits 5 and 9 and the value 0xffffffff fault, and the other bits and the value 0 change nothing; the two fresh runs agree on every bit"
unit = "render"
method = "kernel-poke sweep of probes/render/kernel-words.toml (tri-kernel, word ta:7) on the laptop, linux fork with the debug option on: the 64x64 triangle job, 34 values of the word, run twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-kernel-words", "render-kernel-words-followup"]
terms = [
    "cmd_ta.frag_flags", "FRAG_FLAGS.ABORT", "FRAG_FLAGS.SET_ZLSCTL_BIT0", "FRAG_FLAGS.NO_RENDER",
    "FRAG_FLAGS.GET_VIS_RESULTS", "FRAG_FLAGS.TA3D_DEPENDENCY",
]
+++

**What runs.** The kernel builds the render flags into word 7 of the TA command of the triangle job,
and a `kpoke` armed before the job flips a bit of it in the command the kernel builds for the job.
The sweep gives the word each of its 32 bits flipped alone, the value 0 and the value 0xffffffff, a
fresh context each, after an unpoked baseline. The kernel poke applied in all 34 cases.

**Results.** The baseline draws 1062 triangle pixels and 3034 background (hash
0x99385a04ee01c585). Of the 34 values:

- Bit 0 (`^=0x1`): the job hangs, the context is lost.
- Bits 1 (`^=0x2`) and 4 (`^=0x10`): `job: ok`, no pixel written. All 4096 pixels keep the
  sentinel (0xdeadbeef) and the hash is 0xe4364b426cdce325 in both cases.
- Bits 5 (`^=0x20`) and 9 (`^=0x200`): the job faults and the context is lost. The value
  0xffffffff faults too.
- The other 27 single-bit flips, bit 10 among them, and the value 0 give the baseline image.

The follow-up run of the same sweep gave every one of these 34 results again. The visibility
counters stayed at 0.

**Not shown.** What the words' bits are called or do inside the firmware is not visible from
the image; the sweep shows the outcome only. The fault of bits 5 and 9 is a stall of the job,
and its cause (which unit raises it) is not looked at here. E057 shows the same outcome as bit 4
from the ZLS control word.
