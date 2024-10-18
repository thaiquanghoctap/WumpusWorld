import pygame
import sys
import world
import os.path

# Define constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

MAP_BOARD_WIDTH = 500
MAP_BOARD_HEIGHT = 500

STEP_BOARD_WIDTH = 500

STEP_BOARD_HEIGHT = 600  # HERE

OUTPUT_BOARD_WIDTH = 500
OUTPUT_BOARD_HEIGHT = 150

BORDER_WIDTH = 1

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = WHITE
BUTTON_HOVER_COLOR = (0, 200, 0)

# Define text
FONT_SIZE = 24
TEXT_COLOR = BLACK

# Define world
wumpus_world = world.WumpusWorld()


class GameWindow:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Create the main window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Wumpus World")

        self.icon_image = pygame.image.load('../assets/wumpus.png')
        # self.running = True

        self.map_board = World(self.screen,
                               0, 0, MAP_BOARD_WIDTH, MAP_BOARD_HEIGHT + 100, BORDER_WIDTH, wumpus_world)
        self.kb_board = GameBoard(self.screen,
                                  MAP_BOARD_WIDTH, 50, STEP_BOARD_WIDTH, STEP_BOARD_HEIGHT, BORDER_WIDTH)
        wumpus_world.setKBBoard(self.kb_board)

        self.output_board = GameBoard(self.screen,
                                      MAP_BOARD_WIDTH, STEP_BOARD_HEIGHT + 50, OUTPUT_BOARD_WIDTH, OUTPUT_BOARD_HEIGHT,
                                      BORDER_WIDTH)
        self.score_board = GameBoard(self.screen,
                                     0, MAP_BOARD_HEIGHT, 500, 100, BORDER_WIDTH)

        self.step_button = Button(self.screen,
                                  MAP_BOARD_WIDTH, 0, 500, 50, BORDER_WIDTH,
                                  'STEP', BLACK, FONT_SIZE)

        self.kb_board.enable_scroll()

    def set_icon(self):
        pygame.display.set_icon(self.icon_image)

    def run_game(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    wumpus_world.clearWorld()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if self.step_button.check_button_click(event.pos):
                            wumpus_world.findNextMove()

                    elif event.button == 4:  # Scroll up
                        self.kb_board.scroll_position = max(0, self.kb_board.scroll_position - 20)
                        # print('Scrollbar up!')
                        self.kb_board.show_scrollbar = True
                    elif event.button == 5:  # Scroll down
                        self.kb_board.scroll_position = min(self.kb_board.height - self.kb_board.scrollbar_width,
                                                            self.kb_board.scroll_position + 20)
                        # print('Scrollbar down!')
                        self.kb_board.show_scrollbar = True

            # Clear the screen
            self.screen.fill(BLACK)

            self.map_board.draw_board(WHITE, BLACK)
            self.kb_board.draw_board(WHITE, BLACK)
            self.step_button.draw_button(WHITE, BLACK)

            # Draw the visible portion of the kb_board based on scroll position
            pygame.draw.rect(self.kb_board.screen, WHITE, (
                self.kb_board.rect.x, self.kb_board.rect.y - self.kb_board.scroll_position,
                self.kb_board.rect.width, self.kb_board.rect.height)
                             )

            # Draw the scrollbar and get its rect for handling click events
            if self.kb_board.show_scrollbar:
                scrollbar_rect = self.kb_board.create_scrollbar()
            self.kb_board.draw_content()

            self.map_board.generateWorld()

            # Display score
            image = pygame.image.load(self.map_board.SCORE)
            self.screen.blit(image, (75, 530))

            self.map_board.write_text(x=50, y=550, text=str(wumpus_world.agent.score))

            # Update the display
            pygame.display.flip()
            # wumpus_world.findNextMove()

            clock.tick(60)


class GameBoard:
    def __init__(self, screen, x, y, width, height, border_width=BORDER_WIDTH,
                 text_color=BLACK, font_size=FONT_SIZE):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.height = self.rect.height
        self.width = self.rect.width
        self.content = ''
        self.border_width = border_width

        self.scrollbar_width = 20
        self.scrollable = False
        self.scroll_position = 0
        self.scroll_speed = 20
        self.max_scroll = 0  # This will be updated based on content height

        self.show_scrollbar = False  # Flag to indicate whether the scrollbar should be visible

        self.text_color = text_color
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)

    def draw_content(self):
        # Clear the kb_board
        pygame.draw.rect(self.screen, WHITE, (
            self.rect.x, self.rect.y, self.rect.width, self.rect.height))

        # Split the content into lines
        lines = self.content.split('\n')

        # Draw each line of the content
        line_height = self.font.get_linesize()
        total_height = len(lines) * line_height

        # Adjust the scroll position to stay within bounds
        if self.scroll_position > 0:
            self.scroll_position = min(self.scroll_position, total_height - self.rect.height)
        else:
            self.scroll_position = 0

        # Draw each visible line
        for i, line in enumerate(lines):
            if line_height * i - self.scroll_position < self.rect.height:
                text_surface = self.font.render(line, True, self.text_color)
                # Draw the visible portion to the screen
                text_rect = text_surface.get_rect(
                    topleft=(self.rect.x + 10, (self.rect.y + line_height * i - self.scroll_position) + 10))
                self.screen.blit(text_surface, text_rect)

            # Check if horizontal scrollbar is needed
        total_width = max([self.font.size(line)[0] for line in lines])
        if total_width > self.rect.width:
            # Draw the horizontal scrollbar
            self.draw_horizontal_scrollbar(total_width)

    def draw_horizontal_scrollbar(self, total_width):
        # Calculate scrollbar position and dimensions
        scrollbar_height = 10
        scrollbar_y = self.rect.y + self.rect.height - scrollbar_height
        scrollbar_x = self.rect.x
        scrollbar_width = self.rect.width

        # Draw the scrollbar
        pygame.draw.rect(self.screen, (200, 200, 200), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))

        # Calculate the position of the scrollbar thumb
        thumb_width = (self.rect.width / total_width) * scrollbar_width
        thumb_x = (self.scroll_position / (total_width - self.rect.width)) * (scrollbar_width - thumb_width)

        # Draw the scrollbar thumb
        pygame.draw.rect(self.screen, (100, 100, 100),
                         (scrollbar_x + thumb_x, scrollbar_y, thumb_width, scrollbar_height))

    def update_content(self, content):
        self.content = content + '\n'
        self.max_scroll = max(0, self.get_content_height() - self.height)

    def get_content_height(self):
        text_surface = self.font.render(self.content, True, self.text_color)
        return text_surface.get_rect().height

    def enable_scroll(self):
        self.scrollable = True

    def disable_scroll(self):
        self.scrollable = False

        # Add the following method to handle scrolling

    def scroll(self, direction):
        if self.scrollable:
            if direction == "up":
                self.scroll_position = max(0, self.scroll_position - self.scroll_speed)
            elif direction == "down":
                self.scroll_position = min(self.max_scroll, self.scroll_position + self.scroll_speed)

    def update_scroll_position(self, new_position):
        self.scroll_position = new_position

    def draw_board(self, board_color, border_color=None):
        pygame.draw.rect(self.screen, WHITE, self.rect)
        pygame.draw.rect(self.screen, BLACK, self.rect, self.border_width)
        if self.scrollable:
            # Draw the visible portion of the board based on scroll position
            pygame.draw.rect(self.screen, WHITE,
                             (self.rect.x, self.rect.y - self.scroll_position, self.rect.width, self.rect.height))

            # Draw the scrollbar and get its rect for handling click events
        if self.show_scrollbar:
            scrollbar_rect = self.create_scrollbar()

    def create_scrollbar(self):
        scrollbar_rect = pygame.Rect(self.width - self.scrollbar_width, 0, self.scrollbar_width, self.height)
        pygame.draw.rect(self.screen, BLACK, scrollbar_rect)
        return scrollbar_rect

    def write_text(self, x, y, text=""):
        # Render and draw text
        text_surface = self.font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)


class Button(GameBoard):
    def __init__(self, screen, x, y, width, height, border_width=BORDER_WIDTH,
                 text="", text_color=BLACK, font_size=FONT_SIZE):
        super().__init__(screen, x, y, width, height, border_width)
        self.text = text
        self.text_color = text_color
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)

    def draw_button(self, button_color, border_color=None):
        super().draw_board(button_color, border_color)

        # Render and draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

    def check_button_click(self, pos):
        return self.rect.collidepoint(pos)


class World(GameBoard):
    def __init__(self, screen, x, y, width, height, border_width=BORDER_WIDTH, world=wumpus_world):
        super().__init__(screen, x, y, width, height, border_width)
        self.world = world

        # define grid size
        self.GRID_SIZE = 50
        self.GRID_HEIGHT, self.GRID_WIDTH = MAP_BOARD_HEIGHT // self.GRID_SIZE, MAP_BOARD_WIDTH // self.GRID_SIZE

        self.tiles = self.world.listTiles

        # Image Paths
        self.DOOR = '../assets/door.png'
        self.TILE = '../assets/floor.png'
        self.FLOOR_GOLD = '../assets/floor_gold.png'
        self.FLOOR = '../assets/floor.png'
        self.CEIL = '../assets/ceil.png'
        self.WUMPUS = '../assets/wumpus.png'
        self.GOLD = '../assets/gold.png'
        self.PIT = '../assets/pit.png'
        self.STENCH = '../assets/stench.png'
        self.TERRAIN = '../assets/terrain.png'
        self.AGENT_DOWN = '../assets/agent_down.png'
        self.AGENT_UP = '../assets/agent_up.png'
        self.AGENT_LEFT = '../assets/agent_left.png'
        self.AGENT_RIGHT = '../assets/agent_right.png'
        self.SCORE = '../assets/score_icon.png'

    def draw_image(self, image_path, rect):
        image = pygame.image.load(image_path)
        scaled_image = self.fit_image(image)
        self.screen.blit(scaled_image, rect.topleft)

    def fit_image(self, image):
        return pygame.transform.scale(image, (self.GRID_SIZE, self.GRID_SIZE))

    def generateWorld(self):
        for x in range(self.GRID_WIDTH):
            for y in range(self.GRID_HEIGHT):
                rect = pygame.draw.rect(self.screen, BLACK,
                                        (x * self.GRID_SIZE, y * self.GRID_SIZE,
                                         self.GRID_SIZE, self.GRID_SIZE), 1)

                font = pygame.font.Font(None, 12)
                self.draw_image(self.TERRAIN, rect)
                if self.tiles[y][x].getPit():
                    self.draw_image(self.PIT, rect)

                if self.tiles[y][x].getWumpus():
                    self.draw_image(self.WUMPUS, rect)

                if self.tiles[y][x].getGold():
                    self.draw_image(self.FLOOR_GOLD, rect)
                    self.draw_image(self.GOLD, rect)

                if self.tiles[y][x].getStench():
                    self.draw_image(self.STENCH, rect)

                if self.tiles[y][x].getBreeze() and not self.tiles[y][x].getPit():
                    text_surface = font.render('Breeze', True, WHITE)
                    text_rect = text_surface.get_rect(center=rect.center)
                    self.screen.blit(text_surface, text_rect)

                if y == wumpus_world.doorPos[0] and x == wumpus_world.doorPos[1]:
                    self.draw_image(self.DOOR, rect)

                if self.tiles[y][x].getAgent():
                    if wumpus_world.agent.face == 'R':
                        self.draw_image(self.AGENT_RIGHT, rect)
                    elif wumpus_world.agent.face == 'L':
                        self.draw_image(self.AGENT_LEFT, rect)
                    elif wumpus_world.agent.face == 'U':
                        self.draw_image(self.AGENT_UP, rect)
                    elif wumpus_world.agent.face == 'D':
                        self.draw_image(self.AGENT_DOWN, rect)

                if not self.tiles[y][x].getExplored():
                    self.draw_image(self.CEIL, rect)


def implement(map_name):
    # read map
    if os.path.isfile('../input/' + map_name):
        wumpus_world.readMap('../input/' + map_name)

    game_window = GameWindow()
    game_window.set_icon()

    game_window.run_game()
