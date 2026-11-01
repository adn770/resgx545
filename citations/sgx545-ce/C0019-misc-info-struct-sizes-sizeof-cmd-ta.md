+++
id = "C0019"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:282"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L282"
quote = "IMG_UINT32\tui32Sizeof_CMDTA_SHARED;"
terms = ["misc_info_struct_sizes.sizeof_cmd_ta_shared"]
+++

Line 282 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_CMDTA_SHARED`. It backs the glossary field
`misc_info_struct_sizes.sizeof_cmd_ta_shared`: size of CMDTA_SHARED the EDM was built for:
kernel-written part of the TA command.
