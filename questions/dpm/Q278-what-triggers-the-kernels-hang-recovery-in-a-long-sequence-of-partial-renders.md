+++
id = "Q278"
question = "what triggers the kernel's hang recovery (`job N hung, recovering`) in a job that takes many partial renders: the number of partial renders, the time since the job began, or a register that stops changing, and what does the recovery do with a job that overflows (E706)"
unit = "dpm"
kind = "kernel"
phase = 11
evidence = ["E630", "E706"]
terms = ["Dynamic Parameter Management (DPM)"]
+++
Split in 11.39 from Q103 (merge 15): the kernel-kind part of its open list; Q103 keeps the hardware
part (why a scene takes 35 or more partial renders). E706: without `hold_recovery` the 300-vertex
scene at 4096x4096 in 0x40 pages (2 of 2) logs `job N hung, recovering` and ends `job hung, context
lost` after 35 partial renders, with the registers 0 after the reset; with it the line and `recovery
held` are logged and the job ends as an overflow after 47 partial renders (2 of 2); E630 saw the
line
in two of three of E438's cases. The length alone does not separate the logged jobs from the others
(1.03 and 1.38 s against 0.50 s here and up to 1.40 s in E630); the partial render counts (35, 47
and 92 against 16 and 22 to 33) are where the jobs ended, not thresholds, with the time confound not
separated. What it asks is the design of the driver's watchdog: what it samples, its period and its
limit, and why it fires on a job the hardware is still advancing. To settle it: the watchdog's code
and period in the kernel, and the same scene at partial render counts below and above 35 with a
timeline of the registers the watchdog reads.
