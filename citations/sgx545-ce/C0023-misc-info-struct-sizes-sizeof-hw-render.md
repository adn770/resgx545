+++
id = "C0023"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:287"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L287"
quote = "IMG_UINT32\tui32Sizeof_HWRENDERCONTEXT;"
terms = ["misc_info_struct_sizes.sizeof_hw_render_context"]
+++

Line 287 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_HWRENDERCONTEXT`. It backs the glossary field
`misc_info_struct_sizes.sizeof_hw_render_context`: size of HWRENDERCONTEXT the EDM was built for: HW
render context.
