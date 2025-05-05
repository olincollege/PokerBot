from controller import Controller
from model import Model
from view import PokerView
from time import sleep
import pygame

# pygame.init()

model = Model()  # Initialize the model
view = PokerView(model)  # Initialize the view with the model
print(f"cards{model.player_hand}")
clock = pygame.time.Clock()

running = True
while running:
    clock.tick(1)  # Limit the frame rate to 1 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    view.display_loading_screen()
    sleep(5)  # Simulate loading time
    model.run()  # This handles model updates and drawing

pygame.quit()
