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


pygame.font.init()
font = pygame.font.SysFont(None, 32)
huge_font = pygame.font.SysFont(None, 100)
round_font = pygame.font.SysFont(None, 60)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_LENGTH), pygame.RESIZABLE)


def pygamify_image(subfolder, image_name, height, width):
    """Load an image and convert it to a Pygame surface."""

    return pygame.transform.scale(
        pygame.image.load(os.path.join("assets", subfolder, image_name)),
        (width, height),
    ).convert_alpha()


poker_background = pygamify_image("", "pokertable.jpg", SCREEN_LENGTH, SCREEN_WIDTH)
piggy_bank = pygamify_image("", "piggy_bank.png", PIGGY_LENGTH, PIGGY_WIDTH)


class PokerView:

    def __init__(self, model):
        """ """
        self.model = model
        self.player_hand = self.model.player_hand
        self.bot_hand = self.model.bot_hand
        self.flop = self.model.community_cards[:3]
        self.turn = self.model.community_cards[3:4]
        self.river = self.model.community_cards[4:5]
        self.pot = self.model.pot
        self.chips = self.model.chips
        self.action_buttons = {
            "fold": pygame.Rect(*fold_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
            "check": pygame.Rect(*check_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
            "call": pygame.Rect(*call_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
            "raise": pygame.Rect(*raise_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
        }

    def display_background(self):
        """Display the poker background on the screen."""
        screen.blit(poker_background, (0, 0))
        pygame.display.flip()

    def display_player_hand(self, player_hand):
        """
        Display the player's hand on the screen.
        """
        card1 = pygamify_image(
            "cards", (f"{player_hand[0]}.png"), CARD_LENGTH, CARD_WIDTH
        )
        card2 = pygamify_image(
            "cards", (f"{player_hand[1]}.png"), CARD_LENGTH, CARD_WIDTH
        )
        screen.blit(card1, player_hand_pos_1)
        screen.blit(card2, player_hand_pos_2)
        pygame.display.flip()

    def display_flop(self, flop):
        """
        Display the flop on the screen.
        """
        card1 = pygamify_image("cards", (f"{flop[0]}.png"), CARD_LENGTH, CARD_WIDTH)
        card2 = pygamify_image("cards", (f"{flop[1]}.png"), CARD_LENGTH, CARD_WIDTH)
        card3 = pygamify_image("cards", (f"{flop[2]}.png"), CARD_LENGTH, CARD_WIDTH)
        screen.blit(card1, flop_pos_1)
        screen.blit(card2, flop_pos_2)
        screen.blit(card3, flop_pos_3)
        pygame.display.flip()

    def display_turn(self, turn):
        """
        Display the turn on the screen.
        """
        card = pygamify_image("cards", (f"{turn[0]}.png"), CARD_LENGTH, CARD_WIDTH)
        screen.blit(card, turn_pos)
        pygame.display.flip()

    def display_river(self, river):
        """
        Display the river on the screen.
        """
        card = pygamify_image("cards", (f"{river[0]}.png"), CARD_LENGTH, CARD_WIDTH)
        screen.blit(card, river_pos)
        pygame.display.flip()

    def display_fold_button(self):
        """
        Display the fold button on the screen with centered text.
        """
        fold_rect = self.action_buttons["fold"]

        # Draw the button background
        pygame.draw.rect(screen, BUTTON_COLOR, fold_rect)

        # Render the text
        text_surface = font.render("Fold", True, TEXT_COLOR)

        # Center the text inside the button
        text_rect = text_surface.get_rect(center=fold_rect.center)

        # Blit the text
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_check_button(self):
        """
        Display the check button on the screen with centered text.
        """
        check_rect = self.action_buttons["check"]

        # Draw the button background
        pygame.draw.rect(screen, BUTTON_COLOR, check_rect)

        # Render the text
        text_surface = font.render("Check", True, TEXT_COLOR)

        # Center the text inside the button
        text_rect = text_surface.get_rect(center=check_rect.center)

        # Blit the text
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_call_button(self):
        """
        Display the call button on the screen with centered text.
        """
        call_rect = self.action_buttons["call"]

        # Draw the button background
        pygame.draw.rect(screen, BUTTON_COLOR, call_rect)

        # Render the text
        text_surface = font.render("Call", True, TEXT_COLOR)

        # Center the text inside the button
        text_rect = text_surface.get_rect(center=call_rect.center)

        # Blit the text
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_raise_button(self):
        """
        Display the raise button on the screen with centered text.
        """
        raise_rect = self.action_buttons["raise"]

        # Draw the button background
        pygame.draw.rect(screen, BUTTON_COLOR, raise_rect)

        # Render the text
        text_surface = font.render("Raise", True, TEXT_COLOR)

        # Center the text inside the button
        text_rect = text_surface.get_rect(center=raise_rect.center)

        # Blit the text
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_bot_stack(self, bot_stack):
        """
        Display the bot's stack on the screen.
        """
        text_rect = pygame.Rect(
            bot_stack_pos, (300, 30)
        )  # Adjust width & height if needed
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        pygame.display.update(text_rect)
        text_surface = font.render(f"Bot Stack: {bot_stack}", True, TEXT_COLOR)
        screen.blit(text_surface, bot_stack_pos)
        pygame.display.flip()

    def display_player_stack(self, player_stack):
        """
        Display the bot's stack on the screen.
        """
        text_rect = pygame.Rect(
            player_stack_pos, (300, 30)
        )  # Adjust width & height if needed
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        pygame.display.update(text_rect)
        text_surface = font.render(f"Player Stack: {player_stack}", True, TEXT_COLOR)
        screen.blit(text_surface, player_stack_pos)
        pygame.display.flip()

    def display_bot_decision(self, decision, poker_stage, raise_amount=None):
        """
        Display the bot's decision on the screen.
        """
        text_rect = pygame.Rect(
            bot_decision_pos, (390, 30)
        )  # Adjust width & height if needed
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
        """
        Display the invalid text on the screen.
        """
        text_surface = huge_font.render(
            "THAT MOVE IS INVALID BRO, LEARN POKER", True, TEXT_COLOR
        )
        screen.blit(text_surface, invalid_text_pos)
        pygame.display.flip()

    def hide_invalid_text(self):
        """
        Hide the invalid text on the screen.
        """
        text_rect = pygame.Rect(
            invalid_text_pos, (SCREEN_WIDTH * 0.9, 100)
        )  # Adjust width & height if needed
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        pygame.display.update(text_rect)
        self.display_hidden_bot_hand()

    def display_pot(self, pot):
        """
        Display the pot on the screen, clearing the previous display first.
        """

        # Redraw the background portion where the pot is shown
        text_rect = pygame.Rect(
            invalid_text_pos, (PIGGY_WIDTH, PIGGY_LENGTH)
        )  # Adjust width & height if needed
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)

        screen.blit(piggy_bank, pot_pos)
        text_surface = font.render(f"Pot: {pot}", True, BLACK_COLOR)
        screen.blit(text_surface, (pot_pos[0] + 50, pot_pos[1] + 80))
        pygame.display.flip()

    def display_round(self, poker_round):
        """
        Display the round on the screen.
        """
        text_rect = pygame.Rect(
            display_round_pos, (SCREEN_WIDTH * 0.25, 50)
        )  # Adjust width & height if needed
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        text_surface = round_font.render(f"Round: {poker_round}", True, TEXT_COLOR)
        screen.blit(text_surface, display_round_pos)
        pygame.display.flip()

    def display_winner(self, winner):
        """
        Display the winner on the screen.
        """
        self.hide_invalid_text()

        text_surface = self.render_text_with_outline(
            huge_font, f"{winner} WINS!", BLACK_COLOR, GREEN_COLOR
        )
        text_rect = text_surface.get_rect(center=display_winner_pos)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_showdown(self):
        """
        Display the showdown on the screen.
        """
        text_surface = huge_font.render("SHOWDOWN", True, DARK_RED_COLOR)
        text_rect = text_surface.get_rect(center=display_showdown_pos)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def display_player_round_bet(self, player_bet):
        """
        Display the player's round bet on the screen.
        """
        text_rect = pygame.Rect(
            (player_stack_pos[0], player_stack_pos[1] - SCREEN_LENGTH // 20), (300, 30)
        )  # Adjust width & height if needed
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
        """
        Display the bot's round bet on the screen.
        """
        text_rect = pygame.Rect(
            (bot_stack_pos[0], bot_stack_pos[1] - SCREEN_LENGTH // 20), (300, 30)
        )
        background_crop = poker_background.subsurface(text_rect)
        screen.blit(background_crop, text_rect)
        pygame.display.update(text_rect)
        text_surface = font.render(f"Round Bet: {bot_bet}", True, TEXT_COLOR)
        screen.blit(
            text_surface,
            (bot_stack_pos[0], bot_stack_pos[1] - SCREEN_LENGTH // 20),
        )

    def display_bot_hand(self, bot_hand):
        """
        Display the bot's hand on the screen.
        """
        card1 = pygamify_image("cards", (f"{bot_hand[0]}.png"), CARD_LENGTH, CARD_WIDTH)
        card2 = pygamify_image("cards", (f"{bot_hand[1]}.png"), CARD_LENGTH, CARD_WIDTH)
        screen.blit(card1, bot_hand_pos_1)
        screen.blit(card2, bot_hand_pos_2)
        pygame.display.flip()

    def display_hidden_bot_hand(self):
        """
        Display the bot's hand on the screen.
        """
        card1 = pygamify_image("cards", "card back red.png", CARD_LENGTH, CARD_WIDTH)
        card2 = pygamify_image("cards", "card back red.png", CARD_LENGTH, CARD_WIDTH)
        screen.blit(card1, bot_hand_pos_1)
        screen.blit(card2, bot_hand_pos_2)
        pygame.display.flip()

    def render_text_with_outline(self, font, message, inside_color, outline_color):
        base = font.render(message, True, inside_color)
        outline = pygame.Surface(
            (base.get_width() + 2, base.get_height() + 2), pygame.SRCALPHA
        )

        # Draw outline by rendering the text in 8 surrounding positions
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    pos = (dx + 1, dy + 1)
                    outline.blit(font.render(message, True, outline_color), pos)

        # Draw the main text centered
        outline.blit(base, (1, 1))
        return outline
