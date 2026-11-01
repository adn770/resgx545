+++
id = "E304"
claim = "Render details dword 54, not TA command dword 16, points at the RT data set the firmware counts a scene in: moved by 0xc it makes the kernel report a parameter buffer overflow, after one render and after a scene's geometry kick, so a count lands in the set's partial-render word; moved by 0x8 it turns one render's cleanup from completing to failing and a two-kick scene's from failing to completing; moving dword 16 by either changes nothing; unpoked, a scene of two kicks fails its RT data set cleanup and one render's completes; that the cleanup waits for the executed count to equal the kernel's pending count, which our kernel raises once per scene (DDK: linux fork, sgxfive_render.c), with a kick that is not the scene's last adding one (RE, E156) and a render with render flag bit 10 adding one (RE, E164), is the reading that fits these outcomes [infer]: no case read the counts; one run"
unit = "render"
method = "probes/render/rtds-words.toml on the laptop, linux fork with the debug option on: its script rtds-words.sh runs sgxfive-test tri with one render and with a scene of two kicks (the first geometry only), unpoked and with render details dword 54 (rd:54) or TA command dword 16 (ta:16), both the kernel's RT data set address, flipped by 0x8 or 0xc on the first job through the kernel poke; the kernel reports a nonzero partial-render count after a job as a parameter buffer overflow; the last context cleanup's trace (debugfs render_cleanup) after each; read with ta_words.py states"
tiers = ["HW", "DDK", "RE", "infer"]
date = "2026-11-02"
data = ["render-rtds-words"]
terms = [
    "hw_render_details.count_rt_data_set", "hw_rt_data_set.executed_count",
    "hw_rt_data_set.num_out_of_mem_signals", "hw_rt_data_set.num_spm_renders",
    "FRAG_FLAGS.BIT10",
]
+++

**What runs.** The kernel puts the RT data set (0x32411300) in TA command dword 16 and in render
details dword 54, words no EDM path is typed for (edm_dataflow.md reads dword 54 as an untyped
pointer four times and never reaches dword 16). The set's dword 1 is `executed_count`, dword 3
the out-of-memory count and dword 4 the partial-render count (E156, E160) [RE]; the kernel zeroes
dwords 3 and 4 before each job and fails a job whose dword 4 is not zero afterwards. It adds
one to the pending count, which the set's dword 0 points at, once per scene, at the scene's first
job, not once per kick [DDK: our kernel's source, linux fork, sgxfive_render.c]. A kick that is
not the scene's last adds one to `executed_count` at its finish, and a render with render flag
bit 10 at its completion [RE: E156, E164]. Flipping a pointer by 0x8 or 0xc moves the set's dword
1 onto its dword 3 or dword 4.

**Results.**

| case | job | cleanup |
|---|---|---|
| one render, unpoked | ok | completes |
| two kicks, unpoked | ok, ok | fails (-110) |
| one render, rd:54 ^ 0x8 | ok | fails |
| one render, rd:54 ^ 0xc | overflow reported | fails |
| two kicks, rd:54 ^ 0x8 on the geometry kick | ok, ok | completes |
| two kicks, rd:54 ^ 0xc on the geometry kick | overflow reported on the first | fails |
| one render, ta:16 ^ 0x8 or ^ 0xc | ok | completes |
| two kicks, ta:16 ^ 0x8 or ^ 0xc on the first | ok, ok | fails |

Every completed render draws the control's image. A failed cleanup makes the kernel reset the GPU
(kernel log), and the next case runs normally.

**What it shows.**

- Render details dword 54 is the RT data set the firmware counts in: moved by 0xc, a render and
  a geometry kick both put a count in the word the kernel reads as the partial-render count, and
  the kernel reports an overflow [HW]. That the count is `executed_count`, landing four bytes
  after the word pointed at, is the RE reading (E156, E164). Moved by 0x8 it changes only the
  cleanup's outcome [HW]; where that count lands is not observed. TA command dword 16 is not used
  for the count, nor for anything these jobs show [HW].
- A scene of two kicks fails its RT data set cleanup, and one render's completes [HW]. These
  outcomes, with the rd:54 ^ 0x8 ones, fit a cleanup that waits for the executed count to equal
  the pending count, given the kernel's one per scene [DDK] and the geometry kick's count [RE:
  E156] [infer]. No case read the counts (Q029 plans the read). If the reading holds, the
  kernel's pending count of one per scene fails the cleanup of every scene of several kicks.
