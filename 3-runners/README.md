Runners
================================================================================

Five "runners" race to 100%. Each one is shown as a
[tqdm](https://tqdm.github.io/) progress bar that moves forward by a random
amount (0 to 10%) every second.

Run any step with:

```bash
uv run 3-runners/31_runners.py
```


**Takeaways:**
- one task per independent activity (`create_task`),
- waiting for a group of tasks (`asyncio.wait`),
- broadcasting a signal to many tasks (`asyncio.Event`).


Step 01: One loop runs everyone
--------------------------------------------------------------------------------

Without asyncio, a single loop has to move every runner. Each second it goes
over the runners that are still active, advances them, removes the ones that
reached 100%, and then sleeps:

```python
active = bars.copy()
while active:
    for bar in active:
        progress = random.randint(0, 10)
        bar.update(min(progress, 100 - bar.n))
    active = [bar for bar in active if bar.n < 100]
    time.sleep(1.0)
```

That works, but:

- all the bookkeeping is manual: we keep the list of active runners
  ourselves and remove the finished ones and

- the behavior of *one* runner ("advance randomly until 100%") is spread
  across a loop that deals with *all* of them.


Step 02: One task per runner
--------------------------------------------------------------------------------

Each runner gets its own coroutine, which describes the behavior of a single
runner and nothing else:

```python
async def update(bar):
    while bar.n < 100:
        progress = random.randint(0, 10)
        bar.update(min(progress, 100 - bar.n))
        await asyncio.sleep(1.0)
```

- `main` creates one task per bar with `asyncio.create_task(update(bar))`.

- `await asyncio.wait(tasks)` waits for all of them (by default
  `asyncio.wait` returns when *all* tasks are done).

The event loop does the scheduling: there is no list of active runners and no
manual removal. Each task just ends when its runner finishes.

This is the same move as in [the LEDs section](../0-leds/): from one loop
that interleaves everything by hand to independent tasks.


Step 03: The starting gun
--------------------------------------------------------------------------------

In a real race, runners wait for the start signal. A shared `asyncio.Event`
plays the starting gun:

```python
start = asyncio.Event()

async def update(bar):
    await start.wait()
    ...
```

- every runner begins with `await start.wait()` and stays on the starting
  line;
- `main` creates all the tasks, waits 3 seconds (the bars are visible at
  0%), then calls `start.set()`;
- all the runners are released at once.

One `Event` can release any number of waiting tasks. This makes it a simple
way to make sure everything is ready before work starts.
