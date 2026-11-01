+++
id = "C0119"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:92"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L92"
quote = "IMG_UINT32\t\t\t\tui32BPSetClearSignal;"
terms = ["host_ctl.bp_set_clear_signal"]
+++

Line 92 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32BPSetClearSignal`. It backs the glossary field `host_ctl.bp_set_clear_signal`: breakpoint
set/clear signal.
