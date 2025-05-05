from bot import bot_action
from hand_evaluator import eval7
from view import PokerView
from player import player_action_controller
import pygame
from controller import Controller

# from hand_history import HandHistory
from time import sleep
from config import PLAYER_NAME, STARTING_STACK, SMALL_BLIND, BIG_BLIND
from config import player_blind_pos, bot_blind_pos
import random


class Model:
    def __init__(self, PLAYER_NAME=PLAYER_NAME):
        self.players = [PLAYER_NAME, "Bot"]
        self.chips = {PLAYER_NAME: STARTING_STACK, "Bot": STARTING_STACK}
        self.small_blind = SMALL_BLIND
        self.big_blind = BIG_BLIND
        self.deck = self.create_deck()
        self.player_hand = []
        self.bot_hand = []
        self.community_cards = []
        self.pot = 0
        self.round_active = True
        self.small_blind_holder = "Bot"
        self.big_blind_holder = PLAYER_NAME
        self.player_bet = 25 if self.small_blind_holder == PLAYER_NAME else 50
        self.bot_bet = 50 if self.small_blind_holder == PLAYER_NAME else 25
        self.current_bet = max(self.player_bet, self.bot_bet)
        self.previous_player_bet = 0
        self.previous_bot_bet = 0
        self.view = PokerView(self)
        self.previous_stack = self.chips[self.players[0]] + self.chips[self.players[1]]
        self.stage = ""
        self.previous_player_chips = 0
        self.previous_bot_chips = 0
        self.controller = Controller(self.view)

    def create_deck(self):
        """Create a deck of cards"""
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
        """Deal two hole cards to each player"""
        random.shuffle(self.deck)
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.bot_hand = [self.deck.pop(), self.deck.pop()]

    def deal_community_cards(self, stage):
        """Deals the appropriate community cards based on the stage."""
        if stage == "flop":
            self.community_cards = [self.deck.pop() for _ in range(3)]
        elif stage == "turn" or stage == "river":
            self.community_cards.append(self.deck.pop())

    def player_bet_handling(self):
        self.chips[self.players[0]] -= self.player_bet - self.previous_player_bet
        self.previous_player_bet = self.player_bet

    def player_action_model(self):
        """Player's action during the betting round (e.g., fold, check, bet, etc.)"""
        action = player_action_controller(self)
        print(f"{action}")

        if action == "fold":
            return "Bot"  # Player folds, end hand with Bot Win
        elif action == "check":
            if self.player_bet < self.bot_bet:
                print("Invalid action. Try again.")
                self.view.display_invalid_text()
                return self.player_action_model()
            self.view.hide_invalid_text()
            return 0  # Player checks, stays in the pot
        elif action == "call":
            self.player_bet = self.current_bet
            self.player_bet_handling()
            print("Player Called")
            self.view.hide_invalid_text()
            return "continue"
            # Player calls
        elif action == "raise":
            raise_amount = int(input("Raise your current bet by: "))
            if (
                self.player_bet + raise_amount > self.bot_bet
            ):  # Make sure raise amount is more than bot bet
                self.player_bet += raise_amount
                self.current_bet = self.player_bet
                self.player_bet_handling()
                self.view.hide_invalid_text()
                return "continue"
            else:
                print("Invalid Raise Amount Try Again")
                self.view.display_invalid_text()
                return self.player_action_model()

        else:
            print("Invalid action. Try again.")
            self.view.display_invalid_text()
            return self.player_action_model()

    def betting_round(self, stage):
        """Handle a simple betting round, player vs bot"""
        print(f"Starting Betting Round: {stage}")
        act_first = self.small_blind_holder
        print(f"Player Bet: {self.player_bet}")
        print(f"Player Stack: {self.chips[self.players[0]]}")
        print(f"Bot Bet: {self.bot_bet}")
        print(f"Bot Stack: {self.chips[self.players[1]]}")

        if act_first == PLAYER_NAME:
            result = self.player_action_model()
            print(result)
            if result in [PLAYER_NAME, "Bot"]:
                return result
            result = bot_action(self)
            self.view.display_bot_stack(self.chips[self.players[1]])
            if result in [PLAYER_NAME, "Bot"]:
                return result
        else:
            result = bot_action(self)
            if result in [PLAYER_NAME, "Bot"]:
                return result
            self.view.display_bot_stack(self.chips[self.players[1]])
            result = self.player_action_model()
            if result in [PLAYER_NAME, "Bot"]:
                return result

        while self.player_bet != self.bot_bet:
            # print(f"Player Bet: {self.player_bet}")
            # print(f"Player Stack: {self.chips[self.players[0]]}")
            # print(f"Bot Bet: {self.bot_bet}")
            # print(f"Bot Stack: {self.chips[self.players[1]]}")
            # print(f"test: {act_first}")
            print(f"Pot: {self.pot}")
            self.view.display_player_round_bet(self.player_bet)
            self.get_round_bets()
            self.view.display_pot(self.pot)
            if self.player_bet < self.bot_bet:
                self.view.display_bot_stack(self.chips[self.players[1]])
                self.view.display_player_stack(self.chips[self.players[0]])
                result = self.player_action_model()
                if result == "Bot":  # Player folded
                    return "Bot"
            else:
                result = bot_action(self)
                if result == PLAYER_NAME:  # Bot folded
                    print(f"DEBUG - Player should win")
                    return PLAYER_NAME

    def run(self):
        self.controller.start_game()
        self.reset_after_hand()
        self.deal_hands()
        self.view.initialize_game_view(
            self.pot,
            self.player_hand,
            self.chips[self.players[0]],
            self.chips[self.players[1]],
            self.small_blind_holder,
        )
        self.get_round_bets()
        print("Starting a new hand of poker!")
        print(f"Pot starts at {self.pot}")
        # Preflop betting
        self.stage = "Preflop"
        self.view.display_round(self.stage)
        result = self.betting_round(self.stage)
        self.get_round_bets()
        self.view.display_player_stack(self.chips[self.players[0]])
        self.view.display_bot_stack(self.chips[self.players[1]])
        if result in [PLAYER_NAME, "Bot"]:
            print(f"{result} Wins {self.pot}!")
            self.view.display_winner(result)
            if result == PLAYER_NAME:
                self.chips[self.players[0]] += self.pot
            else:
                print(f"bot chips: {self.chips[self.players[1]]}")
                self.chips[self.players[1]] += self.pot
                print(f"Updated bot chips: {self.chips[self.players[1]]}")
            self.pot = 0
            self.run()

        for stage in ["flop", "turn", "river"]:
            self.stage = stage
            self.view.display_round(self.stage)
            self.reset_after_betting_round()
            self.view.display_pot(self.pot)
            self.deal_community_cards(self.stage)
            if stage == "flop":
                self.view.display_flop(self.community_cards[0:3])
            elif stage == "turn":
                self.view.display_turn(self.community_cards[3:4])
            elif stage == "river":
                self.view.display_river(self.community_cards[4:5])
            result = self.betting_round(self.stage)
            self.view.display_player_stack(self.chips[self.players[0]])
            self.view.display_bot_stack(self.chips[self.players[1]])
            self.get_round_bets()
            if result in [PLAYER_NAME, "Bot"]:
                self.pot = (
                    self.previous_stack
                    - self.chips[self.players[0]]
                    - self.chips[self.players[1]]
                )
                print(f"{result} Wins {self.pot}!")
                self.view.display_winner(result)
                if result == PLAYER_NAME:
                    self.chips[self.players[0]] += self.pot
                else:
                    self.chips[self.players[1]] += self.pot
                self.run()

        # Showdown (winner determination logic to be added)
        self.view.display_showdown()
        self.view.display_bot_hand(self.bot_hand)
        print("Showdown! Determine the winner based on hand strength.")
        sleep(3)
        player_hand_rank = self.hand_evaluator(self.player_hand + self.community_cards)
        bot_hand_rank = self.hand_evaluator(self.bot_hand + self.community_cards)
        print(f"Player hand rank: {player_hand_rank}")
        print(f"Bot hand rank: {bot_hand_rank}")
        self.pot = (
            self.previous_stack
            - self.chips[self.players[0]]
            - self.chips[self.players[1]]
        )
        self.view.display_pot(self.pot)
        if player_hand_rank < bot_hand_rank:
            print(f"Player Wins {self.pot} at Showdown!")
            self.view.display_winner(PLAYER_NAME)
            self.chips[self.players[0]] += self.pot
            self.run()

        elif player_hand_rank == bot_hand_rank:
            print(f"Same Best 5 Cards, Chop {self.pot}!")
            self.chips[self.players[0]] += self.pot // 2
            self.chips[self.players[1]] += self.pot // 2
            self.run()

        else:
            print(f"Bot Wins {self.pot} at Showdown!")
            self.view.display_winner("Bot")
            print(f"Bot chips: {self.chips[self.players[1]]}")
            self.chips[self.players[1]] += self.pot
            print(f"Bot chips: {self.chips[self.players[1]]}")
            self.run()

    def hand_evaluator(self, cards):
        result = eval7(cards)

        return result

    def reset_after_betting_round(self):
        self.player_bet = 0
        self.bot_bet = 0
        self.previous_player_bet = self.player_bet
        self.previous_bot_bet = self.bot_bet
        self.current_bet = max(self.player_bet, self.bot_bet)
        self.pot = (
            self.previous_stack
            - self.chips[self.players[0]]
            - self.chips[self.players[1]]
        )

    def reset_after_hand(self):
        """Reset Many Values after hand ends"""
        self.deck = []
        self.deck = self.create_deck()
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
        self.player_bet = 25 if self.small_blind_holder == PLAYER_NAME else 50
        self.bot_bet = 50 if self.small_blind_holder == PLAYER_NAME else 25
        self.previous_player_bet = self.player_bet
        self.previous_bot_bet = self.bot_bet
        self.previous_stack = self.chips[self.players[0]] + self.chips[self.players[1]]
        self.previous_player_chips = self.chips[self.players[0]]
        self.previous_bot_chips = self.chips[self.players[1]]
        self.chips[self.players[0]] -= self.player_bet
        self.chips[self.players[1]] -= self.bot_bet
        self.pot = (
            self.previous_stack
            - self.chips[self.players[0]]
            - self.chips[self.players[1]]
        )
        self.current_bet = max(self.player_bet, self.bot_bet)

    def get_round_bets(self):
        player_round_bet = self.previous_player_chips - self.chips[self.players[0]]
        bot_round_bet = self.previous_bot_chips - self.chips[self.players[1]]
        self.view.display_player_round_bet(player_round_bet)
        self.view.display_bot_round_bet(bot_round_bet)
