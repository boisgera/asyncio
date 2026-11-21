Mining challenge
================================================================================

A small "proof of work", in the style of cryptocurrency mining: given some
data, find bytes to append so that the SHA-256 hash of the result ends with
`strength` zero bytes (`"00" * strength` in hexadecimal).

There is no shortcut. We try candidates one after the other until one works.
Each extra unit of `strength` makes the search about 256 times longer, which
makes it a good example of a long, **CPU-bound** computation. The question for
this section is: how do we stop it after a timeout?

Run any step with (`--timeout` exists from step 2 on):

```bash
uv run 1-challenge/11_challenge.py hello --strength 2
uv run 1-challenge/12_challenge.py hello --strength 3 --timeout 5
```


Step 1: The solver ([`11_challenge.py`](11_challenge.py))
--------------------------------------------------------------------------------

`solve_challenge` tries every suffix of 0 bytes, then 1 byte, then 2 bytes,
and so on, and returns the first extended data whose hash matches. `main`
(a [Typer](https://typer.tiangolo.com/) command line app) prints the solution,
checks it, and reports the elapsed time.

With a high `strength` the program can run for a very long time, and nothing
lets us give up after a while.


Step 2: Timeout mixed into the solver ([`12_challenge.py`](12_challenge.py))
--------------------------------------------------------------------------------

The simplest fix: every 1000 attempts, the solver checks the clock and exits
if the time budget is spent.

It works, but the solver now has two jobs: solving the challenge *and*
watching the clock. The timeout logic is tangled with the algorithm, and
every long-running function would need the same treatment.


Step 3: A separate timeout task ([`13_challenge.py`](13_challenge.py))
--------------------------------------------------------------------------------

We split the two jobs into two coroutines running as concurrent tasks:

  - `solve_challenge` only searches;
  - `check_timeout` only sleeps for `timeout` seconds and then raises
    `TimeoutError`.

`asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)` returns as soon as
one of them finishes. `first.result()` gives either the solution or re-raises
the timeout error.

There is a catch, and it is the key lesson of this section: **asyncio is
cooperative**. Tasks only switch at an `await`. A CPU-bound loop with no
`await` would hold the event loop forever, and the timeout task would never
get to run. That is why the solver calls `await asyncio.sleep(0.0)` every 1000
iterations: it means "pause for a moment and let the other tasks run".

(As the comment in the code explains, the timeout task raises a regular
`TimeoutError` rather than calling `sys.exit` directly. `SystemExit` is a
`BaseException`, and asyncio does not handle those like ordinary errors
inside tasks.)


Step 4: Using `asyncio.wait`'s timeout ([`14_challenge.py`](14_challenge.py))
--------------------------------------------------------------------------------

asyncio already knows how to wait with a time limit, so we do not need our
own timeout task. `asyncio.wait([solver_task], timeout=timeout)` returns when
the task is done **or** when the time is up. If the `done` set is empty, we
timed out.

The solver still has to yield with `await asyncio.sleep(0.0)`, because the
event loop must get control back to notice that the deadline has passed.

Going further: `asyncio.wait_for(coro, timeout)` and the
`async with asyncio.timeout(...)` context manager are other ways to express
the same idea, and they also cancel the work that timed out.

**Takeaways:** cooperative multitasking (CPU-bound code must yield),
`asyncio.wait` with `FIRST_COMPLETED` or a `timeout`, and separating "what to
compute" from "how long we are willing to wait".
