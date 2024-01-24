from sys import stdin, stdout
from typing import Iterable

input = stdin.readline
print = stdout.write

def ask(default: int):
    response = input().rstrip()
    if not response:
        return default
    return int(response)

def ask_iterable(iterable: Iterable[str], default: int = 0):
    length = 0
    for i, text in enumerate(iterable, 1):
        print("[%d] %s\n" % (i, text,))
        length += 1
    response = input().rstrip()
    if not response:
        return default
    response = int(response)
    if response < 1 or response > length:
        return default
    return response

def ask_yes_no():
    return input(2).rstrip().lower() == "y"