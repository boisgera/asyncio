import asyncio

go_white = asyncio.Event()
go_black = asyncio.Event()

# NOTA: Lock is not the propert construct here.
# TODO: make the "channel" (stream) version with anyio. Queue first!
# TODO: make a lock example with money transaction, credit and debit?
# Demo with and without lock. Copy the go example?

async def display_white():
    while True:
        print("⚪")
        go_black.set()
        await asyncio.sleep(1.0)
        await go_white.wait(); go_white.clear()

async def display_black():
    while True:
        await go_black.wait(); go_black.clear()
        print("⚫")
        await asyncio.sleep(0.5)
        print("⚫")
        go_white.set()
        await asyncio.sleep(1.5)

async def display_white_and_black():
    asyncio.create_task(display_white())
    asyncio.create_task(display_black())
    while True:
        await asyncio.sleep(1000.0)        

asyncio.run(display_white_and_black())
