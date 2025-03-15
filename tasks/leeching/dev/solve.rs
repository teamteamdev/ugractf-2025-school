#!/usr/bin/env -S cargo +nightly -Zscript
---cargo
[package]
edition = "2024"

[dependencies]
itertools = "0.14"
serde = "1"
serde_bencode = "0.2"
serde_bytes = "0.11"
serde_derive = "1"
sha1 = { version = "0.10", features = ["asm"] }

[profile.dev]
opt-level = 3
---

#![feature(slice_as_chunks)]

use itertools::Itertools;
use serde_derive::Deserialize;
use sha1::{Digest as _, Sha1};
use std::collections::hash_map::{Entry, HashMap};
use std::time::Instant;

#[derive(Deserialize)]
struct Info {
    pieces: serde_bytes::ByteBuf,
    #[serde(rename = "piece length")]
    piece_length: i64,
    length: i64,
}

#[derive(Deserialize)]
struct Torrent {
    info: Info,
}

fn main() {
    let filename = std::env::var("SOLVE").expect("SOLVE=path/to/file.torrent ./solve.rs");
    let contents = std::fs::read(&filename).expect("read");
    let Torrent {
        info: Info {
            length,
            piece_length,
            pieces,
        },
    } = serde_bencode::de::from_bytes(&contents).expect("torrent");

    let length: usize = length.try_into().expect("length is long?");
    let piece_length: usize = piece_length.try_into().expect("piece_length is long?");
    let (pieces, last) = pieces.as_chunks::<20>();
    assert!(last.is_empty(), "pieces are of uneven sizes?");

    let mut hash_positions = HashMap::<[u8; 20], Vec<usize>>::new();
    for (index, piece) in pieces.iter().enumerate() {
        hash_positions.entry(*piece).or_default().push(index);
    }

    let mut text: Vec<u8> = vec![b'_'; length as usize];

    let start = Instant::now();

    for partial_length in [length % piece_length, piece_length] {
        for (count, value) in (0..partial_length)
            .map(|_| 0..=255u8)
            .multi_cartesian_product()
            .enumerate()
        {
            // Display some progress...
            if count & ((1 << 20) - 1) == 0 {
                eprint!("\r\x1b[KCracking, {}M done...", count >> 20);
            }

            let hash: [u8; 20] = Sha1::digest(&value).into();
            if let Entry::Occupied(indices) = hash_positions.entry(hash) {
                for index in indices.remove() {
                    let begin = index * piece_length;
                    text[begin..begin + partial_length].copy_from_slice(&value);
                }
            }

            if hash_positions.is_empty() {
                break;
            }
        }
    }

    let newname = filename + ".cracked";
    std::fs::write(&newname, &text).expect("save");

    eprintln!(" check {newname} for raw data. Took {:?}", start.elapsed());

    println!("{}", String::from_utf8_lossy(&text));
}
