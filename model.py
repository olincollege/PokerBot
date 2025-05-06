"""Contains the Model class for the poker game."""

from time import sleep
import random

from ML_bot import bot_action, QBot
from hand_evaluator import eval7
from view import PokerView
from controller import Controller
from config import (
    PLAYER_NAME,
    STARTING_STACK,
    SMALL_BLIND,
    BIG_BLIND,
    BET_SIZES,
    MAX_RAISES_PER_ROUND,
)
from config import player_blind_pos, bot_blind_pos


class Model:
    """
    Model class for the poker game. It handles the game logic, including
    dealing cards, managing bets, and determining the winner.

    Attributes:
        players (list): List of player names.
        chips (dict): Dictionary mapping player names to their chip counts.
    """

    def __init__(self):
        """
        Initializes the Model with player names, starting stacks, blinds,
        and other game parameters.

        Args:
            _players (list): List of player names.
            _chips (dict): Dictionary mapping player names to their chip counts.
            _small_blind (int): Amount for the small blind.
            _big_blind (int): Amount for the big blind.
            _deck (list): List representing the deck of cards.
            player_hand (list): List representing the player's hand.
            bot_hand (list): List representing the bot's hand.
            community_cards (list): List representing the community cards.
            pot (int): Amount in the pot.
            round_active (bool): Flag indicating if the round is active.
            _small_blind_holder (str): Player holding the small blind.
            _big_blind_holder (str): Player holding the big blind.
            player_bet (int): Amount bet by the player.
            bot_bet (int): Amount bet by the bot.
            current_bet (int): Current bet size.
            previous_player_bet (int): Previous bet amount by the player.
            previous_bot_bet (int): Previous bet amount by the bot.
            view (PokerView): Instance of the PokerView class.
            controller (Controller): Instance of the Controller class.
            raise_count (int): Number of raises in the current round.
            _max_raises_per_round (int): Maximum raises allowed per round.
            bot (QBot): Instance of the QBot class for the bot's strategy.
            game_history (list): List to track game history
        """
        self._players = [PLAYER_NAME, "Bot"]
        self._chips = {PLAYER_NAME: STARTING_STACK, "Bot": STARTING_STACK}
        self._small_blind = SMALL_BLIND
        self._big_blind = BIG_BLIND
        self._deck = self.create_deck()
        self.player_hand = []
        self.bot_hand = []
        self.community_cards = []
        self.pot = 0
        self.round_active = True
        self.small_blind_holder = "Bot"
        self.big_blind_holder = PLAYER_NAME
        self.player_bet = (
            self._small_blind
            if self.small_blind_holder == PLAYER_NAME
            else self._big_blind
        )
        self.bot_bet = (
            self._big_blind if self.small_blind_holder == "Bot" else self._small_blind
        )
        self.current_bet = max(self.player_bet, self.bot_bet)
        self.previous_player_bet = 0
        self.previous_bot_bet = 0
        self.view = PokerView(self)
        self.previous_stack = (
            self._chips[self._players[0]] + self._chips[self._players[1]]
        )
        self.stage = ""
        self.previous_player_chips = 0
        self.previous_bot_chips = self._chips[self._players[1]]
        self.controller = Controller(self.view)
        self.raise_count = 0  # Track number of raises in current round
        self._max_raises_per_round = MAX_RAISES_PER_ROUND  # Make accessible to bot
        self.bot = QBot(
            num_buckets=20, save_path="q_strategy.json"
        )  # Initialize the bot
        self.game_history = []  # For tracking results
        self.controller = Controller(self.view)  # Initialize the controller

    @property
    def deck(self):
        """Return the deck of cards. Used for testing."""
        return self._deck

    @deck.setter
    def deck(self, value):
        """Set the deck of cards. Used for testing."""
        self._deck = value

    def create_deck(self):
        """Create a deck of cards

        Returns:
            list: A list of strings representing the deck of cards.
        """
        suits = ["spades", "clubs", "diamonds", "hearts"]
        ranks = [
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
        return [f"{rank}_of_{suit}" for suit in suits for rank in ranks]

    def deal_hands(self):
        """Deal two cards to each player"""
        random.shuffle(self._deck)
        self.player_hand = [self._deck.pop(), self._deck.pop()]
        self.bot_hand = [self._deck.pop(), self._deck.pop()]

    def deal_community_cards(self, stage):
        """Deals the appropriate community cards based on the stage.
        Args:
            stage (str): The current stage of the game (flop, turn, river).
        """
        if stage == "flop":
            self.community_cards = [self._deck.pop() for _ in range(3)]
        elif stage in ["turn", "river"]:
            self.community_cards.append(self._deck.pop())

    def player_bet_handling(self):
        """Handle player betting by deducting chips"""
        self._chips[self._players[0]] -= self.player_bet - self.previous_player_bet
        self.previous_player_bet = self.player_bet

    def bot_bet_handling(self):
        """Handle bot betting by deducting chips"""
        self._chips[self._players[1]] -= self.bot_bet - self.previous_bot_bet
        self.previous_bot_bet = self.bot_bet

    def get_current_bet_size(self):
        """Return the current fixed bet size for the stage"""
        return BET_SIZES.get(self.stage, BIG_BLIND)

    def player_action_model(self):
        """Player's action during the betting round (e.g., fold, check, bet, etc.)
        Returns:
            str: Defines how the game continues (continue/winner name).
        """
        action = self.controller.player_action_controller()

        if action == "fold":
            return "Bot"  # Player folds, end hand with Bot Win
        if action == "check":
            if self.player_bet < self.bot_bet:
                self.view.display_invalid_text()
                return self.player_action_model()
            self.view.hide_invalid_text()
            return 0  # Player checks, stays in the pot
        if action == "call":
            self.player_bet = self.current_bet
            self.player_bet_handling()
            self.view.hide_invalid_text()
            return "continue"  # Player calls
        if action == "raise":
            if self.raise_count >= MAX_RAISES_PER_ROUND:
                self.view.display_invalid_text()
                return self.player_action_model()

            bet_size = self.get_current_bet_size()
            self.player_bet = self.current_bet + bet_size
            self.current_bet = self.player_bet
            self.player_bet_handling()
            self.raise_count += 1
            self.view.hide_invalid_text()
            return "continue"

        self.view.display_invalid_text()
        return self.player_action_model()

    def betting_round(self):
        """Handle a betting round with limit betting structure

        Args:
            stage (str): The current stage of the game (pre-flop, flop, turn, river).

        Returns:
            str: The result of the betting round (e.g., "Player", "Bot", or "continue").
        """
        act_first = self.small_blind_holder

        # Reset raise count for new betting round
        self.raise_count = 0

        if act_first == PLAYER_NAME:
            result = self.player_action_model()
            if result in [PLAYER_NAME, "Bot"]:
                return result
            result = bot_action(self)
            # Update bot bet display after bot acts
            self.view.display_bot_stack(self._chips[self._players[1]])
            self.view.display_bot_round_bet(
                self.previous_player_chips - self._chips[self._players[0]]
            )
            if result in [PLAYER_NAME, "Bot"]:
                return result
        else:
            result = bot_action(self)
            # Update bot bet display immediately after bot acts
            bot_round_bet = self.previous_bot_chips - self._chips[self._players[1]]
            self.view.display_bot_stack(self._chips[self._players[1]])
            self.view.display_bot_round_bet(bot_round_bet)
            if result in [PLAYER_NAME, "Bot"]:
                return result
            result = self.player_action_model()
            if result in [PLAYER_NAME, "Bot"]:
                return result

        while self.player_bet != self.bot_bet:
            # Update displayed bets
            player_round_bet = (
                self.previous_player_chips - self._chips[self._players[0]]
            )
            bot_round_bet = self.previous_bot_chips - self._chips[self._players[1]]
            self.view.display_player_round_bet(player_round_bet)
            self.view.display_bot_round_bet(bot_round_bet)

            self.get_round_bets()
            self.view.display_pot(self.pot)

            if self.player_bet < self.bot_bet:
                self.view.display_bot_stack(self._chips[self._players[1]])
                self.view.display_player_stack(self._chips[self._players[0]])
                result = self.player_action_model()
                if result == "Bot":  # Player folded
                    return result
            else:
                result = bot_action(self)
                # Update bot display after action
                bot_round_bet = self.previous_bot_chips - self._chips[self._players[1]]
                self.view.display_bot_stack(self._chips[self._players[1]])
                self.view.display_bot_round_bet(bot_round_bet)
                if result == PLAYER_NAME:  # Bot folded
                    return result

    def run(self):
        """Main game loop for running the poker game"""

        # Initialize game state
        self.controller.start_game()
        # Reset game state for a new hand
        self.reset_after_hand()
        self.deal_hands()
        # Lets users known game state
        self.view.initialize_game_view(
            self.pot,
            self.player_hand,
            self._chips[self._players[0]],
            self._chips[self._players[1]],
            self.small_blind_holder,
        )
        # Displays big blind and small blind bets
        self.get_round_bets()

        # Preflop betting
        self.stage = "Preflop"
        self.view.display_round(self.stage)
        result = self.betting_round()
        self.get_round_bets()
        self.view.display_player_stack(self._chips[self._players[0]])
        self.view.display_bot_stack(self._chips[self._players[1]])

        # Handle result if someone folded
        if result in [PLAYER_NAME, "Bot"]:
            self.view.display_winner(result)

            # Calculate reward for the bot's learning
            reward = 1.0 if result == "Bot" else -1.0
            reward *= self.pot
            self.bot.update(reward)

            # Distribute pot
            if result == PLAYER_NAME:
                self._chips[self._players[0]] += self.pot
            else:
                self._chips[self._players[1]] += self.pot

            self.pot = 0
            self.run()

        for stage in ["flop", "turn", "river"]:
            self.stage = stage
            self.view.display_round(self.stage)
            self.reset_after_betting_round()
            self.view.display_pot(self.pot)
            self.deal_community_cards(self.stage)

            # Display community cards
            if stage == "flop":
                self.view.display_flop(self.community_cards[0:3])
            elif stage == "turn":
                self.view.display_turn(self.community_cards[3:4])
            elif stage == "river":
                self.view.display_river(self.community_cards[4:5])

            result = self.betting_round()
            self.view.display_player_stack(self._chips[self._players[0]])
            self.view.display_bot_stack(self._chips[self._players[1]])
            self.get_round_bets()

            # Handle result if someone folded
            if result in [PLAYER_NAME, "Bot"]:
                self.pot = (
                    self.previous_stack
                    - self._chips[self._players[0]]
                    - self._chips[self._players[1]]
                )
                self.view.display_winner(result)

                # Calculate reward for the bot's learning
                if result == "Bot":
                    reward = 1.0  # Bot wins
                else:
                    reward = -1.0  # Player wins

                # Scale reward by pot size
                reward *= self.pot

                # Update bot strategy with the scaled reward
                self.bot.update(reward)

                # Distribute pot
                if result == PLAYER_NAME:
                    self._chips[self._players[0]] += self.pot
                else:
                    self._chips[self._players[1]] += self.pot

                self.run()

        # Showdown (winner determination)
        self.view.display_showdown()
        self.view.display_bot_hand(self.bot_hand)
        sleep(3)
        player_hand_rank = self.hand_evaluator(self.player_hand + self.community_cards)
        bot_hand_rank = self.hand_evaluator(self.bot_hand + self.community_cards)

        self.pot = (
            self.previous_stack
            - self._chips[self._players[0]]
            - self._chips[self._players[1]]
        )
        self.view.display_pot(self.pot)

        # Determine winner and update bot's strategy
        if player_hand_rank < bot_hand_rank:  # Lower rank is better in the evaluator
            self.view.display_winner(PLAYER_NAME)
            self._chips[self._players[0]] += self.pot
            reward = -1 * self.pot  # Negative reward for losing
            self.bot.update(reward)
            self.run()
        elif player_hand_rank == bot_hand_rank:
            self._chips[self._players[0]] += self.pot // 2
            self._chips[self._players[1]] += self.pot // 2
            self.bot.update(0.0)  # Neutral reward for tie
            self.run()
        else:
            self.view.display_winner("Bot")
            self._chips[self._players[1]] += self.pot
            reward = 1 * self.pot  # Positive reward for winning
            self.bot.update(reward)
            self.run()

    def hand_evaluator(self, cards):
        """Evaluate the best hand from the player's and community cards
        Args:
            cards (list): List of cards to evaluate.
        Returns:
            result(str): The best hand rank.
        """
        result = eval7(cards)
        return result

    def reset_after_betting_round(self):
        """Reset betting values after a betting round"""
        self.player_bet = 0
        self.bot_bet = 0
        self.previous_player_bet = self.player_bet
        self.previous_bot_bet = self.bot_bet
        self.current_bet = max(self.player_bet, self.bot_bet)
        self.pot = (
            self.previous_stack
            - self._chips[self._players[0]]
            - self._chips[self._players[1]]
        )
        self.raise_count = 0  # Reset raise count for new betting round

    def reset_after_hand(self):
        """Reset Many Values after hand ends"""
        self._deck = []
        self._deck = self.create_deck()

        # Switch blinds
        if self.small_blind_holder == "Bot":
            self.small_blind_holder = PLAYER_NAME
            self.big_blind_holder = "Bot"
            self.view.display_small_blind(player_blind_pos)
            self.view.display_big_blind(bot_blind_pos)
        else:
            self.small_blind_holder = "Bot"
            self.big_blind_holder = PLAYER_NAME
            self.view.display_small_blind(bot_blind_pos)
            self.view.display_big_blind(player_blind_pos)

        # Set bets according to blinds
        self.player_bet = (
            SMALL_BLIND if self.small_blind_holder == PLAYER_NAME else BIG_BLIND
        )
        self.bot_bet = (
            BIG_BLIND if self.small_blind_holder == PLAYER_NAME else SMALL_BLIND
        )

        self.previous_player_bet = self.player_bet
        self.previous_bot_bet = self.bot_bet
        self.previous_stack = (
            self._chips[self._players[0]] + self._chips[self._players[1]]
        )
        self.previous_player_chips = self._chips[self._players[0]]
        self.previous_bot_chips = self._chips[self._players[1]]

        # Post blinds
        self._chips[self._players[0]] -= self.player_bet
        self._chips[self._players[1]] -= self.bot_bet

        # Put blinds into the pot
        self.pot = (
            self.previous_stack
            - self._chips[self._players[0]]
            - self._chips[self._players[1]]
        )
        self.current_bet = max(self.player_bet, self.bot_bet)
        self.raise_count = 0  # Reset raise count for new hand
        self.community_cards = []  # Clear community cards

    def get_round_bets(self):
        """Calculate and display round bets"""
        # Calculate the round bets for both players
        player_round_bet = self.previous_player_chips - self._chips[self._players[0]]
        bot_round_bet = self.previous_bot_chips - self._chips[self._players[1]]
        # Display the round bets
        self.view.display_player_round_bet(player_round_bet)
        self.view.display_bot_round_bet(bot_round_bet)

    @property
    def chips(self):
        """Return the chips of the players"""
        return self._chips

    @property
    def max_raises_per_round(self):
        """Return the maximum raises allowed per round"""
        return self._max_raises_per_round

    @property
    def players(self):
        """Return the players in the game"""
        return self._players
