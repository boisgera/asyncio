import asyncio
import random

counter = 0


async def add(i):
    global counter
    local_counter = counter
    local_counter += i
    counter = local_counter


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
