+++
id = "E357"
claim = "CR_EVENT_STATUS2 bit 7 (TRIG_TA) sets 0.1 to 0.2 ms after the TA kick's PB load in a TA that hangs (VDM state word 1 bits 15:13 = 0) and in one that faults on its stream page, and bit 6 (TRIG_3D) about 0.1 ms after the pixel units start in a fill whose pixel program loops 128 or more times over eight instructions, not with 16; neither sets in any render of one to three renders from 64x64 to 256x256, a 1024x768 partial render, a fill or a copy; once set each stays through later jobs until a reset; a fault raises no other bit of CR_EVENT_STATUS or CR_EVENT_STATUS2"
unit = "platform"
method = "probes/platform/event-timelines.toml and probes/platform/event-trigger.toml on the laptop, linux fork b5a86838ae59 with the debug option on: regtimeline samples CR_CLKGATESTATUS, CR_EVENT_STATUS2, CR_EVENT_STATUS, CR_BIF_INT_STAT, CR_BIF_FAULT and eight DPM registers (event-timelines) or the first three (event-trigger) from 50 ms before each job, every change kept: renders, partial renders, fills, copies and the tables' loop fills twice each, three hangs held with debugfs hold_recovery and ended by debugfs reset; event-trigger puts each loop fill (16 to 12500 iterations, integer, and 1024 and 4096 floating-point) after a debugfs reset; register numbers from the GPL kernel's header"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["platform-event-timelines", "platform-event-trigger"]
terms = [
    "CR_EVENT_STATUS2", "CR_EVENT_STATUS2.TRIG_TA", "CR_EVENT_STATUS2.TRIG_3D", "CR_EVENT_STATUS",
    "CR_BIF_INT_STAT", "CR_BIF_FAULT",
]
+++

**Results.**

- *Renders and transfers.* Through the 10 cases of event-timelines' first pass before its loop
  fills (19 jobs: 17 renders in eight render cases of one to three renders at 64x64, 128x128 and
  256x256 and a 1024x768 one that overflows a 0x30-page parameter buffer, a fill and a copy)
  `CR_EVENT_STATUS2` reads 0x400 (bit 10 alone), once 0x1400 for one sample.
  The 2026-10 register timelines (platform-register-timelines) read 0x400 through the triangle up to
  4096x4096 as well.
- *Loop fills.* After a reset, bit 6 sets 0.10 to 0.32 ms after `CR_CLKGATESTATUS` first reads a
  busy pattern (0x000fffa7, or 0x000fffa4 in the 128-iteration case, where bit 6 follows the
  first such sample by about 0.1 ms) in every loop fill of 128 to 12500 iterations, integer and
  floating-point alike, and not in the fill of 16 iterations; in event-timelines it set during the
  first loop fill and read 0x440 through the 13 jobs after it, renders included, until the held
  hang's reset.
- *Held hangs.* In the TA hang bit 7 sets at 107.4 ms, 0.155 ms after
  `CR_DPM_TA_ALLOC_FREE_LIST_STATUS1` takes the loaded PB (0x04220001 at 107.3 ms); in the fault,
  the PB load at 102.9 ms, the fault (`CR_BIF_INT_STAT` 0x90008, `CR_BIF_FAULT` 0x3e000001) at 103.0
  ms and bit 7 at 103.1 ms (0.153 ms after the PB load). `CR_EVENT_STATUS` shows only what the
  TA kick shows (bits 6 and 9 for one sample) and the job events; no bit follows the fault. The
  pixel hang started with bit 6 already set.
- Every reset puts the register back to 0x400.

**What it shows.**

- Bits 6 and 7 are latched: set by a pixel-side and a TA-side condition, cleared only by the
  reset, which our kernel neither enables nor clears [DDK: linux fork, source reading].
- Bit 7 follows a TA that stops at once (a hang or a fault right after its PB load) and bit 6 a
  pixel program that runs long; a TA or pixel task that runs past a short time is the reading
  that fits both, the header naming them TA and 3D triggers [infer].
- A bus fault raises no event bit of its own in either status register (Q003) [HW: one fault].

**Correction 2026-11-10:** The reading above that bit 6 follows "a pixel program that runs long" and
"a task that runs past a short time" is narrowed by two facts already in the records, read before
the round 2 runs and not a new measurement. [data] The renders of this record (up to 4096x4096,
one to three each) run long without a loop and never set bit 6, and E431's single-run job times
run from 797 us at 16 iterations to 1917 us at 136. [infer] Interpolated, the latch's threshold
(53 against 55 iterations) sits at about 1.1 to 1.3 ms of job time (the render times were not
compared here), while this record's loop fills set the bit 0.10 to 0.32 ms after the pixel units
start, so job time is not the measure either. So "time since
the pixel units started" is not supported, and the latch watches something that grows with the
loop length of an instance (E431's note); the delay of about 121 us between a fault word and the
bit in E764 to E766 would then be a different condition from this one, which is not tested.
