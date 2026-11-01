+++
id = "C0122"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:97"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L97"
quote = "IMG_UINT32\t\t\t\tui32HostClock;"
terms = ["host_ctl.host_clock"]
+++

Line 97 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32HostClock`. It backs the glossary field `host_ctl.host_clock`: host clock at EDM boot.
