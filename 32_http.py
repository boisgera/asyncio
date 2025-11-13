# Python Standard Library
import asyncio
import time

# Third-Party Libraries
import httpx

ROOT = "https://httpbingo.org/"
URLS = [
    f"{ROOT}/image/jpeg",
    f"{ROOT}/image/png",
    f"{ROOT}/image/svg",
    f"{ROOT}/image/webp",
]


async def main():
    httpx_async = httpx.AsyncClient()
    t0 = time.perf_counter()
    response_promises = [httpx_async.get(url, follow_redirects=True) for url in URLS]
    responses = await asyncio.gather(*response_promises)
    dt = time.perf_counter() - t0
    print(f"elapsed time: {dt:.1f}")
    for response in responses:
        _ = response
        # print(f"response code (200 OK): {response.status_code}")
        # print(f"response content length (bytes): {len(response.content)}")


if __name__ == "__main__":
    asyncio.run(main())
