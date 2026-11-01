+++
id = "C0742"
source = "sgx545-ce"
locator = "src/services4/srvkm/devices/sgx/sgxkick.c:43"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/devices/sgx/sgxkick.c#L43"
quote = "PVRSRV_ERROR SGXDoKickKM(IMG_HANDLE hDevHandle, SGX_CCB_KICK_KM *psCCBKick)"
terms = ["SGXDoKickKM"]
+++

Line 43 of `sgxkick.c` in Intel's GPL DDK 1.7 kernel module for Cedarview names `SGXDoKickKM`. It
backs the glossary function `SGXDoKickKM`: kernel side of SGXKickTA.
