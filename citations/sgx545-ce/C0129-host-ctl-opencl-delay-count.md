+++
id = "C0129"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:111"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L111"
quote = "IMG_UINT32\t\t\t\tui32OpenCLDelayCount;"
terms = ["host_ctl.opencl_delay_count"]
+++

Line 111 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32OpenCLDelayCount`. It backs the glossary field `host_ctl.opencl_delay_count`: OpenCL task
timeout counter.
