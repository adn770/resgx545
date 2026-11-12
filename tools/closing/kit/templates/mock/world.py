# SPDX-License-Identifier: MIT
"""mock/world.py: @NAME@'s argv-driven fake laptop for kit/session.py mock. answer() sees the
tool's name, the argv and the world's tokens, never a case name; it returns None (the health
pair, or a refusal) or dict(rc, out, err, files={path: bytes}, kmsg=[lines], latch=(int, word)).
EXPECT: {world: (the driver's status, {stage: the runner's status})}; the mock runs each world on
a fresh fake laptop and fails on any other status. This template accepts every option: make the
fake as strict as the real tool, and add a world for each stop the session relies on."""
EXPECT = {"model": (0, {"s0": 0}), "nodiff": (25, {"s0": 25})}


def opt(a, name, cast=str, default=None):
    return cast(a[a.index(name) + 1]) if name in a else default


def answer(tool, argv, world):
    if not argv or argv in (["fill"], ["tri"]):
        return None
    files = {}
    if "--dump" in argv:
        files[opt(argv, "--dump")] = bytes(16)
    w, h = opt(argv, "--width", int, 64), opt(argv, "--height", int, 32)
    if argv[0] == "tri":
        out = "job: ok\n" + ("" if "nodiff" in world else "diff: 0 of %d pixels\n" % (w * h))
        return dict(out=out, files=files)
    if argv[0] == "fill":
        return dict(out="job: ok\ndiff: 0 of %d pixels\n" % (w * h), files=files)
    return None
