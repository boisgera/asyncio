import httpx
import time

ROOT = "https://httpbingo.org/"
URLS = [
    f"{ROOT}/image/jpeg",
    f"{ROOT}/image/png",
    f"{ROOT}/image/svg",
    f"{ROOT}/image/webp",
]


def main():
    t0 = time.perf_counter()
    responses = []
    for url in URLS:
        responses.append(httpx.get(url, follow_redirects=True))
    dt = time.perf_counter() - t0
    print(f"elapsed time: {dt:.1f}")
    for response in responses:
        _ = response
        #print(f"response code (200 OK): {response.status_code}")
        #print(f"response content length (bytes): {len(response.content)}")


if __name__ == "__main__":
    main()
