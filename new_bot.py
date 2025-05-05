import numpy as np
import random
import json
import os
from hand_evaluator import eval5, eval6, eval7
import itertools

# Load preflop hand strengths
with open("preflop_strength.json") as f:
    PREFLOP_LOOKUP = json.load(f)

def canonicalize(hand):
    # Returns a standardized string for preflop lookup
    ranks = sorted([card.split("_")[0] for card in hand], key=lambda r: "23456789tjqka".index(r[0].lower()))
    suits = [card.split("_of_")[1] for card in hand]
    suited = suits[0] == suits[1]
    key = ranks[1][0].upper() + ranks[0][0].upper()
    if suited:
        key += "s"
    return key

def get_hand_rank(hand, community):
    if len(community) == 0:
        key = canonicalize(hand)
        return PREFLOP_LOOKUP.get(key, 0.5) * 7462  # normalize to match postflop scale
    full = hand + community
    if len(full) == 5:
        return eval5(full)
    elif len(full) == 6:
        return eval6(full)
    else:
        return eval7(full)

def bot_bet_handling(self):
    self.chips[self.players[1]] -= self.bot_bet - self.previous_bot_bet
    self.previous_bot_bet = self.bot_bet

class QBot:
    def __init__(self, num_buckets=20, save_path="q_table.npy"):
        self.num_buckets = num_buckets
        self.num_states = 4 * num_buckets * 4  # street × bucket × betting_state
        self.Q = np.random.rand(self.num_states, 3)  # Random init
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
        self.trajectory = []
        self.save_path = save_path
        self.load_q_table()

    def load_q_table(self):
        if os.path.exists(self.save_path):
            self.Q = np.load(self.save_path)

    def save_q_table(self):
        np.save(self.save_path, self.Q)

    def encode_state(self, street, rank, betting_state):
        bucket = self.get_bucket(rank)
        return street * self.num_buckets * 4 + bucket * 4 + betting_state

    def get_bucket(self, rank):
        return min(int((rank / 7462) * self.num_buckets), self.num_buckets - 1)

    def get_valid_actions(self, betting_state, raise_cap_reached=False):
        if betting_state == 0:
            return [1, 2]
        elif betting_state == 1:
            return [1, 2]
        elif betting_state == 2:
            return []
        elif betting_state == 3:
            return [0, 1] if raise_cap_reached else [0, 1, 2]

    def choose_action(self, state, valid_actions):
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        q_values = self.Q[state]
        masked = [q if i in valid_actions else -np.inf for i, q in enumerate(q_values)]
        return int(np.argmax(masked))

    def record(self, state, action):
        self.trajectory.append((state, action))

    def update(self, final_reward):
        for t, (state, action) in enumerate(reversed(self.trajectory)):
            discounted = final_reward * (self.gamma ** t)
            self.Q[state][action] += self.alpha * (discounted - self.Q[state][action])
        self.trajectory.clear()
        self.save_q_table()

def bot_action(self):
    street_map = {"preflop": 0, "flop": 1, "turn": 2, "river": 3}
    street = street_map[self.stage]

    rank = get_hand_rank(self.bot_hand, self.community_cards)

    # Determine betting state
    if self.bot_bet == 0 and self.player_bet == 0:
        betting_state = 0
    elif self.bot_bet == 0 and self.player_bet > 0:
        betting_state = 3
    elif self.bot_bet > 0 and self.player_bet == 0:
        betting_state = 1
    else:
        betting_state = 2  # both have called

    state = self.bot.encode_state(street, rank, betting_state)
    valid = self.bot.get_valid_actions(betting_state)
    if not valid:
        return 0

    action = self.bot.choose_action(state, valid)
    self.bot.record(state, action)

    if action == 0:
        print("Bot folds")
        return self.players[0]
    elif action == 1:
        print("Bot checks/calls")
        self.bot_bet = self.player_bet
        self.current_bet = self.player_bet
        bot_bet_handling(self)
        return self.current_bet
    elif action == 2:
        raise_amount = 20
        self.bot_bet = self.player_bet + raise_amount
        self.current_bet = self.bot_bet
        print(f"Bot raises to {self.bot_bet}")
        bot_bet_handling(self)
        return self.current_bet
