#!/bin/sh
[[ -n $SOLVE ]] || { echo Usage: SOLVE=/path/to/suspicious.pcap ./solve.sh && exit 1; }

tshark -r "$SOLVE" -T fields -e tcp.payload 'tcp.dstport == 6666' | xxd -r -p | SOLVE=1 python3 generator.py
