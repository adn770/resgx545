+++
id = "E186"
claim = "After the jobs with VDM state word 1 bits 15:13 at 0, 5 or 6 hang, the saved render memory holds no object in either run, as does the three-index lines job; but a job hung in its pixel task leaves its object in the first run and none in the follow-up run, so a missing object does not show that the TA stopped before writing it"
unit = "vdm"
method = "the probe jobs of probes/vdm/state1.toml that hang (bits 15:13 = 0, 5 and 6 of VDM state word 1, lines from three indices, and a job hung in its pixel task as the control) with the parameter buffer and TA data saved after the failure, on the laptop, linux fork with the debug option on; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["vdm-state1", "vdm-state1-followup"]
terms = ["VDM_STATE1.BITS15_13", "VDM_STATE1.BITS11_9"]
+++

**What runs.** Five probe jobs hang the 64x64 triangle job: VDM state word 1 with bits 15:13 =
0, 5 and 6 (`vdm-state-15-13-0`, `-5`, `-6`), the index list with three indices for lines
(`lines3`, VDM word 2 changed), and the control `hang-pixel`, which replaces the pixel program by
one that hangs the pixel task. Each fails with "job hung, context lost (Connection timed out)".
After the failure the probe saves the parameter buffer (4603904 bytes) and the TA data (24576
bytes) of the render context, as for a completed job. The drawn triangle, for comparison, leaves an
object at the first page of the parameter buffer and a control-stream page at 0x1000 (E185).

**Results.**

- Bits 15:13 = 0, 5 and 6: in both runs the parameter buffer holds only the three pages common to
  every dump (0x422000, 0x423000, 0x463000), no object and no stream page, and the TA data is all
  zero. The three dumps are byte-identical to each other in each run.
- Lines from three indices: no object and no stream page in either run. The TA data is all zero in
  the first run; in the follow-up run it is non-zero and byte-identical to the TA data of the
  drawn triangle (seven streams in a region list of 64 headers), while the parameter buffer still
  holds no object.
- The control, a job hung in its pixel task: in the first run the parameter buffer holds the
  object and the stream page (81 non-zero dwords in the first two pages); in the follow-up run
  it holds neither, as for the other hangs. Its TA data is zero in both runs.
- Bits 11:9 = 7: in the probe job it completes and its dump is the drawn triangle's in both runs
  (E185); the sweep that hangs on the same value is E060's, and E413's alternation is the
  difference.

**What this shows.** The first run fits "the job stops before the TA writes the object": the pixel
hang leaves its object and the other four leave none. The follow-up run does not repeat that
control (the pixel hang leaves none), so what a hung job leaves in the saved memory is not
reproducible across the two runs, and a missing object cannot be read as "never written". The
three bits 15:13 values and the three-index lines are consistent with stopping before the TA
writes the object, and are equally consistent with whatever removes the object in the follow-up
control.

**Not shown.** Why the control differs between the two runs, and why the lines job's TA data
differs. What recovery does to the memory, in either run, is not read. That the hang is before
tiling is not established.
