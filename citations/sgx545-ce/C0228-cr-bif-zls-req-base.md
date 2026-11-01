+++
id = "C0228"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1080"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1080"
quote = "#define EUR_CR_BIF_ZLS_REQ_BASE             0x0CB0"
terms = ["Z Load Store (ZLS)", "hw_render_details.bif_zls_req_base"]
+++

Line 1080 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_ZLS_REQ_BASE` and `ZLS`. It backs the glossary register `CR_BIF_ZLS_REQ_BASE`: ZLS
requestor base address; the glossary unit `Z Load Store (ZLS)`: ZLS memory requester (its BIF
requestor base); and the glossary field `hw_render_details.bif_zls_req_base`: ZLS requestor base.
