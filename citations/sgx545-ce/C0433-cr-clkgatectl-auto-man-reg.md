+++
id = "C0433"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:55"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L55"
quote = "#define EUR_CR_CLKGATECTL_AUTO_MAN_REG_MASK 0x01000000U"
terms = ["CR_CLKGATECTL.AUTO_MAN_REG"]
+++

Line 55 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATECTL_AUTO_MAN_REG`. It backs the glossary bit field `CR_CLKGATECTL.AUTO_MAN_REG`:
register-block clock gating: automatic or manual.
