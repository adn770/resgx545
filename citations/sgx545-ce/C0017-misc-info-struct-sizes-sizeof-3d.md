+++
id = "C0017"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:285"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L285"
quote = "IMG_UINT32\tui32Sizeof_3DREGISTERS;"
terms = ["misc_info_struct_sizes.sizeof_3d_registers"]
+++

Line 285 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Sizeof_3DREGISTERS`. It backs the glossary field `misc_info_struct_sizes.sizeof_3d_registers`:
size of 3DREGISTERS the EDM was built for: 3D register block at the start of the render details.
