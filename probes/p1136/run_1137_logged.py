#!/usr/bin/env python3
"""run_1137_logged.py NAME STAGE: run_1137.py unchanged (its frozen judging and stop rules), with every job's record
and whole results page also kept (out/NAME/jobs/<tag>.json: the job, the record and the 1024-dword page as read after
the job), because run_1137.py keeps only the verdicts.  Nothing is judged here and no register is written."""
import json, pathlib, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run_1137 as R  # noqa: E402

_job = R.Ctx.job


def job(self, j, tag, timeout_ms=100, **kw):
    rec, page = _job(self, j, tag, timeout_ms, **kw)
    if not self.dry:
        d = self.out / "jobs"
        d.mkdir(exist_ok=True)
        (d / (tag + ".json")).write_text(json.dumps({"tag": tag, "job": {k: v for k, v in j.items()},
                                                     "record": rec, "page": page}, default=str))
    return rec, page


R.Ctx.job = job
if __name__ == "__main__":
    sys.exit(R.main())
