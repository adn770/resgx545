+++
id = "C0362"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgxfeaturedefs.h:137"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgxfeaturedefs.h#L137"
quote = "#define SGX_FEATURE_SECONDARY_REQUIRES_USE_KICK"
terms = ["FEATURE.SECONDARY_REQUIRES_USE_KICK"]
+++

Line 137 of `sgxfeaturedefs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`SGX_FEATURE_SECONDARY_REQUIRES_USE_KICK`. It backs the glossary flag
`FEATURE.SECONDARY_REQUIRES_USE_KICK`: a secondary PDS program must start a USE task.
