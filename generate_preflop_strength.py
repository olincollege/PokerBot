"""
Generate preflop hand strength data for poker hands.

This script simulates poker hands and calculates the equity of various starting hands.
It generates a JSON file containing the preflop strength of each hand type.
It uses a Monte Carlo simulation approach to estimate the equity of hands against random opponents.
"""

import random
import json
from hand_evaluator import eval7, DECK


def to_card_name(rank, suit):
    """Convert short rank/suit notation to full card name.

    Args:
        rank (str): A single-character rank, e.g., 'A', 'K', 'T', '2'.
        suit (str): A single-character suit, e.g., 's', 'h', 'd', 'c'.

    Returns:
        str: Full card name, e.g., 'ace_of_spades'.
    """
    rank_map = {
        "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7",
        "8": "8", "9": "9", "T": "10", "J": "jack", "Q": "queen",
        "K": "king", "A": "ace",
    }
    suit_map = {
        "s": "spades", "c": "clubs", "d": "diamonds", "h": "hearts",
    }
    return f"{rank_map[rank]}_of_{suit_map[suit]}"


def gen_all_starting_hands():
    """Generate all 169 canonical preflop hand types (e.g., 'AA', 'AKs', 'AKo').

    Returns:
        list[str]: Sorted list of 169 starting hand strings.
    """
    ranks = "AKQJT98765432"
    starting_hands = set()

    for i, rank_i in enumerate(ranks):
        for j in range(i, len(ranks)):
            if i == j:
                starting_hands.add(rank_i + ranks[j])  # e.g., 'AA'
            else:
                starting_hands.add(rank_i + ranks[j] + "s")
                starting_hands.add(rank_i + ranks[j] + "o")

    return sorted(starting_hands)


def create_hand_from_string(hand_str):
    """Generate all specific two-card combos for a hand type.

    Args:
        hand_str (str): Hand type string, e.g., 'AKs', 'TT', 'JTo'.

    Returns:
        list[list[str]]: List of valid two-card combos, each as [card1, card2].
    """
    ranks = hand_str[:2]
    suited = hand_str[2:] == "s"
    hands = []

    suits = "cdhs"
    for suit1 in suits:
        for suit2 in suits:
            if suit1 == suit2 and not suited:
                continue
            if suit1 != suit2 and suited:
                continue
            if suit1 == suit2 and ranks[0] == ranks[1]:
                continue  # avoid duplicate card

            card1 = to_card_name(ranks[0], suit1)
            card2 = to_card_name(ranks[1], suit2)

            if card1 != card2:
                hands.append([card1, card2])

    return hands


def simulate_equity(hand_str, num_trials=10000):
    """Estimate average preflop equity for a given hand type.

    Uses Monte Carlo simulation against a random opponent.

    Args:
        hand_str (str): Hand type string (e.g., 'AKs').
        num_trials (int): Total number of simulations (default: 10000).

    Returns:
        float: Estimated equity of the hand (between 0 and 1).
    """
    hero_hands = create_hand_from_string(hand_str)
    total_equity = 0

    for hero in hero_hands:
        wins = ties = 0
        trials_per_combo = num_trials // len(hero_hands)

        for _ in range(trials_per_combo):
            deck = [c for c in DECK if c not in hero]
            random.shuffle(deck)

            opp = deck[:2]
            board = deck[2:7]

            h1_score = eval7(hero + board)
            h2_score = eval7(opp + board)

            if h1_score < h2_score:
                wins += 1
            elif h1_score == h2_score:
                ties += 1

        equity = (wins + ties / 2) / trials_per_combo
        total_equity += equity

    return total_equity / len(hero_hands)


def main():
    """Run simulations for all 169 hand types and save results to JSON."""
    hands = gen_all_starting_hands()
    table = {}

    for i, hand in enumerate(hands):
        print(f"[{i+1:3}/{len(hands)}] Simulating {hand}...")
        equity = simulate_equity(hand, num_trials=5000)
        table[hand] = round(equity, 4)

    with open("preflop_strength.json", "w", encoding="utf-8") as output_file:
        json.dump(table, output_file, indent=2)

    print("Saved preflop strengths to preflop_strength.json")


if __name__ == "__main__":
    main()
