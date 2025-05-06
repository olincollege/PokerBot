import random
import json
from hand_evaluator import eval7, DECK, LOOKUP, RANK_NAMES, SUIT_NAMES


# Map short rank/suit notation (e.g., 'As') to your format (e.g., 'ace_of_spades')
def to_card_name(rank, suit):
    rank_map = {
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "T": "10",
        "J": "jack",
        "Q": "queen",
        "K": "king",
        "A": "ace",
    }
    suit_map = {"s": "spades", "c": "clubs", "d": "diamonds", "h": "hearts"}
    return f"{rank_map[rank]}_of_{suit_map[suit]}"


# Generate canonical 169 preflop hands
def gen_all_starting_hands():
    ranks = "AKQJT98765432"
    starting_hands = set()

    for i in range(len(ranks)):
        for j in range(i, len(ranks)):
            if i == j:
                starting_hands.add(ranks[i] + ranks[j])  # e.g., 'AA'
            else:
                starting_hands.add(ranks[i] + ranks[j] + "s")
                starting_hands.add(ranks[i] + ranks[j] + "o")
    return sorted(starting_hands)


# Generate actual two-card combinations for a given hand type
def create_hand_from_string(hand_str):
    ranks = hand_str[:2]
    suited = hand_str[2:] == "s"
    offsuit = hand_str[2:] == "o"
    hands = []

    suits = "cdhs"
    for s1 in suits:
        for s2 in suits:
            if s1 == s2 and not suited:
                continue
            if s1 != s2 and suited:
                continue
            if s1 == s2 and ranks[0] == ranks[1]:
                continue  # skip duplicates
            card1 = to_card_name(ranks[0], s1)
            card2 = to_card_name(ranks[1], s2)
            if card1 != card2:
                hands.append([card1, card2])
    return hands


def simulate_equity(hand_str, num_trials=10000):
    hero_hands = create_hand_from_string(hand_str)
    total_equity = 0

    for hero in hero_hands:
        wins, ties = 0, 0
        for _ in range(num_trials // len(hero_hands)):
            deck = DECK.copy()
            deck = [c for c in deck if c not in hero]
            random.shuffle(deck)
            opp = deck[:2]
            board = deck[2:7]

            h1_score = eval7(hero + board)
            h2_score = eval7(opp + board)

            if h1_score < h2_score:
                wins += 1
            elif h1_score == h2_score:
                ties += 1
            # else: loss

        equity = (wins + ties / 2) / (num_trials // len(hero_hands))
        total_equity += equity

    return total_equity / len(hero_hands)


def main():
    hands = gen_all_starting_hands()
    table = {}

    for i, hand in enumerate(hands):
        print(f"[{i+1:3}/{len(hands)}] Simulating {hand}...")
        table[hand] = round(simulate_equity(hand, num_trials=5000), 4)

    with open("preflop_strength.json", "w") as f:
        json.dump(table, f, indent=2)

    print("Saved preflop strengths to preflop_strength.json")


if __name__ == "__main__":
    main()
