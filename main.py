"""Main function initializing pygame and running the game loop"""

import sys
from time import sleep
import pygame

from model import Model
from view import PokerView


model = Model()  # Initialize the model
view = PokerView(model)  # Initialize the view with the model
clock = pygame.time.Clock()

# Initialize pygame
while True:
    clock.tick(1)  # Limit the frame rate to 1 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    view.display_loading_screen()
    sleep(3)  # Simulate loading time
    model.run()  # This handles model updates and drawing
