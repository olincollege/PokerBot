import pygame

PLAYER_NAME = "PLAYER"
STARTING_STACK = 10000
SMALL_BLIND = 25
BIG_BLIND = 50

SCREEN_WIDTH = 1700
SCREEN_LENGTH = 900
CARD_WIDTH = SCREEN_WIDTH / 18
CARD_LENGTH = SCREEN_LENGTH / 7
CARD_SPACING = SCREEN_WIDTH / 110
BUTTON_WIDTH = SCREEN_WIDTH / 10
BUTTON_LENGTH = SCREEN_LENGTH / 10
BUTTON_COLOR = (139, 0, 0)
TEXT_COLOR = (211, 211, 211)
BLACK_COLOR = (0, 0, 0)
PIGGY_WIDTH = SCREEN_LENGTH / 5
PIGGY_LENGTH = SCREEN_LENGTH / 5


player_hand_pos_1 = (
    SCREEN_WIDTH // 2 - CARD_WIDTH - CARD_SPACING,
    SCREEN_LENGTH - CARD_LENGTH * 1.6,
)
player_hand_pos_2 = (
    SCREEN_WIDTH // 2 + CARD_SPACING,
    SCREEN_LENGTH - CARD_LENGTH * 1.6,
)
bot_hand_pos_1 = (
    SCREEN_WIDTH // 2 - CARD_WIDTH - CARD_SPACING,
    CARD_LENGTH * 1.6 - CARD_LENGTH,
)
bot_hand_pos_2 = (SCREEN_WIDTH // 2 + CARD_SPACING, CARD_LENGTH * 1.6 - CARD_LENGTH)

flop_pos_1 = (
    SCREEN_WIDTH // 2 - CARD_WIDTH * 2.5 - 2 * CARD_SPACING,
    SCREEN_LENGTH // 2 - CARD_LENGTH // 2,
)
flop_pos_2 = (
    SCREEN_WIDTH // 2 - CARD_WIDTH * 1.5 - CARD_SPACING,
    SCREEN_LENGTH // 2 - CARD_LENGTH // 2,
)
flop_pos_3 = (
    SCREEN_WIDTH // 2 - CARD_WIDTH // 2,
    SCREEN_LENGTH // 2 - CARD_LENGTH // 2,
)
turn_pos = (
    SCREEN_WIDTH // 2 + CARD_WIDTH // 2 + CARD_SPACING,
    SCREEN_LENGTH // 2 - CARD_LENGTH // 2,
)
river_pos = (
    SCREEN_WIDTH // 2 + 1.5 * CARD_WIDTH + 2 * CARD_SPACING,
    SCREEN_LENGTH // 2 - CARD_LENGTH // 2,
)
pot_pos = (SCREEN_WIDTH - 100, SCREEN_LENGTH - 200)

fold_button_pos = (SCREEN_WIDTH - BUTTON_WIDTH * 1.5, SCREEN_LENGTH - BUTTON_LENGTH * 6)
raise_button_pos = (
    SCREEN_WIDTH - BUTTON_WIDTH * 1.5,
    SCREEN_LENGTH - BUTTON_LENGTH * 4.5,
)
call_button_pos = (SCREEN_WIDTH - BUTTON_WIDTH * 1.5, SCREEN_LENGTH - BUTTON_LENGTH * 3)
check_button_pos = (
    SCREEN_WIDTH - BUTTON_WIDTH * 1.5,
    SCREEN_LENGTH - BUTTON_LENGTH * 1.5,
)
player_stack_pos = (SCREEN_WIDTH // 10, SCREEN_LENGTH // 1.1)
bot_stack_pos = (SCREEN_WIDTH // 10, SCREEN_LENGTH // 10)
bot_decision_pos = (SCREEN_WIDTH // 1.3, SCREEN_LENGTH // 10)
invalid_text_pos = (SCREEN_WIDTH // 20, SCREEN_LENGTH // 5)
pot_pos = (SCREEN_WIDTH // 2 - PIGGY_WIDTH // 2, SCREEN_LENGTH // 1.75)
display_round_pos = (SCREEN_WIDTH // 2.4, SCREEN_LENGTH // 14)
display_winner_pos = (SCREEN_WIDTH // 2.4, SCREEN_LENGTH // 2)
display_showdown_pos = invalid_text_pos


action_buttons = {
    "fold": pygame.Rect(*fold_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
    "check": pygame.Rect(*check_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
    "call": pygame.Rect(*call_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
    "raise": pygame.Rect(*raise_button_pos, BUTTON_WIDTH, BUTTON_LENGTH),
}
