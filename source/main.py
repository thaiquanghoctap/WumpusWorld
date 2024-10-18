import graphics
import sys
import pygame
from pygame.locals import *

# Initialize pygame
pygame.init()

# Create the display surface
menu_screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Wumpus World's Maps")

# Set up colors and fonts
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
FONT = pygame.font.Font(None, 36)

# Menu options
options = ["map1", "map2", "map3", "map4", "map5", "map6"]

# Game loop
selected_map = 0
running = True


def draw_menu(screen, font, option, x, y, width, height, is_selected):
    button_color = (200, 200, 200) if is_selected else (255, 255, 255)
    
    pygame.draw.rect(screen, button_color, (x, y, width, height))
    pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height), 2)  # Border

    text_surface = font.render(option, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN:
            if event.key == K_UP:
                selected_map = (selected_map - 1) % len(options)
            elif event.key == K_DOWN:
                selected_map = (selected_map + 1) % len(options)
            elif event.key == K_RETURN:
                while running:
                    map_name = options[selected_map] + ".txt"
                    board = graphics.implement(map_name)
    # screen fill
    menu_screen.fill((255, 255, 255))
    # Draw menu options
    for i, option in enumerate(options):
        is_selected = (i == selected_map)
        draw_menu(menu_screen, FONT, option, 100, 100 + i * 60, 400, 50, is_selected)
    pygame.display.flip()

# Clean up and quit pygame after the game loop exits
pygame.quit()
sys.exit()
