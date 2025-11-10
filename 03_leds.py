import asyncio
from math import inf

go_white = asyncio.Event()
go_black = asyncio.Event()


async def display_white():
    while True:
        print("⚪")
        go_black.set()
        await asyncio.sleep(1.0)
        await go_white.wait()
        go_white.clear()


async def display_black():
    while True:
        await go_black.wait()
        go_black.clear()
        print("⚫")
        await asyncio.sleep(0.5)
        print("⚫")
        go_white.set()
        await asyncio.sleep(0.5)


async def display_white_and_black():
    asyncio.create_task(display_white())
    asyncio.create_task(display_black())
    await asyncio.sleep(inf)


asyncio.run(display_white_and_black())
