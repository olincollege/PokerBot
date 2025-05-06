"""Main function initializing pygame and running the game loop"""

from time import sleep
import pygame

from model import Model
from view import PokerView


model = Model()  # Initialize the model
view = PokerView(model)  # Initialize the view with the model
clock = pygame.time.Clock()

running = True
while running:
    clock.tick(1)  # Limit the frame rate to 1 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    view.display_loading_screen()
    sleep(3)  # Simulate loading time
    model.run()  # This handles model updates and drawing

pygame.quit()
