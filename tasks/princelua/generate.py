import sys
import json

SALT = "48vbjw8ds1vFD0ds"
FLAG_BASE = "ugra_princ3ss_1s_fre3d_by_y0u_"


def fnv1a(s: str) -> int:
    h = 2166136261
    for c in s.encode():
        h ^= c
        h = (h * 16777619) & 0xffffffff
    return h


def main():
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <user_id> ...", file=sys.stderr)
        sys.exit(1)
    token = f"{fnv1a(sys.argv[1]):x}"
    flag = f"{FLAG_BASE}{fnv1a(token + SALT):x}"
    print(json.dumps({
        "flags": [flag],
        "urls": [f"https://princelua.{{hostname}}/{token}"]
    }))


if __name__ == "__main__":
    main()
