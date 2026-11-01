# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""One place for the later-phase dependencies the tests skip on.

The firmware tools come first; the assemblers, the disassemblers and the Rust workspace
arrive in later phases. A test that needs one asks here, so every test agrees on what
"available" means.
"""
from __future__ import annotations

import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def needs_asm() -> bool:
    """The assemblers (tools/usse-asm) and every source of ours.PROGS."""
    import ours
    return (ROOT / "tools" / "usse-asm" / "Makefile").is_file() and \
        all((ours.PROGS_DIR / name).is_file() for name, _ in ours.PROGS.values())


def needs_dis() -> bool:
    """The disassemblers (tools/usse-dis)."""
    return (ROOT / "tools" / "usse-dis" / "Makefile").is_file()


def needs_cargo() -> bool:
    """cargo on PATH and the Rust workspace."""
    return shutil.which("cargo") is not None and (ROOT / "Cargo.toml").is_file()
