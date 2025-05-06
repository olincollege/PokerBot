"""
Controller file to initialize the controller class for the Poker game.
"""

import pygame
from config import start_game_button_pos, START_BUTTON_WIDTH, START_BUTTON_LENGTH


class Controller:
    """
    Controller class to handle user interactions in the Poker game.

    Attributes:
        start_game_button (pygame.Rect): Rectangle representing the start game button.
        view (PokerView): Instance of the PokerView class to handle UI updates.
    """

    def __init__(self, view):
        """
        Initializes the Controller with a PokerView instance and sets up
        the start game button.

        Args:
            view (PokerView): Instance of the PokerView class.
        """
        self.start_game_button = pygame.Rect(
            *start_game_button_pos, START_BUTTON_WIDTH, START_BUTTON_LENGTH
        )
        self.view = view

    def start_game(self):
        """
        Displays the start game button and waits for user interaction to start the game.

        Returns:
            None
        """
        self.view.display_start_game_button()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_button_clicked(self.start_game_button, event):
                        return
            pygame.display.flip()

    def is_button_clicked(self, rect, event):
        """
        Return True if the given rect is clicked with left mouse button.

        Args:
            rect (pygame.Rect): The rectangle to check for a click.
            event (pygame.event.Event): The event to check.

        Returns:
            bool: True if the rectangle is clicked, False otherwise.
        """
    
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and rect.collidepoint(event.pos)
        )

    def player_action_controller(self):
        """
        Handles player actions by displaying action buttons and waiting for user input.

        Returns:
            action(str): The action chosen by the player (e.g., "fold", "call", "raise").
        """

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for action, rect in self.view.action_buttons.items():
                        if self.is_button_clicked(rect, event):
                            return action
            pygame.display.flip()
