+++
id = "C0016"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:112"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L112"
quote = "} SGXMKIF_HOST_CTL;"
terms = ["host_ctl"]
+++

Line 112 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`SGXMKIF_HOST_CTL`. It backs the glossary structure `host_ctl`: host control block
(init/power/cleanup status, timers).
