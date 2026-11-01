# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The results page of own_res (dword indices), the host and the task share it (plan 1.4)."""
MAGIC, CMD, STATE, RUNID, OVERLAP, RUNID_ECHO = 0, 1, 2, 3, 4, 5
PARAMS = 8                  # 8..15: host parameters (loop count, B, C, ...)
PARAM_B, PARAM_C, PARAM_N = 8, 9, 10
LOG = 16                    # 16..31: the event log, 4 dwords per slot
RESULTS = 0x40              # 4 dwords per command: results of command n at RESULTS + 4 n
INITFILL = 0xdeadc0de
BUSY, DONE = 1, 2
PAGE_DWORDS = 1024

# the registers of 9b
R1, R2 = 0x0814, 0x0a78
A = {R1: 0x15a5a, R2: 0x15}
B = {R1: 0x0a5a5, R2: 0x2a}
C = {R1: 0x0f0f0, R2: 0x0c}
MASK = {R1: 0x1ffff, R2: 0x3f}


def slot(n: int) -> int:
    return RESULTS + 4 * n


# the 9b commands: number -> (name, kind, d)
X9B = {
    1: ("X0", "x0", 0), 2: ("X1", "x1", 0),
    3: ("X2_d0", "x2", 0), 4: ("X2_d1", "x2", 1), 5: ("X2_d2", "x2", 2),
    6: ("X2_d4", "x2", 4), 7: ("X2_d16", "x2", 16),
    8: ("X3", "x3", 0), 9: ("X4", "x4", 0), 10: ("X5", "x5", 0),
    11: ("X6_d0", "x6", 0), 12: ("X6_d4", "x6", 4),
    13: ("X7", "x7", 0), 14: ("X8", "x8", 0), 15: ("X9", "x9", 0),
    16: ("X10", "x10", 64), 17: ("X11", "x11", 0),
}
