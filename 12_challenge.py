# Standard Library
import hashlib
import sys
import time

# Third-Party Libraries
import typer


def hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def solve_challenge(data: bytes, strength: int, timeout: float) -> bytes:
    num_bytes = 0
    t0 = time.perf_counter()
    while True:
        num_bits = num_bytes * 8
        for i in range(2**num_bits):
            data_ext = data + i.to_bytes(num_bytes)
            h = hash(data_ext)
            if h.endswith("00" * strength):
                return data_ext
            if i % 1000 == 0:
                dt = time.perf_counter() - t0
                if dt >= timeout:
                    error = f"error: timeout, {dt:.1f} s elapsed."
                    sys.exit(error)
        num_bytes += 1


def main(data: str, strength: int = 1, timeout: float = 10.0) -> None:
    data = data.encode("utf-8")
    print(f"{data = }")
    print(f"{strength = }")
    t0 = time.perf_counter()
    solution = solve_challenge(data, strength, timeout)
    dt = time.perf_counter() - t0
    print(f"{solution = }")
    print(f"{solution.startswith(data) = }")
    print(f"{hash(solution) = }")
    print(f"{hash(solution).endswith('00' * strength) = }")
    print(f"elapsed time: {dt:.1f} s")


if __name__ == "__main__":
    typer.run(main)
