+++
id = "C0107"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:400"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L400"
quote = "#define EUR_CR_EVENT_STATUS_PIXELBE_END_RENDER_MASK 0x00040000U"
terms = ["Pixel Back End (PBE)"]
+++

Line 400 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS_PIXELBE_END_RENDER` and `PIXELBE`. It backs the glossary bit field
`CR_EVENT_STATUS.PIXELBE_END_RENDER`: status: pixel back end finished the render; and the glossary
unit `Pixel Back End (PBE)`: PBE as spelled in register names; signals end of render.
