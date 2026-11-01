+++
id = "C0133"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:88"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L88"
quote = "IMG_UINT32\t\t\t\tui32uKernelTimerClock;"
terms = ["host_ctl.ukernel_timer_clock"]
+++

Line 88 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32uKernelTimerClock`. It backs the glossary field `host_ctl.ukernel_timer_clock`: EDM timer
period in core clocks.
