object "Ugra" {
    code {
        datacopy(0, dataoffset("runtime"), datasize("runtime"))
        return(0, datasize("runtime"))
    }
    object "runtime" {
        code {
            function shuffleBlock(b) -> result {
                let b0 := shr(0x70, shl(0x0, and(b, 0xffff000000000000000000000000000000000000000000000000000000000000)))
                let b1 := shr(0x80, shl(0x10, and(b, 0x0000ffff00000000000000000000000000000000000000000000000000000000)))
                let b2 := shr(0xb0, shl(0x20, and(b, 0x00000000ffff0000000000000000000000000000000000000000000000000000)))
                let b3 := shr(0x40, shl(0x30, and(b, 0x000000000000ffff000000000000000000000000000000000000000000000000)))
                let b4 := shr(0xc0, shl(0x40, and(b, 0x0000000000000000ffff00000000000000000000000000000000000000000000)))
                let b5 := shr(0x30, shl(0x50, and(b, 0x00000000000000000000ffff0000000000000000000000000000000000000000)))
                let b6 := shr(0x90, shl(0x60, and(b, 0x000000000000000000000000ffff000000000000000000000000000000000000)))
                let b7 := shr(0x20, shl(0x70, and(b, 0x0000000000000000000000000000ffff00000000000000000000000000000000)))
                let b8 := shr(0xd0, shl(0x80, and(b, 0x00000000000000000000000000000000ffff0000000000000000000000000000)))
                let b9 := shr(0xf0, shl(0x90, and(b, 0x000000000000000000000000000000000000ffff000000000000000000000000)))
                let b10 := shr(0x60, shl(0xa0, and(b, 0x0000000000000000000000000000000000000000ffff00000000000000000000)))
                let b11 := shr(0xa0, shl(0xb0, and(b, 0x00000000000000000000000000000000000000000000ffff0000000000000000)))
                let b12 := shr(0xe0, shl(0xc0, and(b, 0x000000000000000000000000000000000000000000000000ffff000000000000)))
                let b13 := shr(0x0, shl(0xd0, and(b, 0x0000000000000000000000000000000000000000000000000000ffff00000000)))
                let b14 := shr(0x50, shl(0xe0, and(b, 0x00000000000000000000000000000000000000000000000000000000ffff0000)))
                let b15 := shr(0x10, shl(0xf0, and(b, 0x000000000000000000000000000000000000000000000000000000000000ffff)))

                result := or(b0, or(b1, or(b2, or(b3, or(b4, or(b5, or(b6, or(b7, or(b8, or(b9, or(b10, or(b11, or(b12, or(b13, or(b14, b15)))))))))))))))
            }
            
            let perm1 := xor(shuffleBlock(calldataload(0x44)), 0xd087f450a472071dad29898d9a036e7a755f80efa5f7146e1785f509e0741ecd)
            let perm2 := xor(shuffleBlock(calldataload(0x64)), 0xd087f450a472071dad29898d9a036e7a755f80efa5f7146e1785f509e0741ecd)
            
            if iszero(eq(perm1, 0xa2f59729c51c6842df50ece3e3731b1d073eed8ad1984b0d67f1865683017dbf)) {
                revert(0, 0)
            }
            if iszero(eq(perm2, 0x91c6b511d41a687adf50c8ccdb4231141a2bf28ee4b64b0d67f18c56a1355f8c)) {
                revert(0, 0)
            }

            mstore(0, 1)
            return(0, 0x20)
        }
    }
}

