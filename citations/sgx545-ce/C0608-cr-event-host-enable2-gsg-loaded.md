+++
id = "C0608"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:250"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L250"
quote = "#define EUR_CR_EVENT_HOST_ENABLE2_GSG_LOADED_MASK 0x00000100U"
terms = ["CR_EVENT_HOST_ENABLE2.GSG_LOADED"]
+++

Line 250 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE2_GSG_LOADED`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE2.GSG_LOADED`: send to host: GSG state loaded.
