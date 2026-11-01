+++
id = "C0690"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:381"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L381"
quote = "IMG_UINT32\t\tui32SharedCmdCCBOffset;"
terms = ["transfer_cmd.shared"]
+++

Line 381 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32SharedCmdCCBOffset`. It backs the glossary field `transfer_cmd.shared`: embedded
transfer_cmd_shared block; the kick passes its client-CCB offset in
transfer_kick.shared_cmd_ccb_offset.
