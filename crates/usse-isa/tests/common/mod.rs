// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! Shared helpers of the integration tests: where the local data lives, and a
//! deterministic word generator.
#![allow(dead_code)] // each test binary uses a part

use std::path::PathBuf;

/// The repository root (two levels above this crate).
pub fn repo() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

/// The closed-binary goldens, kept in the private data repository (never published):
/// $RESGX545_DATA_PRIVATE or a sibling ../resgx545-data-private. None when absent: the
/// tests that need it skip.
pub fn corpus() -> Option<PathBuf> {
    let p = std::env::var_os("RESGX545_DATA_PRIVATE")
        .map(PathBuf::from)
        .unwrap_or(repo().join("../resgx545-data-private"));
    p.is_dir().then_some(p)
}

/// The C decoder (tools/usse-dis, `make -C tools/usse-dis`): $USSE_DIS_C or
/// its build output. Without it the cross-checks fail, unless
/// SKIP_C_CROSSCHECK=1 asks to skip them (None).
pub fn c_usse_dis() -> Option<PathBuf> {
    let p =
        std::env::var_os("USSE_DIS_C").map(PathBuf::from).unwrap_or(repo().join("tools/usse-dis/usse-dis"));
    if p.is_file() {
        return Some(p);
    }
    assert!(
        skip_c_crosscheck(),
        "SKIPPED, NOT PASSED: build tools/usse-dis (make -C tools/usse-dis) or set SKIP_C_CROSSCHECK=1"
    );
    None
}

/// SKIP_C_CROSSCHECK=1: skip the cross-checks against the C tools.
pub fn skip_c_crosscheck() -> bool {
    std::env::var_os("SKIP_C_CROSSCHECK").is_some_and(|v| v == "1")
}

/// xorshift64*: the same words on every run.
pub struct Rng(u64);

impl Rng {
    pub fn new(seed: u64) -> Self {
        Rng(seed | 1)
    }

    pub fn next(&mut self) -> u64 {
        self.0 ^= self.0 >> 12;
        self.0 ^= self.0 << 25;
        self.0 ^= self.0 >> 27;
        self.0.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }
}
