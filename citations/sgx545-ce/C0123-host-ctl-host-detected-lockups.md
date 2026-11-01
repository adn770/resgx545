+++
id = "C0123"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:85"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L85"
quote = "IMG_UINT32\t\t\t\tui32HostDetectedLockups;"
terms = ["host_ctl.host_detected_lockups"]
+++

Line 85 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32HostDetectedLockups`. It backs the glossary field `host_ctl.host_detected_lockups`: lockups
seen by the host.
