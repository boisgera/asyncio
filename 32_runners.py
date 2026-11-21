# Python Standard Library
import asyncio
import random


# Third-Party
import tqdm


async def update(bar):
    while bar.n < 100:
        progress = random.randint(0, 10)
        bar.update(min(progress, 100 - bar.n))
        await asyncio.sleep(1.0)

async def main():
    bars = [
        tqdm.tqdm(
            desc=f"task {i}", 
            total=100, 
            position=i
        ) 
        for i in range(5)
    ]
    tasks = [asyncio.create_task(update(bar)) for bar in bars]
    await asyncio.wait(tasks)
    for bar in bars:
        bar.close()

if __name__ == "__main__":
    asyncio.run(main())
