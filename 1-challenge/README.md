Mining challenge
================================================================================

A small "proof of work", in the style of cryptocurrency mining: given some
data, find bytes to append so that the SHA-256 hash of the result ends with
`strength` zero bytes (`"00" * strength` in hexadecimal).

There is no shortcut: we try candidates one after the other until one works.
Each extra unit of `strength` makes the search about 256 times longer, which
makes it a good example of a long, **CPU-bound** computation. The question for
this section is: how do we stop it after a timeout?

Run any step with (`--timeout` exists from step 02 on):

```bash
uv run 1-challenge/11_challenge.py hello --strength 2
uv run 1-challenge/12_challenge.py hello --strength 3 --timeout 5
```


**Takeaways:**
- cooperative multitasking (CPU-bound code must yield with `await`),
- waiting for the first task to finish (`asyncio.wait` with `FIRST_COMPLETED`),
- waiting with a time limit (`asyncio.wait` with `timeout`),
- separating "what to compute" from "how long we are willing to wait".


Step 01: The solver
--------------------------------------------------------------------------------

`solve_challenge` tries every suffix of 0 bytes, then 1 byte, then 2 bytes,
and so on, and returns the first extended data whose hash matches:

```python
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
```

`main` (a [Typer](https://typer.tiangolo.com/) command line app) prints the
solution, checks it, and reports the elapsed time.

With a high `strength` the program can run for a very long time, and nothing
lets us give up after a while.


Step 02: Timeout mixed into the solver
--------------------------------------------------------------------------------

The simplest fix: every 1000 attempts, the solver checks the clock and exits
if the time budget is spent.

```python
            if i % 1000 == 0:
                dt = time.perf_counter() - t0
                if dt >= timeout:
                    error = f"error: timeout, {dt:.1f} s elapsed."
                    sys.exit(error)
```

That works, but:

- the solver now has two jobs: solving the challenge *and* watching the
  clock, so the timeout logic is tangled with the algorithm and

- every long-running function would need the same treatment.


Step 03: A separate timeout task
--------------------------------------------------------------------------------

We split the two jobs into two coroutines running as concurrent tasks:

- `solve_challenge` only searches;
- `check_timeout` only sleeps for `timeout` seconds and then raises
  `TimeoutError`.

```python
tasks = [
    asyncio.create_task(solve_challenge(data, strength)),
    asyncio.create_task(check_timeout(timeout)),
]
done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
first = done.pop()
```

- `asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)` returns as soon
  as one of the tasks finishes.

- `first.result()` gives either the solution or re-raises the timeout error.

There is a catch, and it is the key lesson of this section: **asyncio is
cooperative**. Tasks only switch at an `await`. A CPU-bound loop with no
`await` would hold the event loop forever, and the timeout task would never
get to run. That is why the solver calls `await asyncio.sleep(0.0)` every 1000
iterations: it means "pause for a moment and let the other tasks run".

The timeout task raises a regular `TimeoutError` rather than calling
`sys.exit` directly: `SystemExit` is a `BaseException`, and asyncio does not
handle those like ordinary errors inside tasks.


Step 04: Using `asyncio.wait`'s timeout
--------------------------------------------------------------------------------

asyncio already knows how to wait with a time limit, so we do not need our
own timeout task:

```python
solver_task = asyncio.create_task(solve_challenge(data, strength))
done, _ = await asyncio.wait([solver_task], timeout=timeout)
```

`asyncio.wait` returns when the task is done **or** when the time is up. If
the `done` set is empty, we timed out.

The solver still has to yield with `await asyncio.sleep(0.0)`, because the
event loop must get control back to notice that the deadline has passed.

Going further: `asyncio.wait_for(coro, timeout)` and the
`async with asyncio.timeout(...)` context manager are other ways to express
the same idea, and they also cancel the work that timed out.
