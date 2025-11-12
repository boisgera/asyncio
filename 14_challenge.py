# Standard Library
import asyncio
import hashlib
import sys
import time

# Third-Party Libraries
import typer


def hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


async def solve_challenge(data: bytes, strength: int) -> bytes:
    num_bytes = 0
    while True:
        num_bits = num_bytes * 8
        for i in range(2**num_bits):
            data_ext = data + i.to_bytes(num_bytes)
            h = hash(data_ext)
            if h.endswith("00" * strength):
                return data_ext
            if i % 1000 == 0:
                await asyncio.sleep(0.0)
        num_bytes += 1


async def tasks(data: str, strength: int, timeout: float) -> bytes:
    solver_task = asyncio.create_task(solve_challenge(data, strength))
    try:
        t0 = time.perf_counter()
        result = await asyncio.wait_for(solver_task, timeout)
    except asyncio.TimeoutError:
        # # We should also cancel the solver task and manage its unwinding.
        # solver_task.cancel()
        # try:
        #     await solver_task
        # except asyncio.CancelledError:
        #     pass
        dt = time.perf_counter() - t0
        error = f"error: timeout, {dt:.1f} s elapsed."
        sys.exit(error)
    return result


def main(data: str, strength: int = 1, timeout: float = 10.0) -> None:
    data = data.encode("utf-8")
    print(f"{data = }")
    print(f"{strength = }")
    t0 = time.perf_counter()
    solution = asyncio.run(tasks(data, strength, timeout))
    dt = time.perf_counter() - t0
    print(f"{solution = }")
    print(f"{solution.startswith(data) = }")
    print(f"{hash(solution) = }")
    print(f"{hash(solution).endswith('00' * strength) = }")
    print(f"elapsed time: {dt:.1f} s")


if __name__ == "__main__":
    typer.run(main)
