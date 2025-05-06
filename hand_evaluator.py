"""Hand evaluator for 5-card and 7-card poker hands using a fast Cactus Kev-style algorithm."""

from hand_evaluator_data import *  # Contains precomputed tables: FLUSHES, UNIQUE_5, HASH_VALUES, HASH_ADJUST
import itertools
import random

# Bitmask encoding constants
_SUITS = [1 << (i + 12) for i in range(4)]  # 4 suits: shift by 12–15
_RANKS = [(1 << (i + 16)) | (i << 8) for i in range(13)]  # rank mask + shift rank to bits 8–11
_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]  # Unique primes for hashing

# Human-readable names
RANK_NAMES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
SUIT_NAMES = ["spades", "clubs", "diamonds", "hearts"]

# Full deck with human-readable strings
DECK = [
    f"{RANK_NAMES[rank]}_of_{SUIT_NAMES[suit]}"
    for rank, suit in itertools.product(range(13), range(4))
]

# Encoded deck values using bitwise format and primes
_DECK = [
    _RANKS[rank] | _SUITS[suit] | _PRIMES[rank]
    for rank, suit in itertools.product(range(13), range(4))
]

# Lookup table mapping string card name to encoded integer
LOOKUP = dict(zip(DECK, _DECK))


def hash_function(x: int) -> int:
    """Performs a custom hashing routine used for detecting hand types.

    Args:
        x (int): Product of primes from 5 cards.

    Returns:
        int: Precomputed value from HASH_VALUES indicating hand strength.
    """
    x += 0xE91AAA35
    x ^= x >> 16
    x += x << 8
    x &= 0xFFFFFFFF  # Ensure 32-bit integer
    x ^= x >> 4
    b = (x >> 8) & 0x1FF
    a = (x + (x << 2)) >> 19
    r = (a ^ HASH_ADJUST[b]) & 0x1FFF
    return HASH_VALUES[r]


def eval5(hand: list[str]) -> int:
    """Evaluates a 5-card poker hand and returns a numerical score (lower is better).

    Args:
        hand (list[str]): List of 5 string card names (e.g., "ace_of_spades").

    Returns:
        int: Hand strength value (smaller is stronger).
    """
    c1, c2, c3, c4, c5 = (LOOKUP[x] for x in hand)
    q = (c1 | c2 | c3 | c4 | c5) >> 16
    # Check for flush using suit bits
    if 0xF000 & c1 & c2 & c3 & c4 & c5:
        return FLUSHES[q]
    # Check for unique non-flush hands
    s = UNIQUE_5[q]
    if s:
        return s
    # Use product of primes to hash into hash table
    p = (c1 & 0xFF) * (c2 & 0xFF) * (c3 & 0xFF) * (c4 & 0xFF) * (c5 & 0xFF)
    return hash_function(p)


def eval6(hand: list[str]) -> int:
    """Evaluates the best 5-card hand out of 6 cards.

    Args:
        hand (list[str]): List of 6 string card names.

    Returns:
        int: Best 5-card hand strength among combinations.
    """
    return min(eval5(combo) for combo in itertools.combinations(hand, 5))


def eval7(hand: list[str]) -> int:
    """Evaluates the best 5-card hand out of 7 cards.

    Args:
        hand (list[str]): List of 7 string card names.

    Returns:
        int: Best 5-card hand strength among combinations.
    """
    return min(eval5(combo) for combo in itertools.combinations(hand, 5))


def one_round5() -> None:
    """Simulates one round of heads-up 5-card poker and prints the winner."""
    deck = list(DECK)
    random.shuffle(deck)
    hand1 = deck[:5]
    hand2 = deck[5:10]
    score1 = eval5(hand1)
    score2 = eval5(hand2)
    hand1_str = "[%s]" % " ".join(hand1)
    hand2_str = "[%s]" % " ".join(hand2)
    if score1 < score2:
        print(f"{hand1_str} beats {hand2_str}")
    elif score1 == score2:
        print(f"{hand1_str} ties {hand2_str}")
    else:
        print(f"{hand2_str} beats {hand1_str}")
    print()


def one_round7() -> None:
    """Simulates one round of Texas Hold'em with 5 community cards and two 2-card hands."""
    deck = list(DECK)
    random.shuffle(deck)
    community = deck[:5]
    hand1 = deck[5:7]
    hand2 = deck[7:9]
    score1 = eval7(community + hand1)
    score2 = eval7(community + hand2)
    community_str = "[%s]" % " ".join(community)
    hand1_str = "[%s]" % " ".join(hand1)
    hand2_str = "[%s]" % " ".join(hand2)
    print(community_str)
    if score1 < score2:
        print(f"{hand1_str} beats {hand2_str}")
    elif score1 == score2:
        print(f"{hand1_str} ties {hand2_str}")
    else:
        print(f"{hand2_str} beats {hand1_str}")
    print()


if __name__ == "__main__":
    for _ in range(100):
        one_round7()
