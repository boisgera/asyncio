import marimo

__generated_with = "0.17.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import asyncio
    from pathlib import Path
    import tempfile
    import time
    return asyncio, tempfile


@app.cell
def _():
    import httpx
    return (httpx,)


@app.cell
def _():
    ROOT = "https://httpbingo.org"
    return (ROOT,)


@app.cell
def _(ROOT):
    URLS = [
        f"{ROOT}/image/jpeg",
        f"{ROOT}/image/png",
        f"{ROOT}/image/webp",
    ]
    return (URLS,)


@app.cell
def _(URLS, httpx):
    responses = []
    for _url in URLS:
        responses.append(httpx.get(_url, follow_redirects=True))
    responses
    return (responses,)


@app.cell
def _(mo, tempfile):
    def image(image_bytes):
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as file:
            file.write(image_bytes)
        return mo.image(file.name)
    return (image,)


@app.cell
def _(image, responses):
    [image(r.content) for r in responses]
    return


@app.cell
def _(URLS, httpx):
    async_httpx = httpx.AsyncClient()
    response_coroutines = []
    for _url in URLS:
        response_coroutines.append(async_httpx.get(_url, follow_redirects=True))
    response_coroutines
    return (response_coroutines,)


@app.cell
async def _(asyncio, response_coroutines):
    responses_async = await asyncio.gather(*response_coroutines)
    responses_async
    return (responses_async,)


@app.cell
def _(image, responses_async):
    [image(r.content) for r in responses_async]
    return


if __name__ == "__main__":
    app.run()
