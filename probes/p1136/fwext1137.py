#!/usr/bin/env python3
"""Phase 11.37 (prepared, NOT RUN): two commands that the landed fwtask_run.py lacks, to be uploaded to
~/fwtask/ beside it and run as `sudo -n python3 ~/fwtask/fwext1137.py CMD 'JSON'`:

  slowevent  start cmd 1 (the slow loop or the str/ldr task) and, after delay_ms, cause one event
             (kick: the miscinfo debugfs read, the one of E538; fill / tri: a client job of the
             sgxfive-test tool; none), then wait for done and report the page words, the HostCtl
             tick counter delta and the host-side times.  It writes no register.
  page       the whole results page (the landed `page` command does the same).

Everything else (arming, reset, the gate, health) is the landed runner's.  The commands only read
what the landed runner reads and write only own_res dwords, as one_cmd does."""
import json
import sys
import time

sys.path.insert(0, "/home/jtorra/fwtask")
import fwtask_run as FR   # noqa: E402

TOOL = "/home/jtorra/sgxfive-test"


def slowevent(a):
    n0 = FR.dmesg_len()
    res = FR.Res()
    for k, v in a["params"].items():
        res.w(int(k), v)
    res.w(FR.OVERLAP, 0)
    res.w(FR.STATE, 0)
    res.w(FR.RUNID, a.get("runid", 1))
    tk0 = FR.regs()[1].get(12)
    t0 = time.monotonic()
    res.w(FR.CMD, a.get("cmd", 1))
    time.sleep(a.get("delay_ms", 0) / 1000)
    trig_t = time.monotonic()
    trig = a.get("trigger", "none")
    out = {}
    if trig == "kick":
        out["trigger"] = FR.miscinfo()
    elif trig in ("fill", "tri"):
        out["trigger"] = FR.sh(f"{TOOL} {trig} 2>&1 | grep -E '^diff|FAIL' | head -2", check=False).strip()
    done = False
    while (time.monotonic() - t0) * 1000 < a.get("timeout_ms", 300):
        if res.r(FR.STATE)[0] == 2:
            done = True
            break
    t1 = time.monotonic()
    tk1 = FR.regs()[1].get(12)
    out.update({"done": done, "ms": (t1 - t0) * 1000, "trigger_at_ms": (trig_t - t0) * 1000,
                "ticks": (tk1 - tk0) & 0xffffffff, "ticks_expected": (t1 - t0) * 997,
                "page": res.page(), "log_bad": [ln for ln in FR.dmesg_new(n0) if FR.BAD_LOG.search(ln)],
                "alive": FR.alive(), "health": FR.health()})
    res.close()
    FR.emit(out)
    return 0 if done else 1


def page(_):
    r = FR.Res()
    p = r.page()
    r.close()
    FR.emit({"page": p})


def main():
    a = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    sys.exit({"slowevent": slowevent, "page": page}[sys.argv[1]](a) or 0)


if __name__ == "__main__":
    main()
