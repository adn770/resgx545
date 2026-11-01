+++
id = "C0451"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:65"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L65"
quote = "#define EUR_CR_CLKGATECTL2_UCACHEL2_CLKG_MASK 0x00000030U"
terms = ["CR_CLKGATECTL2.UCACHEL2_CLKG"]
+++

Line 65 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATECTL2_UCACHEL2_CLKG`. It backs the glossary bit field `CR_CLKGATECTL2.UCACHEL2_CLKG`:
clock-gating mode of the USSE L2 cache (0 on, 1 off, 2 auto per psb_regs.h).
