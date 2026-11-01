+++
id = "C0464"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:117"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L117"
quote = "#define EUR_CR_CLKGATESTATUS_PDS0_CLKS_MASK 0x00000080U"
terms = ["CR_CLKGATESTATUS.PDS0_CLKS"]
+++

Line 117 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATESTATUS_PDS0_CLKS`. It backs the glossary bit field `CR_CLKGATESTATUS.PDS0_CLKS`:
clock state of the PDS 0.
