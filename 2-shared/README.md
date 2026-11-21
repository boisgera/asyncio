Shared data
================================================================================

Many tasks update one shared global `counter`. Half of them add `+1`, the
other half add `-1`, in random order. Whatever the order, the counter should
always come back to `0`. Does it?

Every second, `main` prints the counter and then starts 2000 new tasks
("🔨 hammer the counter"). It then sleeps for a second to let them finish
("😴 let the dust settle").

Run any step with (stop with `Ctrl+C`):

```bash
uv run 2-shared/21_shared.py
```


Step 1: No suspension point, no problem ([`21_shared.py`](21_shared.py))
--------------------------------------------------------------------------------

```python
async def add(i):
    global counter
    local_counter = counter
    local_counter += i
    counter = local_counter
```

Output: `0 0 0 0 …`, as expected.

The update takes three steps (read, compute, write), but there is no `await`
between them. Since asyncio only switches tasks at an `await`, each `add`
runs from start to finish without being interrupted. Here the
read-modify-write is effectively **atomic**.


Step 2: A race condition ([`22_shared.py`](22_shared.py))
--------------------------------------------------------------------------------

We add `await asyncio.sleep(0.0)` between the steps. This stands in for any
real `await` (a database query, a network call…) that could appear in the
middle of an update.

Output: something like `0 -1 -2 -3 -2 …`. The counter drifts.

Each `await` lets the event loop switch to another task. Now many tasks
**read** the counter before any of them has **written** its result back. They
all compute from the same stale value, and each write overwrites the previous
one. Most updates are lost: this is a classic **race condition**.

Note that this happens with a single thread. Concurrency bugs are not only a
multithreading problem: anywhere a task can be suspended in the middle of a
read-modify-write is a potential race.


Step 3: Protecting the update with a lock ([`23_shared.py`](23_shared.py))
--------------------------------------------------------------------------------

An `asyncio.Lock` ensures that only one task at a time runs the critical
section:

```python
await lock.acquire()
...  # read, compute, write (with awaits in between)
lock.release()
```

Output: `0 0 0 0 …` again. A task that tries to acquire a lock that is
already held is suspended until the lock is released, so the updates can no
longer interleave.

As the comment in the code says, the idiomatic form is:

```python
async with lock:
    ...
```

It is shorter, and it releases the lock even if the critical section raises
an exception. With the explicit `acquire()`/`release()`, an exception would
leave the lock held forever.

**Takeaways:** asyncio code is safe *between* two `await`s, every `await` is a
point where other tasks can modify shared state, and `asyncio.Lock` (with
`async with`) protects critical sections.
