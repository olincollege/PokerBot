"""Hand evaluator for 5-card and 7-card poker hands using a fast Cactus Kev-style algorithm."""

import itertools
import random
from hand_evaluator_data import FLUSHES, UNIQUE_5, HASH_VALUES, HASH_ADJUST


# Bitmask encoding constants
_SUITS = [1 << (i + 12) for i in range(4)]  # 4 suits: shift by 12–15
_RANKS = [
    (1 << (i + 16)) | (i << 8) for i in range(13)
]  # rank mask + shift rank to bits 8–11
_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]  # Unique primes for hashing

# Human-readable names
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


def hash_function(x_num: int) -> int:
    """Performs a custom hashing routine used for detecting hand types.

    Args:
        x_num (int): Product of primes from 5 cards.

    Returns:
        int: Precomputed value from HASH_VALUES indicating hand strength.
    """
    x_num += 0xE91AAA35
    x_num ^= x_num >> 16
    x_num += x_num << 8
    x_num &= 0xFFFFFFFF  # Ensure 32-bit integer
    x_num ^= x_num >> 4
    b_num = (x_num >> 8) & 0x1FF
    a_num = (x_num + (x_num << 2)) >> 19
    r_num = (a_num ^ HASH_ADJUST[b_num]) & 0x1FFF
    return HASH_VALUES[r_num]


def eval5(hand: list[str]) -> int:
    """Evaluates a 5-card poker hand and returns a numerical score (lower is better).

    Args:
        hand (list[str]): List of 5 string card names (e.g., "ace_of_spades").

    Returns:
        int: Hand strength value (smaller is stronger).
    """
    card_1, card_2, card_3, card_4, card_5 = (LOOKUP[x_num] for x_num in hand)
    q_num = (card_1 | card_2 | card_3 | card_4 | card_5) >> 16
    # Check for flush using suit bits
    if 0xF000 & card_1 & card_2 & card_3 & card_4 & card_5:
        return FLUSHES[q_num]
    # Check for unique non-flush hands
    s_num = UNIQUE_5[q_num]
    if s_num:
        return s_num
    # Use product of primes to hash into hash table
    p_num = (
        (card_1 & 0xFF)
        * (card_2 & 0xFF)
        * (card_3 & 0xFF)
        * (card_4 & 0xFF)
        * (card_5 & 0xFF)
    )
    return hash_function(p_num)


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
    hand1_str = f"[{' '.join(hand1)}]"
    hand2_str = f"[{' '.join(hand2)}]"
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
    community_str = f"[{' '.join(community)}]"
    hand1_str = f"[{' '.join(hand1)}]"
    hand2_str = f"[{' '.join(hand2)}]"
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
