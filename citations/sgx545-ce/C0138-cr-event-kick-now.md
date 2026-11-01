+++
id = "C0138"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:755"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L755"
quote = "#define EUR_CR_EVENT_KICK_NOW_MASK          0x00000001U"
terms = ["CR_EVENT_KICK.NOW"]
+++

Line 755 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_KICK_NOW`. It backs the glossary bit field `CR_EVENT_KICK.NOW`: write 1 to trigger.
