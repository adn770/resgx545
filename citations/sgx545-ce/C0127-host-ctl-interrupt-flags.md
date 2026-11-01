+++
id = "C0127"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:90"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L90"
quote = "IMG_UINT32\t\t\t\tui32InterruptFlags;"
terms = ["host_ctl.interrupt_flags"]
+++

Line 90 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32InterruptFlags`. It backs the glossary field `host_ctl.interrupt_flags`: EDM->host requests
(INTERRUPT_FLAGS.*).
