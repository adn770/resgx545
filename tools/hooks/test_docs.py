# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The workflow after the kit's retirement is written down where a new contributor looks."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def text(name):
    return (ROOT / name).read_text()


def test_hacking_has_a_workflow_section():
    t = text("HACKING.md")
    assert "\n## Workflow\n" in t
    section = t.split("\n## Workflow\n", 1)[1].split("\n## ", 1)[0]
    for word in ("core.hooksPath tools/hooks", "tools/check.sh", "RESGX545_GUARD_DIR",
                 "RESGX545_REQUIRE_GUARD", "Correction YYYY-MM-DD:", "Assisted-by: LLM",
                 "fork-land.sh", "wrapped at 80"):
        assert word in section, word


def test_hacking_setup_uses_the_pinned_requirements():
    t = text("HACKING.md")
    assert "python3.15 -m venv .venv" in t and "requirements-dev.txt" in t


def test_tools_readme_lists_the_new_tools():
    t = text("tools/README.md")
    for word in ("guard.py", "check.sh", "hooks/", "fork/", "bringup/", "health.sh"):
        assert word in t, word


def test_roadmap_has_the_dated_note():
    t = text("doc/roadmap.md")
    assert "Note 2026-11-09:" in t and "2026-11-01" in t


def test_markdown_lines_are_at_most_100_columns():
    for name in ("HACKING.md", "tools/README.md", "doc/roadmap.md"):
        long = [n for n, l in enumerate(text(name).splitlines(), 1) if len(l) > 100]
        assert long == [], (name, long, f"run: tools/wrapmd.py --fix {name}")


def test_hacking_states_where_line_limits_apply():
    t = text("HACKING.md")
    assert "tools/wrapmd.py" in t and "do not hand-wrap code" in t
    assert "tools/wrapmd.py --fix" in (ROOT / "tools/hooks/test_docs.py").read_text()
