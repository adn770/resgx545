+++
id = "C0112"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:216"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L216"
quote = "#define EUR_CR_SOFT_RESET_TA_RESET_MASK     0x00000004U"
terms = ["Tile Accelerator (TA)"]
+++

Line 216 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_SOFT_RESET_TA_RESET` and `TA`. It backs the glossary bit field `CR_SOFT_RESET.TA_RESET`:
hold the TA in reset; and the glossary unit `Tile Accelerator (TA)`: TA block (its soft reset).
