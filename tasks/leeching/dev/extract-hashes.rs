#!/usr/bin/env -S cargo +nightly -Zscript
---cargo
[package]
edition = "2024"

[dependencies]
hex = "0.4"
serde = "1"
serde_bencode = "0.2"
serde_bytes = "0.11"
serde_derive = "1"

[profile.dev]
opt-level = 3
---

#![feature(slice_as_chunks)]

use serde_derive::Deserialize;

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

    dbg!(length);
    dbg!(piece_length);
    for hash in pieces {
        println!("{}", hex::encode(hash));
    }
}
