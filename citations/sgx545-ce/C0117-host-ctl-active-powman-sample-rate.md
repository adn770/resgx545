+++
id = "C0117"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:89"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L89"
quote = "IMG_UINT32\t\t\t\tui32ActivePowManSampleRate;"
terms = ["host_ctl.active_powman_sample_rate"]
+++

Line 89 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32ActivePowManSampleRate`. It backs the glossary field `host_ctl.active_powman_sample_rate`:
active power latency in ticks.
