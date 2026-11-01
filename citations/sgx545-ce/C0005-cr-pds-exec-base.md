+++
id = "C0005"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:746"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L746"
quote = "#define EUR_CR_PDS_EXEC_BASE                0x0AB8"
terms = ["CR_PDS_EXEC_BASE", "transfer_cmd.pds_exec_base"]
+++

Line 746 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_PDS_EXEC_BASE`. It backs the glossary register `CR_PDS_EXEC_BASE`: base address of PDS
program fetches; and the glossary field `transfer_cmd.pds_exec_base`: PDS execution base.
