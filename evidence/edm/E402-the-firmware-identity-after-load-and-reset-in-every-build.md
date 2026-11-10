+++
id = "E402"
claim = "With the kernel asking GETMISCINFO at the end of every boot of the firmware and clearing the answer when the firmware stops, DEV_QUERY reports the firmware's core 545, revision 0x1000d and DDK 1.7.17 build 862890 after the load and after a reset, in a build with the debug option and in one without it, and nothing before the load; during a debugfs reset GPU_INFO has SW_VALID clear from 1 ms after the reset is written until it returns (3619 of 3717 reads in the window); the EDM answers in 0.18 to 3.9 ms at the load and in 0.18 to 1.8 ms after a reset; one run of each"
unit = "edm"
method = "a shell script (probes/edm/identity-at-boot.toml) on the laptop over the direct cable, linux fork f1fad0ed9d0e (commit 35 of 11.15; the module built on the laptop, KUnit run at its load: 132 of 132 tests with the debug option, 99 of 99 without), booted once into the test kernel for each build: sgxfive-test query before any context, a fill (its context loads and boots the firmware), query again, a reset (debugfs reset with the debug option, a render faulting on its unmapped stream page and recovered by the fault watchdog without it), query again, the driver's identity lines, a fill and a triangle. With the debug option a python loop then read GPU_INFO on the render node about 28000 times a second while debugfs reset ran, and printed the time of each change of SW_VALID. The build without the debug option is the same sources compiled with the option undefined"
tiers = ["HW", "DDK"]
date = "2026-11-07"
data = []
terms = ["misc_info", "misc_info_features"]
+++

**Results.**

- *Before the load* (both builds): the query reads `ddk 0.0.0 build 0 options 0x0`, `fw_state 0`
  and no `core_sw` line (GPU_INFO_SW_VALID clear); the log has no identity line.
- *After the load* (first context, a fill that renders exactly): `core_sw 545 rev 0x1000d`,
  `ddk 1.7.17 build 862890 options 0x60218`, `fw_state 1`. The log has one line, "SGX firmware:
  core 545 rev 0x1000d, DDK 1.7.17 build 862890", with the answer after 183 µs (debug option on,
  a fresh boot) and 1965 µs (off). An earlier boot with the same module answered the first
  command after 3927 µs, so the first answer varies.
- *After a reset*: the same values; a second identity line, after 1816 µs (debugfs reset, 295 ms
  from the shell, debug option on) and 777 µs (fault recovery, debug option off; the faulting
  render fails with an I/O error and its context is lost). A fill and a 64x64 triangle then run
  exactly in both builds.
- *During a reset* (debug option on): GPU_INFO read in a loop shows SW_VALID set with core_id_sw
  545, clear 1.0 ms after the reset was written (502 to 503.2 ms) with core_id_sw 0, and set
  again at 645.3 ms, 3.5 ms before the write returned (649 ms); 3619 of the 3717 reads made
  while the write ran saw it clear. Before the clear, the flag had stayed set for the whole of
  a reset (the earlier module, by the code). FW_INFO takes the device lock the reset holds, so it
  waits for the reset to end and cannot be read in the window.
- The core and revision the firmware reports agree with the registers, so no mismatch warning is
  logged. The mismatch and the no-answer paths are checked by KUnit only: the EDM answered
  every request on the laptop.

**What it shows.**

- The kernel's request at the end of each boot gives DEV_QUERY the firmware's own identity in a
  build without the debug files, after the load and after each reset, and takes it away while a
  reset restarts the firmware, as the retired question on the firmware identity asked [HW: one run of each build] [DDK: linux fork commits
  32 to 35].
- The answer takes 0.18 to 3.9 ms; the 3 to 4 ms ones are the first command after a boot that
  carries the cache invalidation the boot's init info asks for, as the 3.4 to 3.7 ms of the
  earlier run did [infer]. The 169 to 175 µs of the debug file after a reset (E321) is the same
  order as the 160 to 183 µs seen here.
