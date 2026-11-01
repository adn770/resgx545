+++
id = "C0169"
source = "sgx545-ce"
locator = "src/services4/srvkm/devices/sgx/sgxtransfer.c:195"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/devices/sgx/sgxtransfer.c#L195"
quote = "if ((psKick->ui32Flags & SGXMKIF_TQFLAGS_KEEPPENDING) == 0UL)"
terms = ["transfer_cmd.flags"]
+++

Line 195 of `sgxtransfer.c` in Intel's GPL DDK 1.7 kernel module for Cedarview declares `ui32Flags`.
It backs the glossary field `transfer_cmd.flags`: TQ_FLAGS.* of the transfer.
