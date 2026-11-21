Blinking LEDs
================================================================================

We have two "LEDs": 
- the white one (⚪) is displayed every two seconds and 
- the black one (⚫) is displayed every second.


**Takeaways:** 
- coroutines (`async def`), 
- suspension points (`await`), 
- tasks (`create_task`), 
- the event loop (`asyncio.run`),
- events (`asyncio.Event`).


Step 01: Synchronous code
--------------------------------------------------------------------------------

Each LED on its own is easy to write: an infinite loop that prints and then
sleeps with `time.sleep`.

```python
def display_white():
    while True:
        print("⚪")
        time.sleep(2.0)
```

```python
def display_black():
    while True:
        print("⚫")
        time.sleep(1.0)
```

The problem appears when we want both LEDs at the same time, concurrently. 
There is no easy way to compose `display_white` and `display_black` to
do so, you have to  merge the two loops by hand into a single 
`display_white_and_black()` with a hard-coded sequence of prints and
sleeps. That works, but:

  - the merged schedule has to be worked out by hand and

  - changing any individual behavior means rewriting the whole function.


Step 02: Coroutines and tasks
--------------------------------------------------------------------------------

We keep the original simple loops and make them asynchronous:

```python
async def display_white():
    while True:
        print("⚪")
        await asyncio.sleep(2.0)
```

- `async def` defines a **coroutine function**. Calling it does not run its
  body but returns a **coroutine object** that can be started, paused and 
  resumed.

- `await asyncio.sleep(2.0)` does not block the program, but suspends the
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


Step 3: Coordinating tasks with events
--------------------------------------------------------------------------------

In step 2 the tasks are independent, so nothing controls *the order* in which
they print when they wake up at the same moment. If we want a precise
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

