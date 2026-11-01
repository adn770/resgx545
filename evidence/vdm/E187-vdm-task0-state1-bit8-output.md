+++
id = "E187"
claim = "VDM_TASK0 bits 31:28 at 7, 1 and 0 and VDM_STATE1 bit 8 set leave the saved render memory (parameter buffer and TA data) byte for byte the same as the plain triangle's, in the runs that have them; neither field reaches what the TA writes for this triangle"
unit = "vdm"
method = "the probe jobs vdm-task-7, -1 and -0 of probes/vdm/vertex-tasks.toml (VDM vertex-task word 0 bits 31:28) and vdm-state-bit8 and vdm1-default of probes/vdm/state1.toml, each with the render memory dumped after the job, compared byte for byte, on the laptop, linux fork with the debug option on; the state1 jobs ran twice (the second is the follow-up run), the vertex-task jobs once"
tiers = ["HW"]
date = "2026-11-01"
data = ["vdm-vertex-tasks", "vdm-state1", "vdm-state1-followup"]
terms = ["VDM_TASK0.MAX_VERTICES", "VDM_STATE1.BIT8"]
+++

**What runs.** The triangle job's vertex task word is `vdm:6` (VDM_TASK0 in the glossary); the
sweep and the three probe jobs set its bits 31:28 to 7, 1 and 0 (the job writes 15). The
state1 probe `vdm-state-bit8` sets VDM state word 1 bit 8 on top of the host's word, and
`vdm1-default` is the control with the host's word. All of these use the copy-o0 pixel program
and the 64x64 triangle. After each job the parameter buffer (4603904 bytes) and the TA data
(24576 bytes) are saved.

**Results.** The five dumps `vdm-task-7`, `vdm-task-1`, `vdm-task-0`, `vdm-state-bit8` and
`vdm1-default` are byte-identical in both files. The two state1 dumps are byte-identical in the
first run and the follow-up run, and to the vertex-task dumps (which ran once). Each holds the
drawn triangle's object, its control-stream page and seven streams. The sweep over all 16 values
of bits 31:28 draws the baseline image in each (E060); the dumps cover three of the values.

**Not shown.** The other 13 values of bits 31:28 were not dumped, so for them only the image
agrees (E060). One triangle of three vertices is drawn, so a field that matters only for larger
vertex counts or for several tasks does not show here: the field's name, MAX_VERTICES, is a
glossary term that this run does not test. Neither field is shown to be ignored by the TA in
general, only to leave this job's output unchanged.
