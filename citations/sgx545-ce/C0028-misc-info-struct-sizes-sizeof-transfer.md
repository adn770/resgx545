+++
id = "C0028"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:283"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L283"
quote = "IMG_UINT32\tui32Sizeof_TRANSFERCMD;"
terms = ["misc_info_struct_sizes.sizeof_transfer_cmd"]
+++

Line 283 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_TRANSFERCMD`. It backs the glossary field `misc_info_struct_sizes.sizeof_transfer_cmd`:
size of TRANSFERCMD the EDM was built for: transfer-queue command.
