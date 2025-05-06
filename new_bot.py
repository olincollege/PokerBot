import numpy as np
import random
import json
import os
import logging
from hand_evaluator import eval5, eval6, eval7
from view import PokerView

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="poker_bot.log",
    filemode="a",
)
logger = logging.getLogger("poker_bot")


# Load preflop hand strengths
def load_preflop_data():
    try:
        with open("preflop_strength.json") as f:
            data = json.load(f)
            logger.info(f"Loaded preflop data with {len(data)} hand combinations")
            return data
    except FileNotFoundError:
        logger.warning("preflop_strength.json not found. Using default values.")
        print("Warning: preflop_strength.json not found. Using default values.")
        # Return a small default dictionary with some common hand values
        return {
            "AA": 1.0,
            "KK": 0.95,
            "QQ": 0.9,
            "JJ": 0.85,
            "TT": 0.8,
            "AKs": 0.82,
            "AQs": 0.78,
            "AJs": 0.75,
            "AKo": 0.75,
            "22": 0.5,
            "32o": 0.2,
        }


PREFLOP_LOOKUP = load_preflop_data()


def canonicalize(hand):
    # Returns a standardized string for preflop lookup
    # Handle cards in format like "10_of_hearts" or "ace_of_spades"
    rank_map = {
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "10": "t",
        "jack": "j",
        "queen": "q",
        "king": "k",
        "ace": "a",
    }

    # Extract ranks and suits
    card_parts = [card.split("_of_") for card in hand]
    ranks = [part[0] for part in card_parts]
    suits = [part[1] for part in card_parts]

    # Map ranks to single-character representation
    mapped_ranks = [rank_map.get(rank, "x") for rank in ranks]

    # Sort ranks
    sorted_ranks = sorted(mapped_ranks, key=lambda r: "23456789tjqka".index(r))

    # Check if suited
    suited = suits[0] == suits[1]

    # Create key in format like "AKs" or "QJ"
    key = sorted_ranks[1].upper() + sorted_ranks[0].upper()
    if suited:
        key += "s"

    return key


def get_hand_rank(hand, community):
    try:
        if len(community) == 0:
            key = canonicalize(hand)
            return (
                PREFLOP_LOOKUP.get(key, 0.5) * 7462
            )  # normalize to match postflop scale

        full = hand + community
        if len(full) == 5:
            return eval5(full)
        elif len(full) == 6:
            return eval6(full)
        else:
            return eval7(full)
    except Exception as e:
        print(f"Error in get_hand_rank: {e}")
        print(f"Hand: {hand}")
        print(f"Community: {community}")
        # Fallback to a default value
        return 0.5 * 7462


def bot_bet_handling(self):
    self.chips[self.players[1]] -= self.bot_bet - self.previous_bot_bet
    self.previous_bot_bet = self.bot_bet


class QBot:
    def __init__(self, num_buckets=20, save_path="q_strategy.json"):
        self.num_buckets = num_buckets
        self.num_states = 4 * num_buckets * 4  # street × bucket × betting_state
        self.Q = np.zeros((self.num_states, 3))  # Initialize with zeros
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.epsilon = 0.1  # Exploration rate
        self.trajectory = []
        self.save_path = save_path
        self.load_strategy()
        self.games_played = 0

    def load_strategy(self):
        """Load Q-table from JSON file"""
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r") as f:
                    data = json.load(f)
                    self.Q = np.array(data["q_table"])
                    self.games_played = data.get("games_played", 0)
                    print(
                        f"Strategy loaded from {self.save_path}. Games played: {self.games_played}"
                    )
            except Exception as e:
                print(f"Error loading strategy: {e}. Using default values.")
                # Initialize with slightly random values to avoid ties
                self.Q = np.random.rand(self.num_states, 3) * 0.1

    def save_strategy(self):
        """Save Q-table to JSON file"""
        data = {"q_table": self.Q.tolist(), "games_played": self.games_played + 1}

        try:
            with open(self.save_path, "w") as f:
                json.dump(data, f)
            print(f"Strategy saved to {self.save_path}")
        except Exception as e:
            print(f"Error saving strategy: {e}")

    def encode_state(self, street, rank, betting_state):
        bucket = self.get_bucket(rank)
        return street * self.num_buckets * 4 + bucket * 4 + betting_state

    def get_bucket(self, rank):
        return min(int((rank / 7462) * self.num_buckets), self.num_buckets - 1)

    def get_valid_actions(self, betting_state, raise_cap_reached=False):
        if betting_state == 0:  # No bets yet
            return [1, 2]  # Check (1) or Raise (2)
        elif betting_state == 1:  # Bot has bet, player hasn't
            return [1, 2]  # Check (1) or Raise (2)
        elif betting_state == 2:  # Both have bet same amount
            return [1]  # Check/Call (1)
        elif betting_state == 3:  # Player has bet, bot hasn't matched
            return (
                [0, 1] if raise_cap_reached else [0, 1, 2]
            )  # Fold (0), Call (1), or Raise (2)

    def choose_action(self, state, valid_actions):
        # Decrease epsilon over time to reduce exploration
        effective_epsilon = max(0.01, self.epsilon * (1 - self.games_played / 1000))

        if random.random() < effective_epsilon:
            return random.choice(valid_actions)

        q_values = self.Q[state]
        masked = [q if i in valid_actions else -np.inf for i, q in enumerate(q_values)]
        return int(np.argmax(masked))

    def record(self, state, action):
        self.trajectory.append((state, action))

    def update(self, final_reward):
        for t, (state, action) in enumerate(reversed(self.trajectory)):
            discounted = final_reward * (self.gamma**t)
            self.Q[state][action] += self.alpha * (discounted - self.Q[state][action])
        self.trajectory.clear()
        self.games_played += 1
        self.save_strategy()


def bot_action(self):
    """Bot's action during the betting round"""
    # Debug print for stage
    print(f"Current stage: {self.stage}")

    # Handle case sensitivity and variations in stage names
    stage_lower = self.stage.lower() if hasattr(self.stage, "lower") else "preflop"

    # Map the stage to numeric values
    if "pre" in stage_lower:
        street = 0  # Preflop
        round = "preflop"
    elif "flop" in stage_lower:
        street = 1  # Flop
        round = "flop"
    elif "turn" in stage_lower:
        street = 2  # Turn
        round = "turn"
    elif "river" in stage_lower:
        street = 3  # River
        round = "river"
    else:
        street = 0  # Default to preflop
        round = "preflop"

    # Debug print for cards
    print(f"Bot hand: {self.bot_hand}")
    print(f"Community cards: {self.community_cards}")

    # Calculate hand rank with error handling
    try:
        rank = get_hand_rank(self.bot_hand, self.community_cards)
    except Exception as e:
        print(f"Error getting hand rank: {e}")
        rank = 0.5 * 7462  # Default to middle rank

    # Determine the current betting state
    if self.bot_bet == 0 and self.player_bet == 0:
        betting_state = 0  # No bets yet
    elif self.bot_bet == 0 and self.player_bet > 0:
        betting_state = 3  # Player has bet, bot hasn't matched
    elif self.bot_bet > 0 and self.player_bet == self.bot_bet:
        betting_state = 2  # Both have bet same amount
    else:
        betting_state = 1  # Bot has bet, player hasn't or hasn't matched

    state = self.bot.encode_state(street, rank, betting_state)
    valid = self.bot.get_valid_actions(
        betting_state, self.raise_count >= self.max_raises_per_round
    )

    if not valid:
        return 0  # Default action if no valid actions (shouldn't happen)

    action = self.bot.choose_action(state, valid)

    self.bot.record(state, action)

    if action == 0:
        PokerView.display_bot_decision(self, "fold", round)
        print("Bot folds")
        return self.players[0]  # Bot folds, player wins
    elif action == 1:
        PokerView.display_bot_decision(self, "check/call", round)
        print("Bot checks/calls")
        self.bot_bet = self.player_bet
        self.current_bet = self.player_bet
        bot_bet_handling(self)
        return self.current_bet
    elif action == 2:
        raise_amount = self.get_current_bet_size()
        PokerView.display_bot_decision(self, "raise", round, raise_amount)
        self.bot_bet = self.player_bet + raise_amount
        self.current_bet = self.bot_bet
        print(f"Bot raises to {self.bot_bet}")
        bot_bet_handling(self)
        self.raise_count += 1
        return self.current_bet
