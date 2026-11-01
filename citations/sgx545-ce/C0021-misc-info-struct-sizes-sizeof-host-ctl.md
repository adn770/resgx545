+++
id = "C0021"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:292"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L292"
quote = "IMG_UINT32\tui32Sizeof_HOST_CTL;"
terms = ["misc_info_struct_sizes.sizeof_host_ctl"]
+++

Line 292 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_HOST_CTL`. It backs the glossary field `misc_info_struct_sizes.sizeof_host_ctl`: size of
HOST_CTL the EDM was built for: host control block.
