+++
id = "E396"
claim = "CR_PDS_REG_0A78 at 0x00, 0x01, 0x08, 0x20, 0x2c and 0x3f does not change the time of a 256x256 triangle render: the median of five runs, each the mean of the last five of six renders, lies between 67274 and 67469 us for every value (0.3 percent), in a shuffled order; one 0x01 run had two slow renders (73110, 74396 us), the only outlier"
unit = "pds"
method = "probes/pds/reg-0a78-timing.toml (script reg-0a78-timing.sh) on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: kreg writes of 0x0a78 before each run and 0x2c after, sgxfive-test tri 256x256 -n 6, thirty runs in a fixed shuffled order"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-reg-0a78-timing"]
terms = []
+++
**Results.** Mean and median of the five runs per value (us): 0x00 67532, 67442; 0x01 67871,
67309; 0x08 67454, 67469; 0x20 67290, 67274; 0x2c 67503, 67452; 0x3f 67428, 67375. E141's slower
0x01 and 0x20 are not seen again.
