from sys import stdout
# from typing import Callable, Iterable, Sequence

# input = stdin.readline
print = stdout.write

# GetTextCallback = Callable[[int, str], str]

# def get_response(default: int):
#     response = input().rstrip()
#     if not response:
#         return default
#     return int(response)

# def _default_get_text(*_):
#     return "[%d] %s\n"

# def get_response_iterable(iterable: Iterable[str], default: int = 0, get_text: GetTextCallback | None = None):
#     length = 0
#     if get_text is None:
#         get_text = _default_get_text
#     for i, text in enumerate(iterable, 1):
#         print(get_text(i, text) % (i, text,))
#         length += 1
#     response = input().rstrip()
#     if not response:
#         return default
#     response = int(response)
#     if response < 1 or response > length:
#         return default
#     return response

# def get_response_sequence(sequence: Sequence[str], default: int = 0, get_text: GetTextCallback | None = None) -> str:
#     return sequence[get_response_iterable(sequence, default, get_text) - 1]

# def get_response_dict[T](dict_: dict[str, T], default: int = 0, get_text: GetTextCallback | None = None) -> T:
#     return dict_[tuple(dict_.keys())[get_response_iterable(dict_, default, get_text) - 1]]

# def get_response_yes_or_no():
#     return input(2).rstrip().lower() == "y"