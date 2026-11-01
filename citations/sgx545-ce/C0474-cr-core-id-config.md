+++
id = "C0474"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:182"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L182"
quote = "#define EUR_CR_CORE_ID_CONFIG_MASK          0x0000FFFFU"
terms = ["CR_CORE_ID.CONFIG"]
+++

Line 182 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CORE_ID_CONFIG`. It backs the glossary bit field `CR_CORE_ID.CONFIG`: core configuration.
