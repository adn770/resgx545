#!/usr/bin/env python3
"""Wrap the prose of a markdown file at 98 columns (headings, blank lines and fenced code untouched;
a list item keeps its marker and a hanging indent)."""
import re, sys, textwrap
lines = open(sys.argv[1]).read().split("\n")
out, para, prefix = [], [], ""
W = 98
def flush():
    global para, prefix
    if para:
        text = " ".join(x.strip() for x in para)
        ind = " " * len(prefix)
        out.extend(textwrap.wrap(text, W, initial_indent=prefix, subsequent_indent=ind,
                                 break_long_words=False, break_on_hyphens=False))
    para, prefix = [], ""
for ln in lines:
    if not ln.strip() or ln.startswith("#"):
        flush(); out.append(ln); continue
    m = re.match(r"^(\s*(?:- |\(\d+\) |\d+\. ))", ln)
    if m:
        flush(); prefix = m.group(1); para = [ln[len(prefix):]]
    elif ln.startswith("  ") and para:
        para.append(ln)
    else:
        if para and not prefix:
            para.append(ln)
        else:
            flush(); para = [ln]
flush()
open(sys.argv[1], "w").write("\n".join(out))
