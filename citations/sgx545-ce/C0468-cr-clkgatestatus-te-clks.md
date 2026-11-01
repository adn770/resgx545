+++
id = "C0468"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:105"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L105"
quote = "#define EUR_CR_CLKGATESTATUS_TE_CLKS_MASK   0x00000008U"
terms = ["CR_CLKGATESTATUS.TE_CLKS"]
+++

Line 105 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATESTATUS_TE_CLKS`. It backs the glossary bit field `CR_CLKGATESTATUS.TE_CLKS`: clock
state of the TE.
