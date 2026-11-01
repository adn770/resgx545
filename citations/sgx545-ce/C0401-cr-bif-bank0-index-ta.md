+++
id = "C0401"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1036"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1036"
quote = "#define EUR_CR_BIF_BANK0_INDEX_TA_MASK      0x000000F0U"
terms = ["CR_BIF_BANK0.INDEX_TA"]
+++

Line 1036 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_BANK0_INDEX_TA`. It backs the glossary bit field `CR_BIF_BANK0.INDEX_TA`: directory-list
index for TA requests.
