+++
id = "C0052"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:95"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L95"
quote = "#define EUR_CR_CLKGATESTATUS                0x0008"
terms = ["CR_CLKGATESTATUS"]
+++

Line 95 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATESTATUS`. It backs the glossary register `CR_CLKGATESTATUS`: per-unit clock-gating
state.
