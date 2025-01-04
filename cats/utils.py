"Utility functions for file and string manipulation"

import string
from collections.abc import Callable
from math import sqrt
from typing import Any

############################
# String utility functions #
############################


def lines_from_file(path: str) -> list[str]:
    """Return a list of strings, one for each line in a file."""
    with open(path, 'r') as f:
        return [line.strip() for line in f.readlines()]


def remove_punctuation(s: str) -> str:
    """Return a string with the same contents as s, but with punctuation removed.

    >>> remove_punctuation("It's a lovely day, don't you think?")
    'Its a lovely day dont you think'
    >>> remove_punctuation('Its a lovely day dont you think')
    'Its a lovely day dont you think'
    """
    punctuation_remover: dict[int, None] = str.maketrans('', '', string.punctuation)  # type: ignore
    return s.strip().translate(punctuation_remover)


def lower(s: str) -> str:
    """Return a lowercased version of s.

    >>> lower('HELLO')
    'hello'
    >>> lower('World')
    'world'
    >>> lower('hello WORLD')
    'hello world'
    """
    return s.lower()


def split(s: str) -> list[str]:
    """Return a list of words contained in s, which are sequences of characters
    separated by whitespace (spaces, tabs, etc.).

    >>> split("It's a lovely day, don't you think?")
    ["It's", 'a', 'lovely', 'day,', "don't", 'you', 'think?']
    """
    return s.split()


#############################
# Keyboard layout functions #
#############################

KEY_LAYOUT: list[list[str]] = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='], ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']'], ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'"], ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'], [' ']]


def distance(p1: tuple[int, int], p2: tuple[int, int]) -> float:
    """Return the Euclidean distance between two points

    The Euclidean distance between two points, (x1, y1) and (x2, y2)
    is the square root of (x1 - x2) ** 2 + (y1 - y2) ** 2

    >>> distance((0, 1), (1, 1))
    1.0
    >>> distance((1, 1), (1, 1))
    0.0
    >>> round(distance((4, 0), (0, 4)), 3)
    5.657
    """
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def get_key_distances() -> dict[tuple[str, str], float]:
    """Return a new dictionary mapping key pairs to distances.

    Each key of the dictionary is a tuple of two
    letters as strings, and each value is the euclidean distance
    between the two letters on a standard QWERTY keyboard, normalized

    The scaling is constant, so a pair of keys that are twice
    as far have a distance value that is twice as great

    >>> distances = get_key_distances()
    >>> distances['a', 'a']
    0.0
    >>> round(distances['a', 'd'], 3)
    1.367
    >>> round(distances['d', 'a'], 3)
    1.367
    """
    key_distance: dict[tuple[str, str], float] = {}

    def compute_pairwise_distances(i: int, j: int, d: dict[tuple[str, str], float]) -> None:
        for x in range(len(KEY_LAYOUT)):
            for y in range(len(KEY_LAYOUT[x])):
                l1: str = KEY_LAYOUT[i][j]
                l2: str = KEY_LAYOUT[x][y]
                d[l1, l2] = distance((i, j), (x, y))

    for i in range(len(KEY_LAYOUT)):
        for j in range(len(KEY_LAYOUT[i])):
            compute_pairwise_distances(i, j, key_distance)

    max_value: float = max(key_distance.values())
    return {key: value * 8 / max_value for key, value in key_distance.items()}


def count(f: Callable[..., Any]) -> Callable[..., Any]:
    """Keeps track of the number of times a function f is called using the
    variable call_count

    >>> def factorial(n):
    ...     if n <= 1:
    ...         return 1
    ...     return n * factorial(n - 1)
    >>> factorial = count(factorial)
    >>> factorial(5)
    120
    >>> factorial.call_count
    5
    """

    def counted(*args) -> Any:
        counted.call_count += 1  # type: ignore
        return f(*args)

    counted.call_count: int = 0  # type: ignore
    return counted


###########################
# Miscellaneous functions #
###########################


def deep_convert_to_tuple(sequence) -> tuple[Any, ...] | Any:
    """Deeply converts tuples to lists.
    >>> deep_convert_to_tuple(5)
    5
    >>> deep_convert_to_tuple([2, 'hi'])
    (2, 'hi')
    >>> deep_convert_to_tuple([['These', 'are', 'all'], ['tuples.']])
    (('These', 'are', 'all'), ('tuples.',))
    """
    if isinstance(sequence, (list, tuple)):
        return tuple(deep_convert_to_tuple(item) for item in sequence)
    else:
        return sequence
