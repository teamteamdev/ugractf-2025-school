import itertools
import hashlib
import string

import bencodepy
import tqdm

f = open('flags.torrent', 'rb')
data = bencodepy.decode(f.read())
hash_list = data[b'info'][b'pieces']
piece_len = data[b'info'][b'piece length']
dictionary = string.printable

hashes = {}

for i in range(0, len(hash_list), 20):
    hash = bytes(hash_list[i:i + 20])
    n = i // 20
    if hash not in hashes:
        hashes[hash] = [n]
    else:
        hashes[hash].append(n)

decoded = {}

for i in tqdm.tqdm(itertools.product(dictionary, repeat=piece_len), total=len(dictionary)**piece_len):
    s = ''.join(i)
    m = hashlib.sha1()
    m.update(s.encode('utf-8'))
    hash = m.digest()
    if hash in hashes:
        for j in hashes[hash]:
            decoded[j] = s

for i in range(0, len(decoded)):
    print(decoded[i], end="")
