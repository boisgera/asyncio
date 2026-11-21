Blinking LEDs
================================================================================

Two "LEDs" print a white (⚪) and a black (⚫) dot at their own rhythm. They
are the simplest possible example of two activities that should run *at the
same time*.

Run any step with:

```bash
uv run 0-leds/01_leds.py
```

(Stop it with `Ctrl+C`.)


Step 1: Blocking code ([`01_leds.py`](01_leds.py))
--------------------------------------------------------------------------------

Each LED on its own is easy to write: an infinite loop that prints and then
sleeps with `time.sleep`.

```python
def display_white():
    while True:
        print("⚪")
        time.sleep(2.0)
```

The problem appears when we want **both** LEDs. `display_white()` never
returns, so calling `display_black()` after it does nothing. `time.sleep`
*blocks*: while it sleeps, the program cannot do anything else.

The only way out with plain functions is to merge the two loops by hand into
a single `display_white_and_black()` with a hard-coded sequence of prints and
sleeps. That works, but:

  - the merged schedule has to be worked out by hand, and it is easy to get
    wrong. Look closely: this version repeats every 3 s, so it is *not* the
    "white every 2 s, black every 1 s" pattern of the two separate functions;

  - the two independent behaviors are now tangled in one function. Changing
    a rhythm means rewriting the whole schedule.


Step 2: Coroutines and tasks ([`02_leds.py`](02_leds.py))
--------------------------------------------------------------------------------

We keep the original simple loops and make them asynchronous:

```python
async def display_white():
    while True:
        print("⚪")
        await asyncio.sleep(2.0)
```

  - `async def` defines a **coroutine function**. Calling it does not run its
    body. It returns a coroutine object that can be paused and resumed.

  - `await asyncio.sleep(2.0)` does not block the program. It suspends *this*
    coroutine and gives control back to the **event loop**, which can run
    something else in the meantime.

  - `asyncio.create_task(...)` hands a coroutine to the event loop, which
    then runs it concurrently with the other tasks.

  - `asyncio.run(...)` starts the event loop and runs the main coroutine.

The main coroutine starts the two tasks and then has to stay alive (here it
sleeps forever), because the program stops when `asyncio.run` returns. It
also keeps references to the tasks (`_task_white`, `_task_black`): the event
loop only holds weak references to tasks, so a task with no other reference
may be garbage-collected.

Now each LED is written independently and the event loop does the merging.
There is still only **one thread**. Concurrency comes from the coroutines
taking turns at each `await`.


Step 3: Coordinating tasks with events ([`03_leds.py`](03_leds.py))
--------------------------------------------------------------------------------

In step 2 the tasks are independent, so nothing controls *the order* in which
they print when they wake up at the same moment. Here we want a precise
choreography between the two LEDs, and we get it with `asyncio.Event`:

  - `event.set()` raises a flag;
  - `await event.wait()` suspends the task until the flag is raised (or
    returns immediately if it already is);
  - `event.clear()` lowers the flag again, so it can be reused for the next
    round.

The white LED prints, then signals `go_black`, and later waits for
`go_white`. The black LED waits for `go_black`, prints twice one second
apart, and signals `go_white`. Each task keeps its own logic, but they now
**synchronize** at well-defined points instead of depending on timer luck.

**Takeaways:** coroutines (`async def`), suspension points (`await`), tasks
(`create_task`), the event loop (`asyncio.run`) and a first synchronization
primitive (`asyncio.Event`).
