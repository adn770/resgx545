// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2026 Josep Torra
//! pds-dis: disassemble a raw PDS program, little-endian 32-bit words, the
//! first <data_dwords> of which are the data segment, in the format of
//! tools/usse-dis/pds-dis (byte for byte):
//!
//!   <index>: 0x<HEX8>\t<text>
//!
//! Usage: pds-dis [--which] [--regs] <program.bin> <data_dwords> | --forms
//!
//! --forms lists the form table (index, mask, value, the bits the form reads,
//! pattern), as usse-dis --forms does. --which appends "\t#<n>", the index of
//! the form that decoded each instruction (-1 for none). --regs follows each
//! data dword's "data" with the register it loads: the segment is stored in
//! rows of four dwords, ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1].

use std::io::{BufWriter, Write};
use std::process::ExitCode;

/// C's strtoul(s, 0, 0) for the data count: hex (0x), octal (0) or decimal.
fn strtoul(s: &str) -> u64 {
    let s = s.trim_start();
    let (radix, d) = match s.strip_prefix("0x").or_else(|| s.strip_prefix("0X")) {
        Some(h) if h.starts_with(|c: char| c.is_ascii_hexdigit()) => (16, h),
        _ if s.starts_with('0') => (8, s),
        _ => (10, s),
    };
    let end = d.find(|c: char| !c.is_digit(radix)).unwrap_or(d.len());
    u64::from_str_radix(&d[..end], radix).unwrap_or(0)
}

fn main() -> ExitCode {
    let argv: Vec<String> = std::env::args().collect();
    let stdout = std::io::stdout();
    let mut out = BufWriter::new(stdout.lock());
    if argv.get(1).map(String::as_str) == Some("--forms") {
        for (i, f) in pds_isa::forms().enumerate() {
            let _ = writeln!(
                out,
                "{i}\t{:08X}\t{:08X}\t{:08X}\t{}",
                f.mask as u32,
                f.val as u32,
                f.bits() as u32,
                f.pat.unwrap_or("(reject)")
            );
        }
        return ExitCode::SUCCESS;
    }
    let (mut which, mut regs) = (false, false);
    let mut args = &argv[1..];
    while args.first().is_some_and(|a| a.starts_with("--")) {
        match args[0].as_str() {
            "--which" => which = true,
            "--regs" => regs = true,
            a => {
                eprintln!("{}: unknown option {a}", argv[0]);
                return ExitCode::from(2);
            }
        }
        args = &args[1..];
    }
    if args.len() < 2 {
        eprintln!("usage: {} [--which] [--regs] <program.bin> <data_dwords> | --forms", argv[0]);
        return ExitCode::from(2);
    }
    let data = match std::fs::read(&args[0]) {
        Ok(d) => d,
        Err(e) => {
            eprintln!("{}: {e}", args[0]);
            return ExitCode::from(1);
        }
    };
    let ndata = strtoul(&args[1]);
    for (i, b) in data.chunks_exact(4).enumerate() {
        let w = u32::from_le_bytes(b.try_into().unwrap());
        let mut text = if (i as u64) >= ndata {
            pds_isa::decode(w).text
        } else if regs {
            format!("data ds{}[{}]", i >> 1 & 1, (i >> 2) * 2 + (i & 1))
        } else {
            "data".to_string()
        };
        if which && (i as u64) >= ndata {
            let f = pds_isa::decode(w).form.map_or(-1, |f| f as i64);
            text += &format!("\t#{f}");
        }
        let _ = writeln!(out, "{i}: 0x{w:08X}\t{text}");
    }
    ExitCode::SUCCESS
}
