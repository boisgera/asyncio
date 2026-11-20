import asyncio


async def display_white():
    while True:
        print("⚪")
        await asyncio.sleep(2.0)


async def display_black():
    while True:
        print("⚫")
        await asyncio.sleep(1.0)


async def display_white_and_black():
    _task_white = asyncio.create_task(display_white())
    _task_black = asyncio.create_task(display_black())
    while True:
        await asyncio.sleep(3600.0)


asyncio.run(display_white_and_black())
