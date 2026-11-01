+++
id = "C0029"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:284"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L284"
quote = "IMG_UINT32\tui32Sizeof_TRANSFERCMD_SHARED;"
terms = ["misc_info_struct_sizes.sizeof_transfer_cmd_shared"]
+++

Line 284 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_TRANSFERCMD_SHARED`. It backs the glossary field
`misc_info_struct_sizes.sizeof_transfer_cmd_shared`: size of TRANSFERCMD_SHARED the EDM was built
for: kernel-written part of the transfer command.
