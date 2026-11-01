+++
id = "C0115"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:219"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L219"
quote = "#define EUR_CR_SOFT_RESET_USE_RESET_MASK    0x00000008U"
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

Line 219 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_SOFT_RESET_USE_RESET` and `USE`. It backs the glossary bit field `CR_SOFT_RESET.USE_RESET`:
hold the USSE in reset; and the glossary unit `Universal Scalable Shader Engine (USSE)`: USSE block
(its soft reset); register names use the short abbreviation.
