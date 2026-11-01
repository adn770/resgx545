+++
id = "C0438"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:52"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L52"
quote = "#define EUR_CR_CLKGATECTL_PDS0_CLKG_MASK    0x0000C000U"
terms = ["CR_CLKGATECTL.PDS0_CLKG"]
+++

Line 52 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CLKGATECTL_PDS0_CLKG`. It backs the glossary bit field `CR_CLKGATECTL.PDS0_CLKG`:
clock-gating mode of the PDS 0 (0 on, 1 off, 2 auto per psb_regs.h).
