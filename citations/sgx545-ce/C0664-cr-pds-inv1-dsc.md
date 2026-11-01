+++
id = "C0664"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:770"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L770"
quote = "#define EUR_CR_PDS_INV1_DSC_MASK            0x00000001U"
terms = ["CR_PDS_INV1.DSC"]
+++

Line 770 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_PDS_INV1_DSC`. It backs the glossary bit field `CR_PDS_INV1.DSC`: invalidate this PDS data
cache.
