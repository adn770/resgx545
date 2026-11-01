+++
id = "C0124"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:86"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L86"
quote = "IMG_UINT32\t\t\t\tui32HWRecoverySampleRate;"
terms = ["host_ctl.hw_recovery_sample_rate"]
+++

Line 86 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32HWRecoverySampleRate`. It backs the glossary field `host_ctl.hw_recovery_sample_rate`: lockup
check period in timer ticks.
