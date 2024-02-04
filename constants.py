import yaml

SIZE_BOARD = None
NUMBER_OF_LINES_OF_DOTS_IN_START = None
PLAYER_1_COLOR = None
PLAYER_2_COLOR = None

try:
    with open('settings_server.yaml', 'r') as yaml_file:
        settings_server = yaml.safe_load(yaml_file)
        SIZE_BOARD = settings_server['SIZE_BOARD']
        NUMBER_OF_LINES_OF_DOTS_IN_START = settings_server['NUMBER_OF_LINES_OF_DOTS_IN_START']
        PLAYER_1_COLOR = settings_server['PLAYER_1_COLOR']
        PLAYER_2_COLOR = settings_server['PLAYER_2_COLOR']
        PORT = settings_server['PORT']
        IP_ADDRESS_SERVER = settings_server['IP_ADDRESS_SERVER']

except FileNotFoundError:
    print("settings server not here")
    pass

try:
    # Load the settings_server from the YAML file
    with open('settings_client.yaml', 'r') as yaml_file:
        settings_client = yaml.safe_load(yaml_file)
        IP_ADDRESS_CLIENT = settings_client['IP_ADDRESS_CLIENT']
        PORT = settings_client['PORT']
except FileNotFoundError:
    print("settings client not here")
    pass

try:
    with open('settings.yaml', 'r') as yaml_file:
        settings = yaml.safe_load(yaml_file)
        SIZE_BOARD = settings['SIZE_BOARD']
        NUMBER_OF_LINES_OF_DOTS_IN_START = settings['NUMBER_OF_LINES_OF_DOTS_IN_START']
        PLAYER_1_COLOR = settings['PLAYER_1_COLOR']
        PLAYER_2_COLOR = settings['PLAYER_2_COLOR']

except FileNotFoundError:
    print("settings  not here")
    pass

WIDTH = 1500
HEIGHT = 800
WHITE = (255, 255, 255)
GREY = (112, 112, 112)
BLACK = (0, 0, 0)
BROWN = (150, 75, 0)
RED = (255, 0, 0)
MARGIN = 60
BOARD_LINE_WIDTH = 3
BOARD_COLOR = BLACK
PLAYER_1_COLOR_SELECTED = (153, 204, 255)
PLAYER_2_COLOR_SELECTED = (255, 153, 253)
UP_DIRECTION = "UP"
DOWN_DIRECTION = "DOWN"
PLAYER_1_DIRECTION = UP_DIRECTION
PLAYER_2_DIRECTION = DOWN_DIRECTION
CROWN_PATH = "assets\\images\\crown.png"

UP_LEFT = (MARGIN, MARGIN)
DOWN_RIGHT = (min(WIDTH, HEIGHT) - MARGIN, min(WIDTH, HEIGHT) - MARGIN)
if SIZE_BOARD:
    SQUARE_SIZE = (DOWN_RIGHT[0] - UP_LEFT[0]) / SIZE_BOARD
