from hand_evaluator_data import *
import itertools
import random

_SUITS = [1 << (i + 12) for i in range(4)]
_RANKS = [(1 << (i + 16)) | (i << 8) for i in range(13)]
_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
RANK_NAMES = [
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "jack",
    "queen",
    "king",
    "ace",
]
SUIT_NAMES = ["spades", "clubs", "diamonds", "hearts"]

# Build full deck names like 'ace_of_diamonds'
DECK = [
    f"{RANK_NAMES[rank]}_of_{SUIT_NAMES[suit]}"
    for rank, suit in itertools.product(range(13), range(4))
]

# Build the encoded _DECK as before
_DECK = [
    _RANKS[rank] | _SUITS[suit] | _PRIMES[rank]
    for rank, suit in itertools.product(range(13), range(4))
]
LOOKUP = dict(zip(DECK, _DECK))  # Ensure mapping is correct

LOOKUP = dict(zip(DECK, _DECK))


def hash_function(x):
    x += 0xE91AAA35
    x ^= x >> 16
    x += x << 8
    x &= 0xFFFFFFFF
    x ^= x >> 4
    b = (x >> 8) & 0x1FF
    a = (x + (x << 2)) >> 19
    r = (a ^ HASH_ADJUST[b]) & 0x1FFF
    return HASH_VALUES[r]


def eval5(hand):
    c1, c2, c3, c4, c5 = (LOOKUP[x] for x in hand)
    q = (c1 | c2 | c3 | c4 | c5) >> 16
    if 0xF000 & c1 & c2 & c3 & c4 & c5:
        return FLUSHES[q]
    s = UNIQUE_5[q]
    if s:
        return s
    p = (c1 & 0xFF) * (c2 & 0xFF) * (c3 & 0xFF) * (c4 & 0xFF) * (c5 & 0xFF)
    return hash_function(p)


def eval6(hand):
    return min(eval5(combo) for combo in itertools.combinations(hand, 5))

def eval7(hand):
    return min(eval5(x) for x in itertools.combinations(hand, 5))


def one_round5():
    # shuffle a deck
    deck = list(DECK)
    random.shuffle(deck)
    # draw two hands
    hand1 = deck[:5]
    hand2 = deck[5:10]
    # evaluate the hands
    score1 = eval5(hand1)
    score2 = eval5(hand2)
    # display the winning hand
    hand1 = "[%s]" % " ".join(hand1)
    hand2 = "[%s]" % " ".join(hand2)
    if score1 < score2:
        print(f"{hand1} beats {hand2}")
    elif score1 == score2:
        print(f"{hand1} ties {hand2}")
    else:
        print(f"{hand2} beats {hand1}")
    print()


def one_round7():
    # shuffle a deck
    deck = list(DECK)
    random.shuffle(deck)
    # draw community and two hands
    community = deck[:5]
    hand1 = deck[5:7]
    hand2 = deck[7:9]
    # evaluate the hands
    score1 = eval7(community + hand1)
    score2 = eval7(community + hand2)
    # display the winning hand
    community = "[%s]" % " ".join(community)
    hand1 = "[%s]" % " ".join(hand1)
    hand2 = "[%s]" % " ".join(hand2)
    print(community)
    if score1 < score2:
        print(f"{hand1} beats {hand2}")
    elif score1 == score2:
        print(f"{hand1} ties {hand2}")
    else:
        print(f"{hand2} beats {hand1}")
    print()


if __name__ == "__main__":
    for _ in range(100):
        one_round7()
