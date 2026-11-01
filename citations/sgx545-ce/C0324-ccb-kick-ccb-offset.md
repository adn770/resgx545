+++
id = "C0324"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:285"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L285"
quote = "IMG_UINT32\tui32CCBOffset;"
terms = ["ccb_kick.ccb_offset", "cmd_ta.shared"]
+++

Line 285 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares `ui32CCBOffset`.
It backs the glossary field `ccb_kick.ccb_offset`: client-CCB offset of CMDTA_SHARED; and the
glossary field `cmd_ta.shared`: embedded cmd_ta_shared block; the kick passes its client-CCB offset
in ccb_kick.ccb_offset.
