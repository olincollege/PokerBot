import pygame
from player import is_button_clicked
from config import start_game_button_pos, START_BUTTON_WIDTH, START_BUTTON_LENGTH


class Controller:
    def __init__(self, view):
        self.start_game_button = pygame.Rect(
            *start_game_button_pos, START_BUTTON_WIDTH, START_BUTTON_LENGTH
        )
        self.view = view

    def start_game(self):
        self.view.display_start_game_button()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if is_button_clicked(self.start_game_button, event):
                        return
            pygame.display.flip()
        # self.view.display_bot_hand()
