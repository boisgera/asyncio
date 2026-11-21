# Python Standard Library
import random
import time

# Third-Party
import tqdm


def main():
    bars = [
        tqdm.tqdm(
            desc=f"task {i}", 
            total=100, 
            position=i
        ) 
        for i in range(5)
    ]

    active = bars.copy()
    while active:
        for bar in active:
            progress = random.randint(0, 10)
            bar.update(min(progress, 100 - bar.n))
        active = [bar for bar in active if bar.n < 100]
        time.sleep(1.0)
    for bar in bars:
        bar.close()

if __name__ == "__main__":
    main()
