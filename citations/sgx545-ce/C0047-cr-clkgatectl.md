+++
id = "C0047"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:30"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L30"
quote = "#define EUR_CR_CLKGATECTL                   0x0000"
terms = ["CR_CLKGATECTL"]
+++

Line 30 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATECTL`. It backs the glossary register `CR_CLKGATECTL`: per-unit clock-gating mode
control.
