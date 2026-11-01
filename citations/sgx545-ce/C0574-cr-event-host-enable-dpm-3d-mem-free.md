+++
id = "C0574"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:539"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L539"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_DPM_3D_MEM_FREE_MASK 0x00000001U"
terms = ["CR_EVENT_HOST_ENABLE.DPM_3D_MEM_FREE"]
+++

Line 539 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_DPM_3D_MEM_FREE`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.DPM_3D_MEM_FREE`: send to host: DPM finished freeing 3D pages.
