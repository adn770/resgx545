+++
id = "C0025"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:289"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L289"
quote = "IMG_UINT32\tui32Sizeof_HWRTDATA;"
terms = ["misc_info_struct_sizes.sizeof_hw_rt_data"]
+++

Line 289 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_HWRTDATA`. It backs the glossary field `misc_info_struct_sizes.sizeof_hw_rt_data`: size
of HWRTDATA the EDM was built for: render-target data, one per TA/3D overlap slot.
