import numpy as np
import random

def bot_bet_handling(self):
        self.chips[self.players[1]] -= self.bot_bet - self.previous_bot_bet
        self.previous_bot_bet = self.bot_bet

class QBot:
    def __init__(self, num_buckets=20):
        self.num_buckets = num_buckets
        self.num_states = 4 * num_buckets * 4  # street × bucket × betting_state
        self.Q = np.zeros((self.num_states, 3))  # fold, call/check, raise
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
        self.trajectory = []
        self.starting_chips = None

    def encode_state(self, street, rank, betting_state):
        bucket = self.get_bucket(rank)
        return street * self.num_buckets * 4 + bucket * 4 + betting_state

    def get_bucket(self, rank):
        # You can customize this based on your evaluator
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

def bot_action(self):
    street_map = {"Pre-Flop": 0, "Flop": 1, "Turn": 2, "River": 3}
    street = street_map[self.stage]

    # Get rank from your evaluator
    rank = your_rank_eval_function(self.bot_hand, self.community_cards)

    # Determine betting state
    if self.bot_bet == 0 and self.player_bet == 0:
        betting_state = 0
    elif self.bot_bet == 0 and self.player_bet > 0:
        betting_state = 3
    elif self.bot_bet > 0 and self.player_bet == 0:
        betting_state = 1
    else:
        betting_state = 2  # both have called

    state = QBot.encode_state(street, rank, betting_state)
    valid = QBot.get_valid_actions(betting_state)
    if not valid:
        return 0  # nothing to do

    action = QBot.choose_action(state, valid)
    QBot.record(state, action)

    # Apply action
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
        raise_amount = 20  # fixed for Limit
        self.bot_bet = self.player_bet + raise_amount
        self.current_bet = self.bot_bet
        print(f"Bot raises to {self.bot_bet}")
        bot_bet_handling(self)
        return self.current_bet
