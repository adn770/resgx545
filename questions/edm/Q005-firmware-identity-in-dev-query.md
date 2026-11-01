+++
id = "Q005"
question = "should the kernel ask the firmware for its identity on every boot, so DEV_QUERY reports it without the debug option?"
unit = "edm"
phase = 6
evidence = ["E017", "E022", "E321"]
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

What a query at boot costs is measured (E321, one run): after each of three resets (about
0.27 s each) the EDM answers within 169 to 175 µs, first query and second alike, and a firmware
that has stopped serving commands leaves the query to the kernel's wait, 500 ms (sgxfive_debug.c;
about 0.65 s from the shell). Sending it
would let a build without the debug option report the identity and catch a firmware built for
another core, for well under a millisecond per boot.

Open: the decision. Meanwhile userspace takes the firmware file's values and treats `SW_VALID`
as optional.
