"""
Initializes pygame and loads images for the poker game.
and creates a PokerView class to handle the graphical representation of the game.
"""

import os
import pygame

from config import SCREEN_LENGTH, SCREEN_WIDTH, CARD_LENGTH, CARD_WIDTH
from config import player_hand_pos_1, player_hand_pos_2, bot_hand_pos_1, bot_hand_pos_2
from config import flop_pos_1, flop_pos_2, flop_pos_3, turn_pos, river_pos
from config import raise_button_pos, call_button_pos, check_button_pos, fold_button_pos
from config import BUTTON_LENGTH, BUTTON_WIDTH, BUTTON_COLOR, TEXT_COLOR
from config import bot_stack_pos, player_stack_pos, bot_decision_pos, invalid_text_pos
from config import PIGGY_LENGTH, PIGGY_WIDTH, pot_pos, BLACK_COLOR, display_round_pos
from config import display_winner_pos, display_showdown_pos, GREEN_COLOR, DARK_RED_COLOR
from config import BLIND_LENGTH, BLIND_WIDTH, player_blind_pos, bot_blind_pos
from config import start_game_button_pos, START_BUTTON_WIDTH, START_BUTTON_LENGTH


pygame.font.init()
# Initialize Pygame font module
font = pygame.font.SysFont(None, 32)
# Font for showdown, winner, and invalid text
huge_font = pygame.font.SysFont(None, 100)
# Font for round display
round_font = pygame.font.SysFont(None, 60)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_LENGTH))


def pygamify_image(subfolder, image_name, height, width):
    """Load an image and convert it to a Pygame surface."""

    return pygame.transform.scale(
        pygame.image.load(os.path.join("assets", subfolder, image_name)),
        (width, height),
    ).convert_alpha()


# Convert all images to Pygame images
poker_background = pygamify_image("", "pokertable.jpg", SCREEN_LENGTH, SCREEN_WIDTH)
piggy_bank = pygamify_image("", "piggy_bank.png", PIGGY_LENGTH, PIGGY_WIDTH)
small_blind = pygamify_image("", "small_blind.png", BLIND_LENGTH, BLIND_WIDTH)
big_blind = pygamify_image("", "big_blind.png", BLIND_LENGTH, BLIND_WIDTH)
loading_screen = pygamify_image("", "loading_poker.png", SCREEN_LENGTH, SCREEN_WIDTH)


class PokerView:
    """
    PokerView class to handle the graphical representation of the poker game.

    Attributes:
        _model (Model): The game model containing game data.
        _player_hand (list): The player's hand.
        _bot_hand (list): The bot's hand.
        _flop (list): The flop cards.
        _turn (list): The turn card.
        _river (list): The river card.
        _pot (int): The current pot size.
        _chips (dict): The chips of the players.
        _action_buttons (dict of pygame.rect): The action buttons for the game.


    """

    def __init__(self, model):
        """Initialize the PokerView with game model data."""
        self._model = model
        self._player_hand = self._model.player_hand
        self._bot_hand = self._model.bot_hand
        self._flop = self._model.community_cards[:3]
        self._turn = self._model.community_cards[3:4]
        self._river = self._model.community_cards[4:5]
        self._pot = self._model.pot
        self._chips = self._model.chips
        self._action_buttons = {
            "fold": pygame.Rect(*fold_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
            "check": pygame.Rect(*check_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
            "call": pygame.Rect(*call_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
            "raise": pygame.Rect(*raise_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
        }

    def display_background(self):
        """Display the poker table background."""
        screen.blit(poker_background, (0, 0))
        pygame.display.flip()

    def display_loading_screen(self):
        """Display the loading screen."""
        screen.blit(loading_screen, (0, 0))
        pygame.display.flip()

    def display_player_hand(self, player_hand):
        """Display the player's hand."""
        card1 = pygamify_image(
            "cards", f"{player_hand[0]}.png", CARD_LENGTH, CARD_WIDTH
        )
        card2 = pygamify_image(
            "cards", f"{player_hand[1]}.png", CARD_LENGTH, CARD_WIDTH
        )
        screen.blit(card1, player_hand_pos_1)
        screen.blit(card2, player_hand_pos_2)
        pygame.display.flip()

    def display_flop(self, flop):
        """Display the flop cards.

        Args:
            flop (list): The flop cards.
        """
        card1 = pygamify_image("cards", f"{flop[0]}.png", CARD_LENGTH, CARD_WIDTH)
        card2 = pygamify_image("cards", f"{flop[1]}.png", CARD_LENGTH, CARD_WIDTH)
        card3 = pygamify_image("cards", f"{flop[2]}.png", CARD_LENGTH, CARD_WIDTH)
        screen.blit(card1, flop_pos_1)
        screen.blit(card2, flop_pos_2)
        screen.blit(card3, flop_pos_3)
        pygame.display.flip()

    def display_turn(self, turn):
        """Display the turn card.

        Args:
            turn (list): The turn card.
        """
        card = pygamify_image("cards", f"{turn[0]}.png", CARD_LENGTH, CARD_WIDTH)
        screen.blit(card, turn_pos)
        pygame.display.flip()

    def display_river(self, river):
        """Display the river card.

        Args:
            river (list): The river card.
        """
        card = pygamify_image("cards", f"{river[0]}.png", CARD_LENGTH, CARD_WIDTH)
        screen.blit(card, river_pos)
        pygame.display.flip()

    def display_fold_button(self):
        """Display the fold button."""
        fold_rect = self._action_buttons["fold"]
        pygame.draw.rect(screen, BUTTON_COLOR, fold_rect)
        text_surface = font.render("Fold", True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=fold_rect.center)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_check_button(self):
        """Display the check button."""
        check_rect = self._action_buttons["check"]
        pygame.draw.rect(screen, BUTTON_COLOR, check_rect)
        text_surface = font.render("Check", True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=check_rect.center)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_call_button(self):
        """Display the call button."""
        call_rect = self._action_buttons["call"]
        pygame.draw.rect(screen, BUTTON_COLOR, call_rect)
        text_surface = font.render("Call", True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=call_rect.center)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_raise_button(self):
        """Display the raise button."""
        raise_rect = self._action_buttons["raise"]
        pygame.draw.rect(screen, BUTTON_COLOR, raise_rect)
        text_surface = font.render("Raise", True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=raise_rect.center)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_bot_stack(self, bot_stack):
        """Display the bot's stack.

        Args:
            bot_stack (int): The bot's stack.
        """
        text_rect = pygame.Rect(bot_stack_pos, (300, 30))
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        pygame.display.update(text_rect)
        text_surface = font.render(f"Bot Stack: {bot_stack}", True, TEXT_COLOR)
        screen.blit(text_surface, bot_stack_pos)
        pygame.display.flip()

    def display_player_stack(self, player_stack):
        """Display the player's stack.
        Args:
            player_stack (int): The player's stack.
        """
        text_rect = pygame.Rect(player_stack_pos, (300, 30))
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        pygame.display.update(text_rect)
        text_surface = font.render(f"Player Stack: {player_stack}", True, TEXT_COLOR)
        screen.blit(text_surface, player_stack_pos)
        pygame.display.flip()

    def display_bot_decision(self, decision, poker_stage, raise_amount=None):
        """Display the bot's decision.
        Args:
            decision (str): The bot's decision.
            poker_stage (str): The current stage of the poker game.
            raise_amount (int, optional): The amount raised by the bot. Defaults
            to None if the decision is not raise.
        """
        text_rect = pygame.Rect(bot_decision_pos, (390, 30))
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        pygame.display.update(text_rect)
        if decision == "raise":
            text_surface = font.render(
                f"Bot {poker_stage} Decision: {decision}d by {raise_amount}",
                True,
                TEXT_COLOR,
            )
        else:
            text_surface = font.render(
                f"Bot {poker_stage} Decision: {decision}", True, TEXT_COLOR
            )
        screen.blit(text_surface, bot_decision_pos)
        pygame.display.flip()

    def display_invalid_text(self):
        """Display an invalid move message."""
        text_surface = huge_font.render(
            "THAT MOVE IS INVALID BRO, LEARN POKER", True, TEXT_COLOR
        )
        screen.blit(text_surface, invalid_text_pos)
        pygame.display.flip()

    def hide_invalid_text(self):
        """Hide the invalid move message."""
        text_rect = pygame.Rect(invalid_text_pos, (SCREEN_WIDTH * 0.9, 60))
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        pygame.display.update(text_rect)
        self.display_hidden_bot_hand()

    def display_pot(self, pot):
        """Display the pot amount.
        Args:
            pot (int): The current pot amount.
        """
        text_rect = pygame.Rect(invalid_text_pos, (PIGGY_WIDTH, PIGGY_LENGTH))
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        screen.blit(piggy_bank, pot_pos)
        text_surface = font.render(f"Pot: {pot}", True, BLACK_COLOR)
        screen.blit(text_surface, (pot_pos[0] + 50, pot_pos[1] + 80))
        pygame.display.flip()

    def display_round(self, poker_round):
        """Display the current round.
        Args:
            poker_round (int): The current round (flop, pre-flop, turn, river).
        """
        text_rect = pygame.Rect(display_round_pos, (SCREEN_WIDTH * 0.25, 50))
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        text_surface = round_font.render(f"Round: {poker_round}", True, TEXT_COLOR)
        screen.blit(text_surface, display_round_pos)
        pygame.display.flip()

    def display_winner(self, winner):
        """Display the winner of the game.
        Args:
            winner (str): The winner of the game.
        """
        text_surface = self.render_text_with_outline(
            huge_font, f"{winner} WINS!", GREEN_COLOR, BLACK_COLOR
        )
        text_rect = text_surface.get_rect(center=display_winner_pos)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_showdown(self):
        """Display the showdown message."""
        text_surface = huge_font.render("SHOWDOWN", True, DARK_RED_COLOR)
        text_rect = text_surface.get_rect(center=display_showdown_pos)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_player_round_bet(self, player_bet):
        """Display the player's round bet.
        Args:
            player_bet (int): The player's round bet.
        """
        text_rect = pygame.Rect(
            (player_stack_pos[0], player_stack_pos[1] - SCREEN_LENGTH // 20), (300, 30)
        )
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        pygame.display.update(text_rect)
        text_surface = font.render(f"Round Bet: {player_bet}", True, TEXT_COLOR)
        screen.blit(
            text_surface,
            (player_stack_pos[0], player_stack_pos[1] - SCREEN_LENGTH // 20),
        )
        pygame.display.flip()

    def display_bot_round_bet(self, bot_bet):
        """Display the bot's round bet.
        Args:
            bot_bet (int): The bot's round bet.
        """
        # Hide the previous bet text
        text_rect = pygame.Rect(
            (bot_stack_pos[0], bot_stack_pos[1] - SCREEN_LENGTH // 20), (300, 30)
        )
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        pygame.display.update(text_rect)

        # Display the new bet text
        text_surface = font.render(f"Round Bet: {bot_bet}", True, TEXT_COLOR)
        screen.blit(
            text_surface,
            (bot_stack_pos[0], bot_stack_pos[1] - SCREEN_LENGTH // 20),
        )

    def display_bot_hand(self, bot_hand):
        """Display the bot's hand.
        Args:
            bot_hand (list): The bot's hand.
        """
        card1 = pygamify_image("cards", f"{bot_hand[0]}.png", CARD_LENGTH, CARD_WIDTH)
        card2 = pygamify_image("cards", f"{bot_hand[1]}.png", CARD_LENGTH, CARD_WIDTH)
        screen.blit(card1, bot_hand_pos_1)
        screen.blit(card2, bot_hand_pos_2)
        pygame.display.flip()

    def display_hidden_bot_hand(self):
        """Display the bot's hand as hidden cards."""
        card1 = pygamify_image("cards", "card back red.png", CARD_LENGTH, CARD_WIDTH)
        card2 = pygamify_image("cards", "card back red.png", CARD_LENGTH, CARD_WIDTH)
        screen.blit(card1, bot_hand_pos_1)
        screen.blit(card2, bot_hand_pos_2)
        pygame.display.flip()

    def render_text_with_outline(
        self, type_font, message, inside_color, outline_color, thickness=2
    ):
        """Render text with an outline.
        Args:
            font (pygame.font.Font): The font to use for rendering.
            message (str): The text to render.
            inside_color (tuple): The color of the text (set as a series
            of three numbers).
            outline_color (tuple): The color of the outline (set as a
            series of three numbers).
            thickness (int): The thickness of the outline.

        Returns:
            outline(pygame.surface): The rendered text surface with an outline.
        """
        base = type_font.render(message, True, inside_color)
        size = thickness * 2 + 1
        outline = pygame.Surface(
            (base.get_width() + size, base.get_height() + size), pygame.SRCALPHA
        )
        for der_x in range(-thickness, thickness + 1):
            for der_y in range(-thickness, thickness + 1):
                if der_x != 0 or der_y != 0:
                    pos = (der_x + thickness, der_y + thickness)
                    outline.blit(type_font.render(message, True, outline_color), pos)
        outline.blit(base, (thickness, thickness))
        return outline

    def display_small_blind(self, position):
        """Display the small blind amount.
        Args:
            position (tuple): The position to display the small blind.
        """
        screen.blit(small_blind, position)
        pygame.display.flip()

    def display_big_blind(self, position):
        """Display the big blind amount.
        Args:
            position (tuple): The position to display the big blind.
        """
        screen.blit(big_blind, position)
        pygame.display.flip()

    def display_start_game_button(self):
        """Display the start game button."""
        start_game_button = pygame.Rect(
            *start_game_button_pos, START_BUTTON_WIDTH, START_BUTTON_LENGTH
        )
        pygame.draw.rect(screen, BUTTON_COLOR, start_game_button)
        text_surface = font.render("Start New Game", True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=start_game_button.center)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def initialize_game_view(
        self, pot, player_hand, player_stack, bot_stack, small_blind_holder
    ):
        """Initialize the game view with the given parameters.
        Args:
            pot (int): The current pot size.
            player_hand (list): The player's hand.
            player_stack (int): The player's stack.
            bot_stack (int): The bot's stack.
            small_blind_holder (str): The player holding the small blind.
        """
        self.display_background()
        self.display_pot(pot)
        self.display_player_hand(player_hand)
        self.display_hidden_bot_hand()
        self.display_call_button()
        self.display_check_button()
        self.display_raise_button()
        self.display_fold_button()
        self.display_player_stack(player_stack)
        self.display_bot_stack(bot_stack)
        if small_blind_holder == "PLAYER":
            self.display_small_blind(player_blind_pos)
            self.display_big_blind(bot_blind_pos)
        else:
            self.display_small_blind(bot_blind_pos)
            self.display_big_blind(player_blind_pos)

    @property
    def action_buttons(self):
        """Get the action buttons for the game.
        Returns:
            dict: The action buttons for the game.
        """
        return self._action_buttons
