import time


def display_white():
    while True:
        print("⚪")
        time.sleep(2.0)


def display_black():
    while True:
        print("⚫")
        time.sleep(1.0)


def display_white_and_black():
    while True:
        print("⚪")
        print("⚫")
        time.sleep(1.0)
        print("⚫")
        time.sleep(1.0)


# display_white()
# display_black()
display_white_and_black()
