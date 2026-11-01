+++
id = "C0001"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1076"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1076"
quote = "#define EUR_CR_BIF_3D_REQ_BASE              0x0CAC"
terms = ["CR_BIF_3D_REQ_BASE", "transfer_cmd.bif_3d_req_base"]
+++

Line 1076 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_3D_REQ_BASE`. It backs the glossary register `CR_BIF_3D_REQ_BASE`: 3D requestor base
address; the glossary field `hw_render_details.bif_3d_req_base`: 3D requestor base; and the glossary
field `transfer_cmd.bif_3d_req_base`: 3D requestor base.
