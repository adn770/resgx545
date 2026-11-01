// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! The data repository as the tests find it: `$RESGX545_DATA`, else `resgx545-data` beside
//! the tree (as `sgx-sim` does). Unit vectors live in `unit-vectors/` and scene vectors in
//! `scene-vectors/` under it (`$RESGX545_UNIT_VECTORS` and `$RESGX545_SCENE_VECTORS` override,
//! so that a set of vectors not yet landed can be replayed). They are outside `vectors/` so
//! that `sgx-sim`'s walk of it, and its replay counts, do not change (doc/specs/vectors.md 5).

use crate::{gz, sha256};
use std::path::{Path, PathBuf};

pub const UNIT_DIR: &str = "unit-vectors";
pub const SCENE_DIR: &str = "scene-vectors";

/// A data repository to read dumps from and the directories of vectors to replay.
#[derive(Debug, Clone)]
pub struct Ctx {
    pub root: Option<PathBuf>,
    pub units: Option<PathBuf>,
    pub scenes: Option<PathBuf>,
}

impl Ctx {
    pub fn from_env() -> Ctx {
        let root = match std::env::var_os("RESGX545_DATA") {
            Some(p) if !p.is_empty() => PathBuf::from(p),
            _ => PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../resgx545-data"),
        };
        let root = Some(root).filter(|r| r.is_dir());
        let pick = |var: &str, sub: &str| {
            std::env::var_os(var)
                .filter(|p| !p.is_empty())
                .map(PathBuf::from)
                .or_else(|| root.as_ref().map(|r| r.join(sub)))
                .filter(|d| d.is_dir())
        };
        Ctx {
            units: pick("RESGX545_UNIT_VECTORS", UNIT_DIR),
            scenes: pick("RESGX545_SCENE_VECTORS", SCENE_DIR),
            root,
        }
    }

    /// A file of the data repository, checked against its sha256 (of the file as stored).
    pub fn read(&self, rel: &str, sha256_hex: &str) -> Result<Vec<u8>, String> {
        let root = self.root.as_ref().ok_or("no data repository")?;
        let b = std::fs::read(root.join(rel)).map_err(|e| format!("{rel}: {e}"))?;
        if !sha256_hex.is_empty() && sha256::hex_digest(&b) != sha256_hex {
            return Err(format!("{rel}: sha256 differs from the vector's"));
        }
        Ok(b)
    }

    /// A gzip file of the data repository, decompressed, the digest of the .gz checked.
    pub fn read_gz(&self, rel: &str, sha256_hex: &str) -> Result<Vec<u8>, String> {
        gz::gunzip(&self.read(rel, sha256_hex)?).map_err(|e| format!("{rel}: {e}"))
    }
}

/// The files under `dir` whose name ends with `suffix`, in path order.
pub fn files(dir: &Path, suffix: &str) -> Vec<PathBuf> {
    fn walk(d: &Path, suffix: &str, out: &mut Vec<PathBuf>) {
        for e in std::fs::read_dir(d).into_iter().flatten().flatten() {
            let p = e.path();
            if p.is_dir() {
                walk(&p, suffix, out);
            } else if p.file_name().and_then(|n| n.to_str()).is_some_and(|n| n.ends_with(suffix)) {
                out.push(p);
            }
        }
    }
    let mut v = vec![];
    walk(dir, suffix, &mut v);
    v.sort();
    v
}

/// Little-endian dwords of a byte buffer (a trailing partial dword is dropped).
pub fn dwords(b: &[u8]) -> Vec<u32> {
    b.chunks_exact(4).map(|c| u32::from_le_bytes([c[0], c[1], c[2], c[3]])).collect()
}
