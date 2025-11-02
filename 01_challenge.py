import hashlib
import sys

# TODO: 
#   1. this
#   2. version with limit on time
#   3. async version that composes the alarm and the search

def hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def solve_challenge(data: bytes, strength: int = 1, pad: int = 2) -> bytes:
    num_bits = (strength + pad) * 8
    for i in range(2**num_bits):
        data_ext = data + i.to_bytes(4)
        h = hash(data_ext)
        if h.endswith("00" * strength):
            return data_ext
    else:
        error = "cannot solve challenge"
        raise RuntimeError(error)

def main() -> None:
    try:
        data = sys.argv[1].encode("utf-8")
    except IndexError:
        data = b"Hello world!"
    print(data)
    strength = 3
    result = solve_challenge(data, strength)
    print(result)
    print(result.startswith(data))
    h = hash(result)
    print(h)
    print(h.endswith("00" * strength))

if __name__ == "__main__":
    main()