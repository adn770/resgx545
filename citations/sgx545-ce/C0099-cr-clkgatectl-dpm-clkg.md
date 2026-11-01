+++
id = "C0099"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:46"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L46"
quote = "#define EUR_CR_CLKGATECTL_DPM_CLKG_MASK     0x00000C00U"
terms = ["CR_CLKGATECTL.DPM_CLKG", "Dynamic Parameter Management (DPM)"]
+++

Line 46 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines `DPM` and
`EUR_CR_CLKGATECTL_DPM_CLKG`. It backs the glossary bit field `CR_CLKGATECTL.DPM_CLKG`: clock-gating
mode of the DPM (0 on, 1 off, 2 auto per psb_regs.h); and the glossary unit `Dynamic Parameter
Management (DPM)`: DPM block (its clock gate).
