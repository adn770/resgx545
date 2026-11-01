+++
id = "C0018"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:281"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L281"
quote = "IMG_UINT32\tui32Sizeof_CMDTA;"
terms = ["misc_info_struct_sizes.sizeof_cmd_ta"]
+++

Line 281 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_CMDTA`. It backs the glossary field `misc_info_struct_sizes.sizeof_cmd_ta`: size of
CMDTA the EDM was built for: TA command (client CCB entry for TA/3D work).
