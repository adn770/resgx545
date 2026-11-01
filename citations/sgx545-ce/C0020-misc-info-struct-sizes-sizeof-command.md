+++
id = "C0020"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:293"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L293"
quote = "IMG_UINT32\tui32Sizeof_COMMAND;"
terms = ["misc_info_struct_sizes.sizeof_command"]
+++

Line 293 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_COMMAND`. It backs the glossary field `misc_info_struct_sizes.sizeof_command`: size of
COMMAND the EDM was built for: kernel CCB command.
