"""
Training module for the QBot poker AI using self-play.

This module provides functionality to train the QBot poker AI through self-play
in a limit hold'em environment. It simulates poker games where the bot plays
against itself, learning from the outcomes and improving its strategy over time.

Usage:
    python train_ML_bot.py <iterations>
        iterations: Number of hands to play during training
"""

import random
import logging
import argparse
from ML_bot import QBot, get_hand_rank

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="training.log",
    filemode="a",
)
logger = logging.getLogger("training")


class LimitHoldemSelfPlay:
    """
    A simulation environment for training QBot in limit hold'em through self-play.

    This class provides a complete limit hold'em game environment where two instances
    of QBot can play against each other. The environment handles all game mechanics,
    including dealing cards, managing betting rounds, evaluating hands, and tracking
    rewards.

    Attributes:
        bot1 (QBot): First QBot instance.
        bot2 (QBot): Second QBot instance.
        sb_amount (int): Small blind amount (default: 1).
        bb_amount (int): Big blind amount (default: 2).
        small_bet (int): Small bet size for preflop and flop (default: 2).
        big_bet (int): Big bet size for turn and river (default: 4).
        starting_chips (int): Initial chip stack for each bot (default: 1000).
    """

    def __init__(
        self,
        bot1,
        bot2,
        sb_amount=1,
        bb_amount=2,
        small_bet=2,
        big_bet=4,
        starting_chips=1000,
    ):
        """
        Initialize a new limit hold'em self-play environment.

        Args:
            bot1 (QBot): First bot instance.
            bot2 (QBot): Second bot instance.
            sb_amount (int): Small blind amount.
            bb_amount (int): Big blind amount.
            small_bet (int): Small bet size for preflop and flop rounds.
            big_bet (int): Big bet size for turn and river rounds.
            starting_chips (int): Starting chip stack for each bot.
        """
        self.bot1 = bot1
        self.bot2 = bot2
        self.sb_amount = sb_amount
        self.bb_amount = bb_amount
        self.small_bet = small_bet
        self.big_bet = big_bet
        self.starting_chips = starting_chips
        self.community_cards = []
        self.hand1 = []
        self.hand2 = []
        self.flop = []
        self.turn = []
        self.river = []
        self.stage = ""
        self.max_raises_reached = False

        # Initialize game state
        self.reset_game()

        # Standard 52-card deck
        self.ranks = [
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
        self.suits = ["hearts", "diamonds", "clubs", "spades"]
        self.deck = [f"{rank}_of_{suit}" for rank in self.ranks for suit in self.suits]

    def reset_game(self):
        """
        Reset the game state for a new hand.

        This method initializes or resets all game state variables to prepare for
        a new hand of poker, including chip stacks, cards, pot, and betting status.
        """
        self.chips = {0: self.starting_chips, 1: self.starting_chips}
        self.community_cards = []
        self.pot = 0
        self.hand1 = []
        self.hand2 = []
        self.stage = "preflop"
        self.pot_contributions = {0: 0, 1: 0}
        self.current_bet = 0
        self.active_player = 0  # Player 0 starts
        self.button_pos = random.randint(0, 1)  # Randomize button position
        self.max_raises_reached = False

    def deal_cards(self):
        """
        Shuffle the deck and deal cards to players and the board.

        This method shuffles the deck and deals two hole cards to each player
        as well as the community cards (flop, turn, river) that will be revealed
        during the hand.
        """
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
        """
        Move to the next betting round in the hand.

        This method advances the game to the next stage (preflop -> flop -> turn -> river)
        and reveals the appropriate community cards.

        Returns:
            bool: True if the game advanced to a new stage, False if the hand is complete.
        """
        if self.stage == "preflop":
            self.stage = "flop"
            self.community_cards = self.flop
            self.max_raises_reached = False  # Reset raise counter for new street
        elif self.stage == "flop":
            self.stage = "turn"
            self.community_cards = self.flop + self.turn
            self.max_raises_reached = False  # Reset raise counter for new street
        elif self.stage == "turn":
            self.stage = "river"
            self.community_cards = self.flop + self.turn + self.river
            self.max_raises_reached = False  # Reset raise counter for new street
        else:
            return False  # Hand is over
        return True

    def evaluate_winner(self):
        """
        Determine the winner at showdown.

        This method compares the hand strengths of both players to determine
        the winner at showdown.

        Returns:
            int: 0 if bot1 wins, 1 if bot2 wins, -1 for a split pot.
        """
        hand1_rank = get_hand_rank(self.hand1, self.community_cards)
        hand2_rank = get_hand_rank(self.hand2, self.community_cards)

        if hand1_rank < hand2_rank:  # Lower rank is better in this evaluator
            return 0  # Bot 1 wins
        if hand2_rank < hand1_rank:
            return 1  # Bot 2 wins
        return -1  # Split pot

    def get_current_bet_size(self):
        """
        Get the appropriate bet size for the current betting round.

        In limit hold'em, bet sizes are fixed based on the current street.

        Returns:
            int: The current bet size (small_bet for preflop/flop, big_bet for turn/river).
        """
        if self.stage in ["preflop", "flop"]:
            return self.small_bet
        # turn or river
        return self.big_bet

    def get_bot_action(self, bot_id, bot, opponent_bet, bot_bet):
        """
        Get action decision from a bot.

        This method handles the decision-making process for a bot, encoding the
        current game state, determining valid actions, and recording the chosen
        action for later learning.

        Args:
            bot_id (int): 0 for bot1, 1 for bot2.
            bot (QBot): The bot making the decision.
            opponent_bet (int): Current bet from opponent.
            bot_bet (int): Current bet from this bot.

        Returns:
            tuple: (action, new_bet) where action is 0 (fold), 1 (call), or 2 (raise).
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
        valid_actions = bot.get_valid_actions(betting_state, self.max_raises_reached)

        # Choose action
        action = bot.choose_action(state, valid_actions)

        # Record state-action pair
        bot.record(state, action)

        # Calculate new bet based on action
        new_bet = bot_bet
        if action == 1:  # Call/Check
            new_bet = opponent_bet
        elif action == 2:  # Raise
            # In limit hold'em, raise amount is fixed
            new_bet = opponent_bet + self.get_current_bet_size()

        return action, new_bet

    def play_betting_round(self):
        """
        Play a single betting round between the two bots.

        This method simulates a complete betting round, with each bot taking
        turns to act until the betting is complete or a bot folds.

        Returns:
            int or None: If a bot folds, returns the winner's ID. Otherwise None.
        """
        bot1_bet = 0
        bot2_bet = 0
        round_finished = False
        last_raiser = None

        # Keep track of number of raises in this round
        raises_made = 0
        max_raises = 4  # Limit hold'em typically allows 4 raises per round

        # In limit hold'em, the player on the button acts first preflop,
        # and the player not on the button acts first on later streets
        if self.stage == "preflop":
            active_player = 1 - self.button_pos  # Small blind acts first
        else:
            active_player = self.button_pos  # Button acts first postflop

        # Handle blinds for preflop
        if self.stage == "preflop":
            sb_player = 1 - self.button_pos

            # Post blinds
            if sb_player == 0:
                bot1_bet = self.sb_amount
                bot2_bet = self.bb_amount
            else:
                bot1_bet = self.bb_amount
                bot2_bet = self.sb_amount

            # Update pot and chips
            self.pot += bot1_bet + bot2_bet
            self.pot_contributions[0] += bot1_bet
            self.pot_contributions[1] += bot2_bet
            self.chips[0] -= bot1_bet
            self.chips[1] -= bot2_bet

        while not round_finished:
            if active_player == 0:
                # Bot 1's turn
                action, new_bet = self.get_bot_action(0, self.bot1, bot2_bet, bot1_bet)

                if action == 0:  # Fold
                    return 1  # Bot 2 wins

                # Update bet
                if new_bet > bot1_bet:
                    # This is a raise
                    if raises_made < max_raises:
                        raises_made += 1
                        last_raiser = 0
                    else:
                        # Can't raise, must call
                        self.max_raises_reached = True
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
                    if raises_made < max_raises:
                        raises_made += 1
                        last_raiser = 1
                    else:
                        # Can't raise, must call
                        self.max_raises_reached = True
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

        # Reset max raises flag if we've hit the cap
        if raises_made >= max_raises:
            self.max_raises_reached = True

        return None  # No one folded, continue to next street

    def play_hand(self):
        """
        Play a complete hand of limit hold'em poker.

        This method simulates a complete hand from dealing cards through all
        betting rounds to showdown or until one player folds.

        Returns:
            tuple: (winner_id, rewards) where rewards is a dict {bot_id: reward}
        """
        # Reset game state and deal cards
        self.reset_game()
        self.deal_cards()

        # Play each betting round
        while True:
            result = self.play_betting_round()

            # If someone folded, end the hand
            if result is not None:
                winner = result
                # Calculate rewards - winner gets the pot
                rewards = {
                    0: self.pot if winner == 0 else -self.pot,
                    1: self.pot if winner == 1 else -self.pot,
                }
                return winner, rewards

            # Advance to next stage
            if not self.advance_stage():
                # We've reached showdown
                winner = self.evaluate_winner()

                # Calculate rewards
                if winner == -1:  # Split pot
                    # Each player gets back their contribution
                    rewards = {0: 0, 1: 0}  # Net profit is 0 for split
                else:
                    # Winner gets the pot minus their contribution (net profit)
                    rewards = {
                        0: self.pot if winner == 0 else -self.pot,
                        1: self.pot if winner == 1 else -self.pot,
                    }
                return winner, rewards


def train_bot(iterations=1000, save_interval=100, display_progress=True):
    """
    Train the QBot against itself for a specified number of iterations.

    This function creates two QBot instances and trains them through self-play
    in the limit hold'em environment.

    Args:
        iterations (int): Number of hands to play.
        save_interval (int): How often to save the bot's strategy.
        display_progress (bool): Whether to print progress updates.

    Returns:
        QBot: The trained bot instance.
    """
    # Initialize bots (they will share the strategy file)
    bot = QBot(num_buckets=20)
    training_bot = QBot(num_buckets=20, save_path="training_q_strategy.json")

    # Initialize self-play environment
    game = LimitHoldemSelfPlay(bot, training_bot)

    # Training statistics
    wins = {0: 0, 1: 0, -1: 0}  # -1 represents split pots
    total_reward = 0

    logger.info("Starting training for %d iterations", iterations)

    for i in range(iterations):
        # Play a hand
        winner, rewards = game.play_hand()

        # Update win statistics
        wins[winner] = wins.get(winner, 0) + 1

        # Track total reward for bot 1
        total_reward += rewards[0]

        # Update Q-values for both bots
        bot.update(rewards[0])
        training_bot.update(rewards[1])

        # Display progress
        if display_progress and (i + 1) % (iterations // 10 or 1) == 0:
            win_rate = (wins[0] / (i + 1)) * 100
            avg_reward = total_reward / (i + 1)

            progress_msg = (
                f"Progress: {i+1}/{iterations} hands played\n"
                f"Bot 1 wins: {wins[0]} ({win_rate:.1f}%)\n"
                f"Bot 2 wins: {wins[1]} ({(wins[1]/(i+1))*100:.1f}%)\n"
                f"Split pots: {wins[-1]} ({(wins[-1]/(i+1))*100:.1f}%)\n"
                f"Average reward for Bot 1: {avg_reward:.2f}\n"
            )

            print(progress_msg)
            logger.info(progress_msg)

        # Save strategy at intervals
        if (i + 1) % save_interval == 0:
            bot.save_strategy()
            logger.info("Strategy saved after %d iterations", i + 1)

    # Final save
    bot.save_strategy()
    logger.info("Training complete. Final strategy saved.")

    # Return the trained bot
    return bot


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Train QBot through self-play in limit hold'em"
    )
    parser.add_argument(
        "iterations",
        type=int,
        nargs="?",
        default=1000,
        help="Number of hands to play during training",
    )
    parser.add_argument(
        "--save-interval",
        type=int,
        default=100,
        help="How often to save the bot's strategy",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    print(f"Starting self-play training for {args.iterations} iterations...")
    train_bot(
        iterations=args.iterations,
        save_interval=args.save_interval,
        display_progress=not args.quiet,
    )
