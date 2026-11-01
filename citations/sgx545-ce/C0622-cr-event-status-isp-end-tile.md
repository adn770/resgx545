+++
id = "C0622"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:385"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L385"
quote = "#define EUR_CR_EVENT_STATUS_ISP_END_TILE_MASK 0x00800000U"
terms = ["CR_EVENT_STATUS.ISP_END_TILE"]
+++

Line 385 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS_ISP_END_TILE`. It backs the glossary bit field `CR_EVENT_STATUS.ISP_END_TILE`:
status: ISP finished a tile.
