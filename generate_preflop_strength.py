import random
import json
from hand_evaluator import eval7, DECK, LOOKUP, RANK_NAMES, SUIT_NAMES

def to_card_name(rank: str, suit: str) -> str:
    """Converts short card notation to the full 'rank_of_suit' format.

    This function takes a rank and suit in shorthand (e.g., 'A' for Ace, 's' for spades)
    and converts it into the full card name format (e.g., 'ace_of_spades').

    Args:
        rank (str): A single character representing the rank (e.g., 'A', 'K', 'Q').
        suit (str): A single character representing the suit (e.g., 's' for spades).

    Returns:
        str: The full card name in the format 'rank_of_suit' (e.g., 'ace_of_spades').
    """
    rank_map = {'2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
                '7': '7', '8': '8', '9': '9', 'T': '10',
                'J': 'jack', 'Q': 'queen', 'K': 'king', 'A': 'ace'}
    suit_map = {'s': 'spades', 'c': 'clubs', 'd': 'diamonds', 'h': 'hearts'}
    return f"{rank_map[rank]}_of_{suit_map[suit]}"

def gen_all_starting_hands() -> list:
    """Generates all canonical 169 preflop hand combinations for Texas Hold'em.

    This function generates all the possible preflop hands (both suited and offsuit)
    based on the 13 ranks and suits of the deck. The resulting hands are sorted alphabetically.

    Returns:
        list: A sorted list of all possible starting hand combinations (169 total),
              represented as strings (e.g., 'AsKd', '9s8o', etc.).
    """
    ranks = 'AKQJT98765432'  # List of ranks ordered from Ace to 2
    starting_hands = set()

    for i in range(len(ranks)):
        for j in range(i, len(ranks)):  # Ensure the order of cards doesn't repeat
            if i == j:
                starting_hands.add(ranks[i] + ranks[j])  # Pair hands (e.g., 'AA')
            else:
                starting_hands.add(ranks[i] + ranks[j] + 's')  # Suited hands (e.g., 'AsKs')
                starting_hands.add(ranks[i] + ranks[j] + 'o')  # Offsuit hands (e.g., 'AsKd')

    return sorted(starting_hands)

def create_hand_from_string(hand_str: str) -> list:
    """Generates actual two-card combinations from a starting hand string.

    Given a string representation of a starting hand (e.g., 'AsKd', '9s8o'),
    this function generates all possible 2-card combinations, ensuring that
    suits and ranks match the required hand type (suited or offsuit).

    Args:
        hand_str (str): A string representing the hand type (e.g., 'AsKs', '9s8o').

    Returns:
        list: A list of 2-card combinations represented as strings (e.g., ['ace_of_spades', 'king_of_spades']).
    """
    ranks = hand_str[:2]
    suited = hand_str[2:] == 's'
    offsuit = hand_str[2:] == 'o'
    hands = []

    suits = 'cdhs'  # The four suits: clubs, diamonds, hearts, spades
    for s1 in suits:
        for s2 in suits:
            if s1 == s2 and not suited:  # Skip suited hands if not needed
                continue
            if s1 != s2 and suited:  # Skip offsuit hands if suited is required
                continue
            if s1 == s2 and ranks[0] == ranks[1]:  # Skip duplicate pairs
                continue
            card1 = to_card_name(ranks[0], s1)
            card2 = to_card_name(ranks[1], s2)
            if card1 != card2:  # Avoid adding identical cards
                hands.append([card1, card2])
    return hands

def simulate_equity(hand_str: str, num_trials: int = 10000) -> float:
    """Simulates equity for a given starting hand against random opponents.

    This function simulates a set number of poker hands (default 10,000 trials),
    computes the win/loss/tie statistics for the hand, and returns the equity as the
    ratio of wins and ties.

    Args:
        hand_str (str): The string representation of the hand (e.g., 'AsKd').
        num_trials (int): The number of simulation trials to run (default 10000).

    Returns:
        float: The equity of the hand, calculated as the fraction of wins and ties
               over the total number of trials.
    """
    hero_hands = create_hand_from_string(hand_str)
    total_equity = 0

    # For each hand combination, simulate multiple trials
    for hero in hero_hands:
        wins, ties = 0, 0
        for _ in range(num_trials // len(hero_hands)):
            deck = DECK.copy()
            deck = [c for c in deck if c not in hero]  # Remove the hero's cards from the deck
            random.shuffle(deck)
            opp = deck[:2]  # The opponent's two cards
            board = deck[2:7]  # The community cards (5 cards in total)

            h1_score = eval7(hero + board)  # Evaluate hero's hand
            h2_score = eval7(opp + board)  # Evaluate opponent's hand

            if h1_score < h2_score:  # Hero wins
                wins += 1
            elif h1_score == h2_score:  # Tie
                ties += 1
            # else: loss (not needed for equity calculation)

        equity = (wins + ties / 2) / (num_trials // len(hero_hands))
        total_equity += equity

    return total_equity / len(hero_hands)

def main():
    """Main driver function for simulating and saving preflop hand strengths.

    This function generates all possible preflop hands, simulates the equity for
    each hand type, and saves the results as a JSON file (preflop_strength.json).
    """
    hands = gen_all_starting_hands()  # Generate all starting hands
    table = {}

    # Simulate the equity for each hand type and store the results
    for i, hand in enumerate(hands):
        print(f"[{i+1:3}/{len(hands)}] Simulating {hand}...")
        table[hand] = round(simulate_equity(hand, num_trials=50000), 4)

    # Save the results to a JSON file
    with open("preflop_strength.json", "w") as f:
        json.dump(table, f, indent=2)

    print("Saved preflop strengths to preflop_strength.json")

if __name__ == "__main__":
    main()
