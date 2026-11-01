+++
id = "C0381"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:117"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L117"
quote = "IMG_UINT32\t\t\tui32CtrlFlags;"
terms = ["cmd_ta_shared.ctrl_flags"]
+++

Line 117 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32CtrlFlags`. It backs the glossary field `cmd_ta_shared.ctrl_flags`: CMD_TA_CTRL_FLAGS.*; READY
is set last by the kernel.
