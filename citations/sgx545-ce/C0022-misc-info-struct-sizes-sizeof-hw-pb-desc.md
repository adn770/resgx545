+++
id = "C0022"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:286"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L286"
quote = "IMG_UINT32\tui32Sizeof_HWPBDESC;"
terms = ["misc_info_struct_sizes.sizeof_hw_pb_desc"]
+++

Line 286 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_HWPBDESC`. It backs the glossary field `misc_info_struct_sizes.sizeof_hw_pb_desc`: size
of HWPBDESC the EDM was built for: parameter-buffer descriptor.
