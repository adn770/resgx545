+++
id = "E154"
claim = "The request word TA3DCtl dword 31 has nine request bits in use, each posted by one pa1 bit of the event task or by a named routine and each handled by one of PDS #14's three tasks (0x1, 0x2, 0x8 and 0x40000 by the task at 0xe74, 0x80 and 0x20000 by 0x5d4, 0x10, 0x20, 0x40 and 0x80000 by 0xae8), and the EDM keeps the TA's state in sa8 and the 3D's in sa9 so that one TA job and one 3D job are in flight at a time"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the post routine at 0x1756, all nine of its callers, the event task at 0x6 and the three request tasks selected by PDS #14 (E146); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["ta3d_ctl", "CR_EVENT_STATUS", "CR_EVENT_HOST_CLEAR"]
+++

**What was read.** Instruction numbers are indices in hex. The routine at `0x1756` ORs the request
mask it is given into TA3DCtl dword 31 and starts PDS #14 (E146) when the OR changed the word.
Each of PDS #14's three tasks begins by removing the bits it was handed (`pa0`) from dword 31.
`pa1` is the event word PDS #13 hands to its general task (E146, E155); the tasks write
`CR_EVENT_HOST_CLEAR` (`0x0134`) with the value that acknowledges the event.

**Results.** The table gives each request bit, who posts it, and the task and routine that
handle it with the acknowledgement written first.

| request | posted by | task, then routine (acknowledgement) |
|---|---|---|
| `0x1` | event task, `pa1` bit 22 | `0xe74`, `0xeb4` (`0x1`) |
| `0x2` | event task, `pa1` bit 4 | `0xe74`, `0xebb` (`0x40000`) |
| `0x8` | event task, `pa1` bit 7 | `0xe74`, `0xecd` (`0x8000`) |
| `0x10`, `0x20` | event task, `pa1` bit 20 or 21 (together) | `0xae8`, `0xb50` (`0x6`) |
| `0x40` | `pa1` bit 10; also `0x617`, `0x1029`, `0x14a9` | `0xae8`, `0xc23` (`0x1000`) |
| `0x80` | event task, `pa1` bit 9; also `0xdf2` | `0x5d4`, `0x606` (`0x2000`) |
| `0x20000` | the routine at `0x1592`: a TA queue is not empty | `0x5d4`, `0x6f5` |
| `0x40000` | the routine at `0x159e`: the transfer or 3D queue is not empty | `0xe74`, `0x1035` |
| `0x80000` | `0xfe1`, when a partial render completes | `0xae8`, `0xdbf` |

- *Selection.* PDS #14 starts `0xe74` for any bit of `0x4000f`, else `0x5d4` for any bit of
  `0x120080`, else `0xae8` (E146). The bits `0x4` and `0x100000` are in the first two masks, but
  neither task has a branch for them: a request with only those bits runs the task and ends it.
- *Event task.* Its test of `pa1` bits `0x380400` includes bit 19, which posts nothing.
- *Other posters of `0x40`.* At `0x617` (TA finished, with bit 9 of `sa8` set), and at `0x1029`
  and `0x14a9` (the end of a 3D or transfer job, when bit 17 of `sa8` is set; the terminate
  handler at `0xc23` sets that bit when it finds the 3D running). `0x80` is posted a second time
  at `0xdf2`, in the resume routine at `0xdbf`.
- *No waiting.* A task ends through the shared routine at `0x1974` (a cache flush and the end
  of the PDS task); work continues from the next event or request. The waits inside a handler
  are polls of a status register.
- *One job each.* The TA scheduler (`0x6f5`) starts a TA kick only when bit 0 of `sa8` is clear
  and the 3D scheduler (`0x1035`) only when bit 0 of `sa9` is clear, except that a context in a
  lower queue index than the one running may be taken while a render runs. The TA state word
  `sa8` has bit 0 (TA running, set at the end of the TA kick, cleared at TA finished), bit 11
  (out-of-memory pending, set at `0xb50`), and bits 5, 9, 10, 18 and 22, which the
  out-of-memory and partial-render paths set and clear. The 3D state word `sa9` has bit 0 (3D
  running), bit 1 (partial render), bit 2 (a transfer is the job), bit 4 (a render is in flight),
  bit 5 (the deallocation is pending) and bit 6 (an out-of-memory is waiting for the 3D).
- *Queues.* Contexts wait on lists held in secondary attributes, head then tail: transfer
  `sa13` and `sa14`, TA `sa15` and `sa16`, 3D `sa17` and `sa18`, one list per queue index; the
  routines at `0x1592` and `0x159e` look at the heads of index 0 only (the TA head, and the
  transfer and the 3D heads).

**Not shown.** Which bit of `CR_EVENT_STATUS` each `pa1` bit is (E155 reads it); what the three
`sa8` bits other than 0 and 11 mean in each path; whether a second request posted while a task
runs is lost or run (the post routine ORs it in and starts PDS #14 again only when the word
changed); nothing here runs the firmware.
