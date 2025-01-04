"""Typing test implementation"""

import random
from collections.abc import Callable
from datetime import datetime
from itertools import pairwise
from typing import Any

from ucb import interact, main, trace
from utils import (
    count,
    deep_convert_to_tuple,
    lines_from_file,
    lower,
    remove_punctuation,
    split,
)

###########
# Phase 1 #
###########


def pick(paragraphs: list[str], select: Callable[[str], bool], k: int) -> str:
    """Return the Kth paragraph from PARAGRAPHS for which the SELECT returns True.
    If there are fewer than K such paragraphs, return an empty string.

    Arguments:
        paragraphs: a list of strings representing paragraphs
        select: a function that returns True for paragraphs that meet its criteria
        k: an integer

    >>> ps = ['hi', 'how are you', 'fine']
    >>> s = lambda p: len(p) <= 4
    >>> pick(ps, s, 0)
    'hi'
    >>> pick(ps, s, 1)
    'fine'
    >>> pick(ps, s, 2)
    ''
    """
    # BEGIN PROBLEM 1
    '*** YOUR CODE HERE ***'
    filtered_paragraphs: list[str] = [p for p in paragraphs if select(p)]
    return filtered_paragraphs[k] if k < len(filtered_paragraphs) else ''
    # END PROBLEM 1


def about(subject: list[str]) -> Callable[[str], bool]:
    """Return a function that takes in a paragraph and returns whether
    that paragraph contains one of the words in SUBJECT.

    Arguments:
        subject: a list of words related to a subject

    >>> about_dogs = about(['dog', 'dogs', 'pup', 'puppy'])
    >>> pick(['Cute Dog!', 'That is a cat.', 'Nice pup!'], about_dogs, 0)
    'Cute Dog!'
    >>> pick(['Cute Dog!', 'That is a cat.', 'Nice pup.'], about_dogs, 1)
    'Nice pup.'
    """
    assert all(lower(x) == x for x in subject), 'subjects should be lowercase.'

    # BEGIN PROBLEM 2
    '*** YOUR CODE HERE ***'
    s: set[str] = set(subject)
    return lambda p: any(w in s for w in remove_punctuation(p).lower().split())
    # END PROBLEM 2


def accuracy(typed: str, source: str):
    """Return the accuracy (percentage of words typed correctly) of TYPED
    compared to the corresponding words in SOURCE.

    Arguments:
        typed: a string that may contain typos
        source: a model string without errors

    >>> accuracy('Cute Dog!', 'Cute Dog.')
    50.0
    >>> accuracy('A Cute Dog!', 'Cute Dog.')
    0.0
    >>> accuracy('cute Dog.', 'Cute Dog.')
    50.0
    >>> accuracy('Cute Dog. I say!', 'Cute Dog.')
    50.0
    >>> accuracy('Cute', 'Cute Dog.')
    100.0
    >>> accuracy('', 'Cute Dog.')
    0.0
    >>> accuracy('', '')
    100.0
    """
    typed_words: list[str] = split(typed)
    source_words: list[str] = split(source)
    # BEGIN PROBLEM 3
    '*** YOUR CODE HERE ***'
    if not typed_words and not source_words:
        return 100.0
    if not typed_words or not source_words:
        return 0.0
    counts: int = sum(1 for w1, w2 in zip(typed_words, source_words) if w1 == w2)
    return counts / len(typed_words) * 100
    # END PROBLEM 3


def wpm(typed: str, elapsed: int | float):
    """Return the words-per-minute (WPM) of the TYPED string.

    Arguments:
        typed: an entered string
        elapsed: an amount of time in seconds

    >>> wpm('hello friend hello buddy hello', 15)
    24.0
    >>> wpm('0123456789', 60)
    2.0
    """
    assert elapsed > 0, 'Elapsed time must be positive'
    # BEGIN PROBLEM 4
    '*** YOUR CODE HERE ***'
    return len(typed) * 12 / elapsed
    # END PROBLEM 4


################
# Phase 4 (EC) #
################


def memo(f: Callable[..., Any]) -> Callable[..., Any]:
    """A general memoization decorator."""
    cache = {}

    def memoized(*args: Any) -> Any:
        immutable_args: tuple[Any, ...] | Any = deep_convert_to_tuple(args)  # convert *args into a tuple representation
        if immutable_args not in cache:
            result = f(*immutable_args)
            cache[immutable_args] = result
            return result
        return cache[immutable_args]

    return memoized


def memo_diff(diff_function: Callable[[str, str, int], int]) -> Callable[[str, str, int], int]:
    """A memoization function."""
    cache: dict[tuple[str, str, int], int] = {}

    def memoized(typed: str, source: str, limit: int) -> int:
        # BEGIN PROBLEM EC
        "*** YOUR CODE HERE ***"
        key: tuple[str, str, int] = (typed, source, limit)
        if key in cache:
            return cache[key]
        result: int = diff_function(typed, source, limit)
        cache[key] = result
        return result
        # END PROBLEM EC

    return memoized


###########
# Phase 2 #
###########


@memo
def autocorrect(
    typed_word: str,
    word_list: list[str],
    diff_function: Callable[[str, str, int], int],
    limit: int,
) -> str:
    """Returns the element of WORD_LIST that has the smallest difference
    from TYPED_WORD based on DIFF_FUNCTION. If multiple words are tied for the smallest difference,
    return the one that appears closest to the front of WORD_LIST. If the
    difference is greater than LIMIT, return TYPED_WORD instead.

    Arguments:
        typed_word: a string representing a word that may contain typos
        word_list: a list of strings representing source words
        diff_function: a function quantifying the difference between two words
        limit: a number

    >>> ten_diff = lambda w1, w2, limit: 10  # Always returns 10
    >>> autocorrect('hwllo', ['butter', 'hello', 'potato'], ten_diff, 20)
    'butter'
    >>> first_diff = lambda w1, w2, limit: (1 if w1[0] != w2[0] else 0)  # Checks for matching first char
    >>> autocorrect('tosting', ['testing', 'asking', 'fasting'], first_diff, 10)
    'testing'
    """
    # BEGIN PROBLEM 5
    '*** YOUR CODE HERE ***'
    if typed_word in word_list:
        return typed_word
    diff_list: list[int] = [diff_function(typed_word, word, limit) for word in word_list]
    index: int = min(range(len(diff_list)), key=diff_list.__getitem__)
    if diff_list[index] > limit:
        return typed_word
    return word_list[index]
    # END PROBLEM 5


def furry_fixes(typed: str, source: str, limit: int) -> int:
    """A diff function for autocorrect that determines how many letters
    in TYPED need to be substituted to create SOURCE, then adds the difference in
    their lengths and returns the result.

    Arguments:
        typed: a starting word
        source: a string representing a desired goal word
        limit: a number representing an upper bound on the number of chars that must change

    >>> big_limit = 10
    >>> furry_fixes('nice', 'rice', big_limit)  # Substitute: n -> r
    1
    >>> furry_fixes('range', 'rungs', big_limit)  # Substitute: a -> u, e -> s
    2
    >>> furry_fixes('pill', 'pillage', big_limit)  # Don't substitute anything, length difference of 3.
    3
    >>> furry_fixes('roses', 'arose', big_limit)  # Substitute: r -> a, o -> r, s -> o, e -> s, s -> e
    5
    >>> furry_fixes('rose', 'hello', big_limit)  # Substitute: r->h, o->e, s->l, e->l, length difference of 1.
    5
    """
    # BEGIN PROBLEM 6
    '*** YOUR CODE HERE ***'
    if not typed or not source:
        return len(typed) or len(source)
    if typed[0] == source[0]:
        return furry_fixes(typed[1:], source[1:], limit)
    if limit == 0:
        return 1
    return 1 + furry_fixes(typed[1:], source[1:], limit - 1)
    # END PROBLEM 6


@memo_diff
def minimum_mewtations(typed: str, source: str, limit: int) -> int:
    """A diff function for autocorrect that computes the edit distance from TYPED to SOURCE.
    This function takes in a string TYPED, a string SOURCE, and a number LIMIT.

    Arguments:
        typed: a starting word
        source: a string representing a desired goal word
        limit: a number representing an upper bound on the number of edits

    >>> big_limit = 10
    >>> minimum_mewtations('cats', 'scat', big_limit)  # cats -> scats -> scat
    2
    >>> minimum_mewtations('purng', 'purring', big_limit)  # purng -> purrng -> purring
    2
    >>> minimum_mewtations('ckiteus', 'kittens', big_limit)  # ckiteus -> kiteus -> kitteus -> kittens
    3
    """
    if not typed or not source:  # Base cases should go here, you may add more base cases as needed.
        # BEGIN
        '*** YOUR CODE HERE ***'
        return len(typed) or len(source)
        # END
    # Recursive cases should go below here
    if typed[0] == source[0]:  # Feel free to remove or add additional cases
        # BEGIN
        '*** YOUR CODE HERE ***'
        return minimum_mewtations(typed[1:], source[1:], limit)
        # END
    else:
        if limit == 0:
            return 1
        add: int = minimum_mewtations(typed, source[1:], limit - 1)
        remove: int = minimum_mewtations(typed[1:], source, limit - 1)
        substitute: int = minimum_mewtations(typed[1:], source[1:], limit - 1)
        # BEGIN
        '*** YOUR CODE HERE ***'
        return 1 + min(add, remove, substitute)
        # END


# Ignore the line below


def final_diff(typed: str, source: str, limit: int):
    """A diff function that takes in a string TYPED, a string SOURCE, and a number LIMIT.
    If you implement this function, it will be used."""
    assert 1 == 0, 'Remove this line to use your final_diff function.'


FINAL_DIFF_LIMIT = 60  # REPLACE THIS WITH YOUR LIMIT


###########
# Phase 3 #
###########


def report_progress(
    typed: list[str],
    source: list[str],
    user_id: int,
    upload: Callable[[dict[str, int | float]], None],
) -> float:
    """Upload a report of your id and progress so far to the multiplayer server.
    Returns the progress so far.

    Arguments:
        typed: a list of the words typed so far
        source: a list of the words in the typing source
        user_id: a number representing the id of the current user
        upload: a function used to upload progress to the multiplayer server

    >>> print_progress = lambda d: print('ID:', d['id'], 'Progress:', d['progress'])
    >>> # The above function displays progress in the format ID: __, Progress: __
    >>> print_progress({'id': 1, 'progress': 0.6})
    ID: 1 Progress: 0.6
    >>> typed = ['how', 'are', 'you']
    >>> source = ['how', 'are', 'you', 'doing', 'today']
    >>> report_progress(typed, source, 2, print_progress)
    ID: 2 Progress: 0.6
    0.6
    >>> report_progress(['how', 'aree'], source, 3, print_progress)
    ID: 3 Progress: 0.2
    0.2
    """
    # BEGIN PROBLEM 8
    '*** YOUR CODE HERE ***'
    counts: int = 0
    for t, s in zip(typed, source):
        if t == s:
            counts += 1
        else:
            break
    progress: float = counts / len(source)
    upload({'id': user_id, 'progress': progress})
    return progress
    # END PROBLEM 8


def time_per_word(
    words: list[str],
    timestamps_per_player: list[list[int]],
) -> dict[str, list[Any]]:
    """Return a dictionary {'words': words, 'times': times} where times
    is a list of lists that stores the durations it took each player to type
    each word in words.

    Arguments:
        words: a list of words, in the order they are typed.
        timestamps_per_player: A list of lists of timestamps including the time
                          the player started typing, followed by the time the
                          player finished typing each word.

    >>> p = [[75, 81, 84, 90, 92], [19, 29, 35, 36, 38]]
    >>> result = time_per_word(['collar', 'plush', 'blush', 'repute'], p)
    >>> result['words']
    ['collar', 'plush', 'blush', 'repute']
    >>> result['times']
    [[6, 3, 6, 2], [10, 6, 1, 2]]
    """
    # BEGIN PROBLEM 9
    '*** YOUR CODE HERE ***'
    times: list[list[int]] = [[t1 - t0 for t0, t1 in pairwise(timestamps)] for timestamps in timestamps_per_player]
    # END PROBLEM 9
    return {'words': words, 'times': times}


def fastest_words(words_and_times: dict[str, list[Any]]) -> list[list[str]]:
    """Return a list of lists indicating which words each player typed fastests.

    Arguments:
        words_and_times: a dictionary {'words': words, 'times': times} where
        words is a list of the words typed and times is a list of lists of times
        spent by each player typing each word.

    >>> p0 = [5, 1, 3]
    >>> p1 = [4, 1, 6]
    >>> fastest_words({'words': ['Just', 'have', 'fun'], 'times': [p0, p1]})
    [['have', 'fun'], ['Just']]
    >>> p0  # input lists should not be mutated
    [5, 1, 3]
    >>> p1
    [4, 1, 6]
    """
    check_words_and_times(words_and_times)  # verify that the input is properly formed
    words: list[str] = words_and_times['words']
    times: list[list[int]] = words_and_times['times']
    player_indices = range(len(times))  # contains an *index* for each player
    word_indices = range(len(words))  # contains an *index* for each word
    # BEGIN PROBLEM 10
    '*** YOUR CODE HERE ***'
    fastest: list[list[str]] = [[] for _ in player_indices]
    for i, word in enumerate(words):
        fastest_player: int = min(player_indices, key=lambda p: times[p][i])
        fastest[fastest_player].append(word)
    return fastest
    # END PROBLEM 10


def check_words_and_times(words_and_times: dict[str, list[Any]]) -> None:
    """Check that words_and_times is a {'words': words, 'times': times} dictionary
    in which each element of times is a list of numbers the same length as words.
    """
    assert 'words' in words_and_times and 'times' in words_and_times and len(words_and_times) == 2
    words: list[str] = words_and_times['words']
    times: list[list[int]] = words_and_times['times']
    assert all(type(w) == str for w in words), 'words should be a list of strings'
    assert all(type(t) == list for t in times), 'times should be a list of lists'
    assert all(isinstance(i, (int, float)) for t in times for i in t), 'times lists should contain numbers'
    assert all(len(t) == len(words) for t in times), 'There should be one word per time.'


def get_time(
    times: list[list[int]],
    player_num: int,
    word_index: int,
) -> int:
    """Return the time it took player_num to type the word at word_index,
    given a list of lists of times returned by time_per_word."""
    num_players: int = len(times)
    num_words: int = len(times[0])
    assert word_index < len(times[0]), f'word_index {word_index} outside of 0 to {num_words - 1}'
    assert player_num < len(times), f'player_num {player_num} outside of 0 to {num_players - 1}'
    return times[player_num][word_index]


enable_multiplayer = False  # Change to True when you're ready to race.

##########################
# Command Line Interface #
##########################


def run_typing_test(topics):
    """Measure typing speed and accuracy on the command line."""
    paragraphs = lines_from_file('data/sample_paragraphs.txt')
    random.shuffle(paragraphs)
    select = lambda p: True
    if topics:
        select = about(topics)
    i = 0
    while True:
        source = pick(paragraphs, select, i)
        if not source:
            print('No more paragraphs about', topics, 'are available.')
            return
        print('Type the following paragraph and then press enter/return.')
        print('If you only type part of it, you will be scored only on that part.\n')
        print(source)
        print()

        start = datetime.now()
        typed = input()
        if not typed:
            print('Goodbye.')
            return
        print()

        elapsed = (datetime.now() - start).total_seconds()
        print('Nice work!')
        print('Words per minute:', wpm(typed, elapsed))
        print('Accuracy:        ', accuracy(typed, source))

        print('\nPress enter/return for the next paragraph or type q to quit.')
        if input().strip() == 'q':
            return
        i += 1


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions."""
    import argparse

    parser = argparse.ArgumentParser(description='Typing Test')
    parser.add_argument('topic', help='Topic word', nargs='*')
    parser.add_argument('-t', help='Run typing test', action='store_true')

    args = parser.parse_args()
    if args.t:
        run_typing_test(args.topic)
