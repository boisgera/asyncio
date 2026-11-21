HTTP requests
================================================================================

Download a few images from [httpbingo.org](https://httpbingo.org), a test
HTTP service, with the [HTTPX](https://www.python-httpx.org/) library.

In the previous sections, most of the waiting was simulated with
`asyncio.sleep`. Here the waiting is real: most of the time of an HTTP request
is spent waiting for the network. This is the kind of **I/O-bound** work where
asyncio really helps.

Run the scripts with:

```bash
uv run 4-http/41_http.py
uv run 4-http/42_http.py
```

and open the notebook with:

```bash
uv run marimo edit 4-http/43_http.py
```


Step 1: Sequential requests ([`41_http.py`](41_http.py))
--------------------------------------------------------------------------------

`httpx.get` is a regular blocking call. The requests are sent one after the
other, and each one waits for the previous one to finish. The total time is
roughly the **sum** of the individual request times.


Step 2: Concurrent requests ([`42_http.py`](42_http.py))
--------------------------------------------------------------------------------

`httpx.AsyncClient` offers the same API, but its methods are coroutines:

```python
client = httpx.AsyncClient()
coroutines = [client.get(url, follow_redirects=True) for url in URLS]
responses = await asyncio.gather(*coroutines)
```

  - Building the list does **not** send anything. Calling `client.get(...)`
    only creates coroutine objects.

  - `asyncio.gather` runs them all concurrently and returns their results
    **in the same order** as its arguments (not in the order they finish).

While one request waits for the network, the event loop moves the others
forward. The total time is now roughly that of the **slowest** request.
Compare the elapsed times printed by the two scripts.

Good practice is to use the client as an async context manager, so that its
network connections are properly closed:

```python
async with httpx.AsyncClient() as client:
    ...
```


Step 3: Async in a notebook ([`43_http.py`](43_http.py))
--------------------------------------------------------------------------------

The same experiment in a [marimo](https://marimo.io) notebook, with the
downloaded images displayed in it:

  - The first cells do the sequential version with `httpx.get` and show the
    images.

  - Then a cell builds the list of `AsyncClient.get(...)` calls. Its output
    shows **coroutine objects**, not responses. This confirms that nothing has
    run yet.

  - The next cell runs them with `await asyncio.gather(...)` directly at the
    top level of the cell.

Top-level `await` works because the notebook already runs an event loop. In
that context you write `await ...` and *not* `asyncio.run(...)`. The latter
would fail, because it cannot start a second event loop inside a running one.

**Takeaways:** asyncio is most useful for I/O-bound work, coroutines do
nothing until awaited, `asyncio.gather` runs them concurrently and collects
their results in order, and notebooks such as marimo (or Jupyter) let you
`await` at the top level.
