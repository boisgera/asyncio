# Standard Library
import hashlib
import time

# Third-Party Libraries
import typer


def hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def solve_challenge(data: bytes, strength: int) -> bytes:
    num_bytes = 0
    while True:
        num_bits = num_bytes * 8
        for i in range(2**num_bits):
            data_ext = data + i.to_bytes(num_bytes)
            h = hash(data_ext)
            if h.endswith("00" * strength):
                return data_ext
        num_bytes += 1


def main(data: str, strength: int = 1) -> None:
    binary_data = data.encode("utf-8")
    print(f"{data = }")
    print(f"{strength = }")
    t0 = time.perf_counter()
    solution = solve_challenge(binary_data, strength)
    dt = time.perf_counter() - t0
    print(f"{solution = }")
    print(f"{solution.startswith(binary_data) = }")
    print(f"{hash(solution) = }")
    print(f"{hash(solution).endswith('00' * strength) = }")
    print(f"elapsed time: {dt:.1f} s")


if __name__ == "__main__":
    typer.run(main)
