+++
id = "C0450"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:86"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L86"
quote = "#define EUR_CR_CLKGATECTL2_TEX1_CLKG_MASK   0x000C0000U"
terms = ["CR_CLKGATECTL2.TEX1_CLKG"]
+++

Line 86 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATECTL2_TEX1_CLKG`. It backs the glossary bit field `CR_CLKGATECTL2.TEX1_CLKG`:
clock-gating mode of the texture unit 1 (0 on, 1 off, 2 auto per psb_regs.h).
