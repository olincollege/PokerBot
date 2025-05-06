from config import action_buttons
import pygame


def is_button_clicked(rect, event):
    """
    Return True if the given rect is clicked with left mouse button.
    """
    return (
        event.type == pygame.MOUSEBUTTONDOWN
        and event.button == 1  # Left click
        and rect.collidepoint(event.pos)
    )


def player_action_controller(self):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for action, rect in self.view.action_buttons.items():
                    if is_button_clicked(rect, event):
                        return action
        pygame.display.flip()
