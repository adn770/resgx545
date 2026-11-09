# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The rewrite kit is retired: no tracked file points at a script that lived only in it. A
landed file that names the kit says so on the same line (a dated note, its meaning kept)."""
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = "tools/" + "rewrite"


def tracked_lines():
    files = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True,
                           text=True, check=True).stdout.split("\0")
    for f in filter(None, files):
        p = ROOT / f
        if p.is_file() and p.suffix in {".py", ".sh", ".md", ".toml", ".rs", ".c", ".h", ".txt"}:
            for n, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                yield f, n, line


def test_the_kit_is_named_only_as_retired():
    bad = [f"{f}:{n}" for f, n, line in tracked_lines()
           if KIT in line and "retired" not in line and not f.endswith("test_stale_refs.py")]
    assert bad == []


def test_the_series_check_script_it_copies_exists():
    text = (ROOT / "probes/p1134/series_check.sh").read_text()
    m = re.search(r'"\$H/((?:\.\./)+)([\w./-]+check\.sh)"', text) or \
        re.search(r'"\$H/((?:\.\./)+)([\w./-]+fork-check\.sh)"', text)
    assert m, "series_check.sh names no check script"
    assert (ROOT / "probes/p1134" / m.group(1) / m.group(2)).resolve().is_file()
