+++
id = "Q005"
question = "should the kernel ask the firmware for its identity on every boot, so DEV_QUERY reports it without the debug option?"
unit = "edm"
kind = "kernel"
phase = 6
evidence = ["E017", "E022", "E321", "E402"]
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
context creation (`sgxfive_ioctl_create_ctx` loads the firmware; no other ioctl does). Before
that, the firmware query gives zeros (E022).

What a query at boot costs is measured (E321, one run): after each of three resets (about 0.27 s
each) the EDM answers within 169 to 175 µs, first query and second alike, and a firmware that has
stopped serving commands leaves the query to the kernel's wait, 500 ms.

Decided (2026-11-07, the user): the kernel asks GETMISCINFO in every build, at the end of each boot
of the firmware, so after the load and after each reset. An answer sets `SW_VALID`; a reply for
another core or revision than the registers name, or a firmware built for another core than 545,
is kept and warned about; no answer leaves `SW_VALID` clear and logs once until the firmware
answers again, and the boot does not fail for it. Done in the linux fork's commit 32, with KUnit
in builds with and without the debug option (the reply's core check, no answer, `GPU_INFO`).
A review of the first version added, in the same commits: SW_VALID is cleared when the firmware
stops (sgxfive_halt), so GPU_INFO shows no identity while a reset restarts the firmware and a
failed boot leaves none, and FW_INFO's `ddk_version` is 0 while the flag is clear; the stored
values are written with WRITE_ONCE before the flag is released and read with READ_ONCE after it
is acquired. Checked on the laptop in both builds (E402): nothing before the load, then core 545
and DDK 1.7.17 after the load and after a reset, the answer in 0.18 to 3.9 ms, and the flag clear
for the length of a reset (GPU_INFO read in a loop during a debugfs reset).

What is left: a mismatch and a missing answer have not been seen on hardware, since the EDM
answered every request; only KUnit covers them.
