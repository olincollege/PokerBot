from bot import bot_action
from hand_evaluator import eval7

# from hand_history import HandHistory
from time import sleep
from model import Model
from view import PokerView
from config import PLAYER_NAME, STARTING_STACK, SMALL_BLIND, BIG_BLIND
import random


class Controller:
    def __init__(self, model):
        self.model = model
        self.view = PokerView(self.model)
        self.game_started = False
        self.cards = []
        self.player_hand = self.model.player_hand

    def start_game(self):
        """Start the game by dealing cards and displaying the initial state."""
        if not self.game_started:
            self.game_started = True
            self.model.run()
            self.model.reset_after_hand()
            self.game_started = False

        # self.view.display_bot_hand()
