+++
id = "C0126"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:91"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L91"
quote = "IMG_UINT32\t\t\t\tui32InterruptClearFlags;"
terms = ["host_ctl.interrupt_clear_flags"]
+++

Line 91 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32InterruptClearFlags`. It backs the glossary field `host_ctl.interrupt_clear_flags`: host
acknowledges of host_ctl.interrupt_flags.
