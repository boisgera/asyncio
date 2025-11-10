import asyncio
import random

counter = 0
lock = asyncio.Lock()

async def add(i):
    global counter
    await lock.acquire() # better: async with lock
    await asyncio.sleep(0.0)
    local_counter = counter
    await asyncio.sleep(0.0)
    local_counter += i
    await asyncio.sleep(0.0)
    counter = local_counter
    lock.release()

async def main():
    while True:
        print(counter)
        # 🔨 Hammer the counter!
        tasks = []
        for _ in range(1000):
            tasks.append(add(1))
            tasks.append(add(-1))
        random.shuffle(tasks)
        for task in tasks:
            asyncio.create_task(task)
        
        # 😴 Let the dust settle
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())