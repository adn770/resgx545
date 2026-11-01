+++
id = "C0027"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:291"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L291"
quote = "IMG_UINT32\tui32Sizeof_HWTRANSFERCONTEXT;"
terms = ["misc_info_struct_sizes.sizeof_hw_transfer_context"]
+++

Line 291 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_HWTRANSFERCONTEXT`. It backs the glossary field
`misc_info_struct_sizes.sizeof_hw_transfer_context`: size of HWTRANSFERCONTEXT the EDM was built
for: HW transfer context.
