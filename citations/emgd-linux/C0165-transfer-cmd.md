+++
id = "C0165"
source = "emgd-linux"
locator = "drm/pvr/services4/include/sgx_mkif_km.h:211"
link = "https://github.com/EMGD-Community/intel-binaries-linux/blob/e6884ec2eaaf1afe88d5ff9dd44d70403525be5b/drm/pvr/services4/include/sgx_mkif_km.h#L211"
quote = "* (SGXMKIF_TRANSFERCMD), and is accessed from the kernel part of the driver"
terms = ["transfer_cmd"]
+++

Line 211 of `sgx_mkif_km.h` in Intel's EMGD kernel sources declares `SGXMKIF_TRANSFERCMD`. It backs
the glossary structure `transfer_cmd`: transfer command structure proper; holds TRANSFERCMD_SHARED.
