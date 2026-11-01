+++
id = "Q005"
question = "should the kernel ask the firmware for its identity on every boot, so DEV_QUERY reports it without the debug option?"
unit = "edm"
phase = 6
evidence = ["E017", "E022"]
terms = ["misc_info", "misc_info_features"]
+++

The firmware answers GETMISCINFO with its core and DDK identity (E017). The kernel sends
GETMISCINFO only when the debugfs `miscinfo` file is read (sgxfive_debug.c), and that file
exists only with `DRM_GMA500_SGXFIVE_DEBUG`. The answer is recorded there, even when it
does not match the registers and the firmware file, and nothing clears it on a reload or
reset. So DEV_QUERY (sgxfive_drv.c) reports the firmware's own core id, revision and DDK
version only after that file has been read in a debug build. Until then
`DRM_SGXFIVE_GPU_INFO_SW_VALID` is clear and `ddk_version` is 0.

The values the kernel reads from the firmware file (`ddk_build`, `build_options`) are
reported in every build, but only once the firmware is loaded, which happens at the first
job. Before that, the firmware query gives zeros. The query on a fresh boot of the laptop
shows this, in a debug build with the file not yet read (E022):
`ddk 0.0.0 build 0 options 0x0`, `fw_state 0`.

Open: whether to send GETMISCINFO after every boot. On the laptop the answer came within
173 to 175 µs of a boot, and within 2 to 2127 µs on repeated reads, all upper bounds (E017).
Sending it would let a build without the debug option report the identity and catch a
firmware built for another core. Meanwhile userspace takes the firmware file's values and
treats `SW_VALID` as optional.
