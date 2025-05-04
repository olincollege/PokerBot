from time import sleep
import random
from player import player_action
from bot import bot_action
from hand_evaluator import eval7
from config import PLAYER_NAME, STARTING_STACK, SMALL_BLIND, BIG_BLIND
import QBot



class PokerGame:
    def __init__(self):
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
        self.previous_bot_bet = 0
        self.previous_player_bet = 0
        QBot.starting_chips = self.chips[self.players[1]]

    def create_deck(self):
        """Create a deck of cards"""
        suits = ["♠", "♣", "♦", "♥"]
        ranks = [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "T",
            "J",
            "Q",
            "K",
            "A",
        ]
        return [f"{rank}{suit}" for suit in suits for rank in ranks]

    def deal_hands(self):
        """Deal two hole cards to each player"""
        random.shuffle(self.deck)
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.bot_hand = [self.deck.pop(), self.deck.pop()]
        print(
            f"\n{self.players[0]}'s Hand: {self.player_hand[0]} {self.player_hand[1]}"
        )  # Player sees their own cards

    def display_hands(self):
        """Shows player's hands (for the player only)"""
        print(
            f"\n{self.players[0]}'s Hand: {self.player_hand[0]} {self.player_hand[1]}"
        )

    def display_bot_hand(self):
        """Displays bot hand"""
        print(
            f"\n{self.players[1]}'s Hand: {self.bot_hand[0]} {self.bot_hand[1]}"
        )

    def betting_round(self, stage):
        """Handle a simple betting round, player vs bot"""
        print(f"Starting Betting Round: {stage}")
        act_first = self.small_blind_holder
        print(f"Player Bet: {self.player_bet}")
        print(f"Player Stack: {self.chips[self.players[0]]}")
        print(f"Bot Bet: {self.bot_bet}")
        print(f"Bot Stack: {self.chips[self.players[1]]}")

        if act_first == PLAYER_NAME:
            result = player_action(self)
            if result in [PLAYER_NAME, "Bot"]:
                return result
            result = bot_action(self)
            if result in [PLAYER_NAME, "Bot"]:
                return result
        else:
            result = bot_action(self)
            if result in [PLAYER_NAME, "Bot"]:
                return result
            result = player_action(self)
            if result in [PLAYER_NAME, "Bot"]:
                return result

        while self.player_bet != self.bot_bet:
            print(f"Player Bet: {self.player_bet}")
            print(f"Player Stack: {self.chips[self.players[0]]}")
            print(f"Bot Bet: {self.bot_bet}")
            print(f"Bot Stack: {self.chips[self.players[1]]}")
            print(f"test: {act_first}")
            if self.player_bet < self.bot_bet:
                result = player_action(self)
                if result == "Bot":  # Player folded
                    return "Bot"
            else:
                result = bot_action(self)
                if result == PLAYER_NAME:  # Bot folded
                    print("DEBUG - Player should win")
                    return PLAYER_NAME

    def deal_community_cards(self, stage):
        """Deals the appropriate community cards based on the stage."""
        if stage == "flop":
            self.community_cards = [self.deck.pop() for _ in range(3)]
        elif stage == "turn" or stage == "river":
            self.community_cards.append(self.deck.pop())
        print(f"Community cards: {self.community_cards}")

    def run(self):
        self.reset_after_hand()  # causes errors I think, need to replace to reset bets
        self.deal_hands()
        print("Starting a new hand of poker!")
        self.pot = self.small_blind + self.big_blind
        print(f"Pot starts at {self.pot}")
        # Preflop betting
        stage = "Preflop"
        result = self.betting_round(stage)
        pot = self.player_bet + self.bot_bet
        if result in [PLAYER_NAME, "Bot"]:
            print(f"{result} Wins {pot}!")
            if result == PLAYER_NAME:
                self.chips[self.players[0]] += pot
            else:
                self.chips[self.players[1]] += pot
            pot = 0
            return result

        for step in ["flop", "turn", "river"]:
            stage = step
            self.reset_after_betting_round()
            self.display_hands()
            print(f"Pot: {pot}")
            self.deal_community_cards(stage)
            result = self.betting_round(stage)
            pot += self.player_bet + self.bot_bet
            if result in [PLAYER_NAME, "Bot"]:
                print(f"{result} Wins {pot}!")
                if result == PLAYER_NAME:
                    self.chips[self.players[0]] += pot
                else:
                    self.chips[self.players[1]] += pot
                pot = 0
                return result

        # Showdown (winner determination logic to be added)
        print("Showdown! Determine the winner based on hand strength.")
        self.display_hands()
        self.display_bot_hand()
        sleep(3)
        player_hand_rank = self.hand_evaluator(
            self.player_hand + self.community_cards
        )
        bot_hand_rank = self.hand_evaluator(
            self.bot_hand + self.community_cards
        )
        print(f"Player hand rank: {player_hand_rank}")
        print(f"Bot hand rank: {bot_hand_rank}")
        if player_hand_rank < bot_hand_rank:
            print(f"Player Wins {pot} at Showdown!")
            self.chips[self.players[0]] += pot
            pot = 0
        elif player_hand_rank == bot_hand_rank:
            print(f"Same Best 5 Cards, Chop {pot}!")
            self.chips[self.players[0]] += pot / 2
            self.chips[self.players[1]] += pot / 2
            pot = 0
        else:
            print(f"Bot Wins {pot} at Showdown!")
            self.chips[self.players[1]] += pot
            pot = 0

    def hand_evaluator(self, cards):
        result = eval7(cards)

        return result

    def reset_after_betting_round(self):
        self.player_bet = 0
        self.bot_bet = 0
        self.previous_player_bet = self.player_bet
        self.previous_bot_bet = self.bot_bet
        self.current_bet = max(self.player_bet, self.bot_bet)

    def reset_after_hand(self):
        """Reset Many Values after hand ends"""
        final_reward = self.chips[self.players[1]] - QBot.starting_chips
        QBot.update(final_reward)
        QBot.starting_chips = self.chips[self.players[1]]
        self.deck = []
        self.deck = self.create_deck()
        if self.small_blind_holder == "Bot":
            self.small_blind_holder = PLAYER_NAME
            self.big_blind_holder = "Bot"
        else:
            self.small_blind_holder = "Bot"
            self.big_blind_holder = PLAYER_NAME
        self.player_bet = 25 if self.small_blind_holder == PLAYER_NAME else 50
        self.bot_bet = 50 if self.small_blind_holder == PLAYER_NAME else 25
        self.previous_player_bet = self.player_bet
        self.previous_bot_bet = self.bot_bet
        self.chips[self.players[0]] -= self.player_bet
        self.chips[self.players[1]] -= self.bot_bet
        self.current_bet = max(self.player_bet, self.bot_bet)
