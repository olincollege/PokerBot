from controller import Controller
from model import Model
import pygame

# pygame.init()

model = Model()  # Initialize the model
controller = Controller(model)  # This sets up both model and view internally
controller.start_game()  # This handles model updates and drawing
print(f"cards{model.player_hand}")
clock = pygame.time.Clock()

running = True
while running:
    clock.tick(1)  # Limit the frame rate to 10 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    controller.start_game()  # This handles model updates and drawing

pygame.quit()
