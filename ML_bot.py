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
    """
    Load preflop hand strength data from a JSON file.

    Returns:
        dict: A dictionary mapping preflop hand strings (e.g., "AKs", "QQ") to 
              their estimated strength values (floats between 0 and 1). If the 
              file is not found, a default dictionary with common hand strengths 
              is returned instead.

    Logs:
        - Info message if the data is successfully loaded.
        - Warning message and a console print if the file is missing.
    """
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
    """
    Convert a two-card poker hand into a canonical shorthand representation.

    Args:
        hand (list of str): A list of two card strings in the format 
                            "<rank>_of_<suit>", e.g., ["ace_of_spades", "king_of_spades"].

    Returns:
        str: A canonical hand key in shorthand poker notation (e.g., "AKs", "QJo", "22").
             "s" is appended for suited hands (same suit), no suffix for offsuit pairs.

    Notes:
        - Ranks are mapped to standard shorthand: e.g., "10" → "T", "jack" → "J", etc.
        - Hands are ordered so the higher rank comes first.
        - If rank is unrecognized, "x" is used as a placeholder.
    """
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
    """
    Evaluate the strength of a poker hand given the community cards.

    Args:
        hand (list of str): The player's two hole cards (e.g., ["ace_of_spades", "king_of_hearts"]).
        community (list of str): The shared community cards on the table (0 to 5 cards).

    Returns:
        float: A numerical score representing hand strength.
               - For preflop (no community cards), returns a normalized score based on preflop hand strength.
               - For postflop, uses eval5, eval6, or eval7 depending on the number of total cards.

    Notes:
        - Preflop values come from a lookup table and are scaled to match postflop score range.
        - If an exception occurs during evaluation, a default mid-range value is returned.
    """
    try:
        if len(community) == 0:
            key = canonicalize(hand)
            return (1.0 - PREFLOP_LOOKUP.get(key, 0.5)) * 7462  # normalize to match postflop scale
        
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
    """
    Deducts the bot's bet difference from its chip stack and updates the previous bet amount.
    """
    self.chips[self.players[1]] -= self.bot_bet - self.previous_bot_bet
    self.previous_bot_bet = self.bot_bet


class QBot:
    """
    A reinforcement learning bot for Limit Hold'em using Q-learning with function approximation.

    Attributes:
        num_buckets (int): Number of buckets to discretize hand strength.
        num_states (int): Total number of discrete states (street × bucket × betting state).
        Q (np.ndarray): Q-table storing expected values for each (state, action) pair.
        alpha (float): Learning rate for Q-learning.
        gamma (float): Discount factor for future rewards.
        epsilon (float): Exploration rate for epsilon-greedy policy.
        trajectory (list): List of (state, action) pairs recorded during a hand.
        save_path (str): Path to save/load the Q-table.
        games_played (int): Number of games played so far.
    """
    def __init__(self, num_buckets=20, save_path="q_strategy.json"):
        """
        Initialize a new QBot instance.

        Args:
            num_buckets (int): Number of buckets for discretizing hand strength.
            save_path (str): File path to load/save Q-table data.
        """
        self.num_buckets = num_buckets
        self.num_states = 4 * num_buckets * 4  # street × bucket × betting_state
        self.Q = np.zeros((self.num_states, 3))  # Initialize with zeros
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.epsilon = 0.1  # Exploration rate
        self.trajectory = []
        self.save_path = save_path
        self.games_played = 0
        self.load_strategy()

    def load_strategy(self):
        """
        Load the Q-table and number of games played from a JSON file.

        If the file is not found or cannot be parsed, initializes the Q-table
        with small random values to encourage early exploration.
        """
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
        """
        Save the current Q-table and number of games played to a JSON file.

        Increments the games played counter by 1 before saving.
        """
        data = {
            'q_table': self.Q.tolist(),
            'games_played': self.games_played + 1
        }
        
        try:
            with open(self.save_path, "w") as f:
                json.dump(data, f)
            print(f"Strategy saved to {self.save_path}")
        except Exception as e:
            print(f"Error saving strategy: {e}")

    def encode_state(self, street, rank, betting_state):
        """
        Encode the current game state into a single integer index.

        Args:
            street (int): The current betting round (0=preflop, 1=flop, etc.).
            rank (float): Hand strength as an integer between 0 and 7462.
            betting_state (int): A discrete integer encoding the betting situation.

        Returns:
            int: Encoded state index.
        """
        bucket = self.get_bucket(rank)
        return street * self.num_buckets * 4 + bucket * 4 + betting_state

    def get_bucket(self, rank):
        """
        Assign a hand strength rank to a discrete bucket.

        Args:
            rank (float): Hand strength (0 to 7462).

        Returns:
            int: Bucket index (0 to num_buckets - 1).
        """
        return min(int((rank / 7462) * self.num_buckets), self.num_buckets - 1)

    def get_valid_actions(self, betting_state, raise_cap_reached=False):
        """
        Return a list of valid actions based on the current betting state.

        Args:
            betting_state (int): The current betting situation (0-3).
            raise_cap_reached (bool): Whether the raise limit has been reached.

        Returns:
            list[int]: A list of allowed actions [0=Fold, 1=Call/Check, 2=Raise].
        """
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
        """
        Choose an action using an epsilon-greedy policy.

        Args:
            state (int): Encoded state index.
            valid_actions (list[int]): A list of valid actions.

        Returns:
            int: The chosen action index.
        """
        # Decrease epsilon over time to reduce exploration
        effective_epsilon = max(0.01, self.epsilon * (1 - self.games_played / 1000))

        if random.random() < effective_epsilon:
            return random.choice(valid_actions)

        q_values = self.Q[state]
        masked = [q if i in valid_actions else -np.inf for i, q in enumerate(q_values)]
        return int(np.argmax(masked))

    def record(self, state, action):
        """
        Record a state-action pair during the game for later Q-value updates.

        Args:
            state (int): The current state.
            action (int): The chosen action in this state.
        """
        self.trajectory.append((state, action))

    def update(self, final_reward):
        """
        Update Q-values from the recorded trajectory using the final reward.

        Args:
            final_reward (float): The outcome reward of the game (e.g., net chips won).
        """
        for t, (state, action) in enumerate(reversed(self.trajectory)):
            discounted = final_reward * (self.gamma**t)
            self.Q[state][action] += self.alpha * (discounted - self.Q[state][action])
        self.trajectory.clear()
        self.games_played += 1
        self.save_strategy()


def bot_action(self):
    """
    Determines and executes the bot's action during its turn in the betting round.

    The method:
    - Parses the current game stage and encodes it into a numeric 'street' value.
    - Computes the bot's hand strength using the hand and community cards.
    - Determines the current betting state between the player and the bot.
    - Encodes the full game state for the Q-learning agent (QBot).
    - Selects an action using QBot's epsilon-greedy policy.
    - Executes the chosen action (fold, call/check, or raise).
    - Updates internal bet states and returns the outcome.

    Returns:
        int or str: If the bot folds, returns the player ID (indicating a win).
                    Otherwise, returns the new current bet value.
    """
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



# ADDED TRAINING FUNCTIONALITY BELOW THIS LINE

class SelfPlayGame:
    """
    A simplified poker game structure for self-play training.
    
    This class simulates a poker game between two QBot instances, allowing
    the bot to learn through self-play without requiring the full game UI.
    """
    def __init__(self, bot1, bot2, starting_chips=1000, bet_size=20, max_raises=4):
        """
        Initialize a self-play game environment.
        
        Args:
            bot1 (QBot): First bot instance
            bot2 (QBot): Second bot instance
            starting_chips (int): Starting chip stack for each bot
            bet_size (int): Size of standard bet
            max_raises (int): Maximum number of raises allowed per betting round
        """
        self.bot1 = bot1
        self.bot2 = bot2
        self.starting_chips = starting_chips
        self.bet_size = bet_size
        self.max_raises = max_raises
        
        # Initialize game state
        self.reset_game()
        
        # Standard 52-card deck
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        self.suits = ['hearts', 'diamonds', 'clubs', 'spades']
        self.deck = [f"{rank}_of_{suit}" for rank in self.ranks for suit in self.suits]
    
    def reset_game(self):
        """Reset the game state for a new hand."""
        self.chips = {0: self.starting_chips, 1: self.starting_chips}
        self.community_cards = []
        self.pot = 0
        self.hand1 = []
        self.hand2 = []
        self.stage = "preflop"
        self.pot_contributions = {0: 0, 1: 0}
        self.current_bet = 0
        self.active_player = 0  # Player 0 starts
        
    def deal_cards(self):
        """Shuffle the deck and deal cards."""
        random.shuffle(self.deck)
        
        # Deal two cards to each bot
        self.hand1 = [self.deck[0], self.deck[1]]
        self.hand2 = [self.deck[2], self.deck[3]]
        
        # Deal community cards
        self.flop = [self.deck[4], self.deck[5], self.deck[6]]
        self.turn = [self.deck[7]]
        self.river = [self.deck[8]]
        
        # Start with empty community cards
        self.community_cards = []
    
    def advance_stage(self):
        """Move to the next betting round."""
        if self.stage == "preflop":
            self.stage = "flop"
            self.community_cards = self.flop
        elif self.stage == "flop":
            self.stage = "turn"
            self.community_cards = self.flop + self.turn
        elif self.stage == "turn":
            self.stage = "river"
            self.community_cards = self.flop + self.turn + self.river
        else:
            return False  # Hand is over
        return True
    
    def evaluate_winner(self):
        """Determine the winner at showdown."""
        hand1_rank = get_hand_rank(self.hand1, self.community_cards)
        hand2_rank = get_hand_rank(self.hand2, self.community_cards)
        
        if hand1_rank < hand2_rank:  # Lower rank is better in this evaluator
            return 0  # Bot 1 wins
        elif hand2_rank < hand1_rank:
            return 1  # Bot 2 wins
        else:
            return -1  # Split pot
    
    def get_bot_action(self, bot_id, bot, opponent_bet, bot_bet):
        """
        Get action decision from a bot.
        
        Args:
            bot_id (int): 0 for bot1, 1 for bot2
            bot (QBot): The bot making the decision
            opponent_bet (int): Current bet from opponent
            bot_bet (int): Current bet from this bot
            
        Returns:
            tuple: (action, new_bet) where action is 0 (fold), 1 (call), or 2 (raise)
        """
        # Convert stage to street number
        if self.stage == "preflop":
            street = 0
        elif self.stage == "flop":
            street = 1
        elif self.stage == "turn":
            street = 2
        else:  # river
            street = 3
            
        # Get hand for current bot
        hand = self.hand1 if bot_id == 0 else self.hand2
        
        # Calculate hand rank
        rank = get_hand_rank(hand, self.community_cards)
        
        # Determine betting state
        if bot_bet == 0 and opponent_bet == 0:
            betting_state = 0  # No bets yet
        elif bot_bet == 0 and opponent_bet > 0:
            betting_state = 3  # Opponent has bet, bot hasn't matched
        elif bot_bet > 0 and opponent_bet == bot_bet:
            betting_state = 2  # Both have bet same amount
        else:
            betting_state = 1  # Bot has bet, opponent hasn't or hasn't matched
            
        # Encode state and get valid actions
        state = bot.encode_state(street, rank, betting_state)
        raise_cap_reached = (self.pot_contributions[bot_id] - self.pot_contributions[1-bot_id] + self.bet_size) / self.bet_size >= self.max_raises
        valid_actions = bot.get_valid_actions(betting_state, raise_cap_reached)
        
        # Choose action
        action = bot.choose_action(state, valid_actions)
        
        # Record state-action pair
        bot.record(state, action)
        
        # Calculate new bet based on action
        new_bet = bot_bet
        if action == 1:  # Call/Check
            new_bet = opponent_bet
        elif action == 2:  # Raise
            new_bet = opponent_bet + self.bet_size
        
        return action, new_bet
    
    def play_betting_round(self):
        """
        Play a single betting round between the two bots.
        
        Returns:
            int or None: If a bot folds, returns the winner's ID. Otherwise None.
        """
        bot1_bet = 0
        bot2_bet = 0
        round_finished = False
        last_raiser = None
        
        # Keep track of number of raises in this round
        raises_made = 0
        
        # Start with bot1
        active_player = 0
        
        while not round_finished:
            if active_player == 0:
                # Bot 1's turn
                action, new_bet = self.get_bot_action(0, self.bot1, bot2_bet, bot1_bet)
                
                if action == 0:  # Fold
                    return 1  # Bot 2 wins
                    
                # Update bet
                if new_bet > bot1_bet:
                    # This is a raise
                    if raises_made < self.max_raises:
                        raises_made += 1
                        last_raiser = 0
                    else:
                        # Can't raise, must call
                        new_bet = bot2_bet
                
                # Update chips and pot
                bet_diff = new_bet - bot1_bet
                self.chips[0] -= bet_diff
                self.pot += bet_diff
                self.pot_contributions[0] += bet_diff
                bot1_bet = new_bet
                
            else:
                # Bot 2's turn
                action, new_bet = self.get_bot_action(1, self.bot2, bot1_bet, bot2_bet)
                
                if action == 0:  # Fold
                    return 0  # Bot 1 wins
                    
                # Update bet
                if new_bet > bot2_bet:
                    # This is a raise
                    if raises_made < self.max_raises:
                        raises_made += 1
                        last_raiser = 1
                    else:
                        # Can't raise, must call
                        new_bet = bot1_bet
                
                # Update chips and pot
                bet_diff = new_bet - bot2_bet
                self.chips[1] -= bet_diff
                self.pot += bet_diff
                self.pot_contributions[1] += bet_diff
                bot2_bet = new_bet
            
            # Check if round is finished
            if bot1_bet == bot2_bet:
                if last_raiser is None or last_raiser != active_player:
                    round_finished = True
            
            # Switch active player
            active_player = 1 - active_player
            
        return None  # No one folded, continue to next street
    
    def play_hand(self):
        """
        Play a complete hand of poker.
        
        Returns:
            tuple: (winner_id, rewards) where rewards is a dict {bot_id: reward}
        """
        # Reset game state
        self.reset_game()
        
        # Deal cards
        self.deal_cards()
        
        # Collect blinds/antes (simplified)
        small_blind = self.bet_size // 2
        big_blind = self.bet_size
        
        self.chips[0] -= small_blind
        self.pot += small_blind
        self.pot_contributions[0] += small_blind
        
        self.chips[1] -= big_blind  
        self.pot += big_blind
        self.pot_contributions[1] += big_blind
        
        # Current stage starts at preflop
        current_stage = "preflop"
        
        # Play each betting round
        while True:
            result = self.play_betting_round()
            
            # If someone folded, end the hand
            if result is not None:
                winner = result
                # Calculate rewards
                rewards = {
                    0: self.pot if winner == 0 else -self.pot_contributions[0],
                    1: self.pot if winner == 1 else -self.pot_contributions[1]
                }
                return winner, rewards
            
            # Advance to next stage
            if not self.advance_stage():
                # We've reached showdown
                winner = self.evaluate_winner()
                
                # Calculate rewards
                if winner == -1:  # Split pot
                    rewards = {0: 0, 1: 0}
                else:
                    rewards = {
                        0: self.pot if winner == 0 else -self.pot_contributions[0],
                        1: self.pot if winner == 1 else -self.pot_contributions[1]
                    }
                return winner, rewards

def train_bot(iterations=1000, save_interval=100, display_progress=True):
    """
    Train the QBot against itself for a specified number of iterations.
    
    Args:
        iterations (int): Number of hands to play
        save_interval (int): How often to save the bot's strategy
        display_progress (bool): Whether to print progress updates
        
    Returns:
        QBot: The trained bot
    """
    # Initialize bots (they will share the strategy)
    bot = QBot(num_buckets=20)
    training_bot = QBot(num_buckets=20, save_path="training_q_strategy.json")
    
    # Initialize self-play environment
    game = SelfPlayGame(bot, training_bot)
    
    # Training statistics
    wins = {0: 0, 1: 0, -1: 0}  # -1 represents split pots
    
    for i in range(iterations):
        # Play a hand
        winner, rewards = game.play_hand()
        
        # Update win statistics
        wins[winner] = wins.get(winner, 0) + 1
        
        # Update Q-values for both bots
        bot.update(rewards[0])
        training_bot.update(rewards[1])
        
        # Display progress
        if display_progress and (i+1) % (iterations // 10) == 0:
            win_rate = (wins[0] / (i+1)) * 100
            print(f"Progress: {i+1}/{iterations} hands played")
            print(f"Bot 1 wins: {wins[0]} ({win_rate:.1f}%)")
            print(f"Bot 2 wins: {wins[1]} ({(wins[1]/(i+1))*100:.1f}%)")
            print(f"Split pots: {wins[-1]} ({(wins[-1]/(i+1))*100:.1f}%)")
            print()
        
        # Save strategy at intervals
        if (i+1) % save_interval == 0:
            bot.save_strategy()
    
    # Final save
    bot.save_strategy()
    
    # Return the trained bot
    return bot

if __name__ == "__main__":
    import sys
    
    # Check if iterations parameter is provided
    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
            print(f"Starting self-play training for {iterations} iterations...")
            train_bot(iterations=iterations)
        except ValueError:
            print(f"Invalid iterations value: {sys.argv[1]}. Please provide a valid integer.")
    else:
        # If no training parameter, the file is being imported for normal gameplay
        pass