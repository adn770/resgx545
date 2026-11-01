+++
id = "C0130"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:104"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L104"
quote = "IMG_UINT32\t\t\t\tui32PerfGroup;"
terms = ["host_ctl.perf_group"]
+++

Line 104 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32PerfGroup`. It backs the glossary field `host_ctl.perf_group`: HW perf counter group.
