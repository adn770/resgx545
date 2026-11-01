"""Import the landed simrun (read-only) with a pysgx built into tables/target (no cargo in the repo)."""
import os, sys, types, pathlib
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
R = pathlib.Path.home() / "src/resgx545"
os.environ.setdefault("FWTASK_USSE_ASM", str(R / "tools/usse-asm/usse-asm"))
sys.path.insert(0, str(HERE / "pysgx"))
import pysgx as _p
sys.modules["load"] = types.SimpleNamespace(pysgx=lambda: _p)
sys.path.insert(0, str(R / "tools/fwtask"))
import fwtask as F
import layout as L
import simrun as S
