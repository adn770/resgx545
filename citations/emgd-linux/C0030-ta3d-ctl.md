+++
id = "C0030"
source = "emgd-linux"
locator = "drm/pvr/services4/srvkm/devices/sgx/pb.c:228"
link = "https://github.com/EMGD-Community/intel-binaries-linux/blob/e6884ec2eaaf1afe88d5ff9dd44d70403525be5b/drm/pvr/services4/srvkm/devices/sgx/pb.c#L228"
quote = "/* signal the microkernel to clear its sTAHWPBDesc and s3DHWPBDesc values in sTA3DCtl */"
terms = ["ta3d_ctl"]
+++

Line 228 of `pb.c` in Intel's EMGD kernel sources declares `s3DHWPBDesc`, `sTA3DCtl` and
`sTAHWPBDesc`. It backs the glossary structure `ta3d_ctl`: TA/3D control block of the EDM; the
glossary field `ta3d_ctl.hw_pb_desc_3d`: PB descriptor loaded in the 3D; and the glossary field
`ta3d_ctl.hw_pb_desc_ta`: PB descriptor loaded in the TA.
