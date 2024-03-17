# pylint: disable=missing-module-docstring,

from SlickCTk.utilities.digsby.load_custom_font import load_font

load_font("./src/SlickCTk/resources/fonts/Nunito-Bold.ttf")

# TEXT
FONT = "Calibri"
TEXT_SIZE_TITLE = 40
TEXT_SIZE_PATH = 14

# PRIMARY / SHARED VARIABLES
COLOR_MAIN_ONE = "#1f1f1f"  # treeview headers, frames
COLOR_MAIN_TWO = "#181818"  # # app bg, menu bg
COLOR_MAIN_THREE = "#272727"  # treeview bg, email buttons
COLOR_ACCENT = "#3574b2"  # hover, row select, scrollbar (BLUE)
COLOR_ACCENT = "#8b0000"  # hover, row select, scrollbar (RED)
COLOR_ACCENT = "#372747"  # hover, row select, scrollbar (BLUE)
COLOR_ACCENT = "#04395e"  # hover, row select, scrollbar (BLUE)
COLOR_ACCENT_TWO = "#570000"  # row select no focus (RED)
COLOR_ACCENT_TWO = "#1e4265"  # row select no focus (BLUE)
COLOR_ACCENT_TWO = "#b05200"  # row select no focus (BLUE)
COLOR_OUTLINES = "#313131"  # outlines, placeholder text
COLOR_TEXT = "#ffffff"

COLOR_APP_BACKGROUND = COLOR_MAIN_ONE

# FRAMES
# FRAME_PADDING_MAIN_SQUARE = 30
FRAME_PADDING = 5
FRAME_BORDER_WIDTH = 1

# CONTEXT MENU - Right-Click Menu
MENU_COLOR_BACKGROUND = COLOR_MAIN_ONE
MENU_COLOR_HOVER = COLOR_ACCENT
MENU_COLOR_OUTLINE = COLOR_OUTLINES

MENU_BUTTON_COLOR_BACKGROUND = "transparent"
MENU_BUTTON_COLOR_HOVER = COLOR_ACCENT
MENU_BUTTON_CORNER_RADIUS = 4

MENU_PADDING_X = 4
MENU_PADDING_Y = 4
MENU_CORNER_RADIUS_0 = 0
MENU_CORNER_RADIUS_ROUNDED = 6

# BUTTONS
BUTTON_COLOR_TEXT = COLOR_TEXT
BUTTON_COLOR_BACKGROUND = COLOR_MAIN_THREE
BUTTON_COLOR_HOVER = COLOR_ACCENT

BUTTON_ACTION_WIDTH = 220
BUTTON_ACTION_HEIGHT = 145
BUTTON_CORNER_RADIUS = 2

# SCROLLBAR
SCROLLBAR_COLOR_BACKGROUND = COLOR_MAIN_THREE
SCROLLBAR_COLOR_BUTTON = COLOR_MAIN_TWO
SCROLLBAR_COLOR_BUTTON_HOVER = COLOR_ACCENT

# SEARCH - Search Bar
SEARCHBAR_COLOR_PLACEHOLDER = "#7a7870"
SEARCHBAR_COLOR_OUTLINE = "#454545"
SEARCHBAR_COLOR_BACKGROUND = COLOR_MAIN_THREE
SEARCHBAR_COLOR_OUTLINE_FOCUS = COLOR_ACCENT

# SEARCHBAR_FONT = ("Helvetica", 12)
# SEARCHBAR_FONT = ("Consolas", 14)
# SEARCHBAR_FONT = ("monospace", 13)
SEARCHBAR_FONT = ("Nunito Bold", 13)

SEARCHBAR_X_FONT = "Nunito Bold"


# TREEVIEW - Shared
TREEVIEW_COLOR_TEXT = COLOR_TEXT
TREEVIEW_COLOR_HEADING = COLOR_MAIN_TWO
TREEVIEW_COLOR_ROW_BACKGROUND = COLOR_MAIN_THREE
TREEVIEW_COLOR_ROW_SELECTED = COLOR_ACCENT
TREEVIEW_COLOR_ROW_SELECTED_FOCUS_LOST = COLOR_ACCENT_TWO

TREEVIEW_FONT_HEADING = "System"
TREEVIEW_FONT_ROW = "System"

# TREEVIEW - Search Results
SEARCH_RESULTS_MAX_ROWS = 10
SEARCH_RESULTS_MIN_ROWS = 3
SEARCH_RESULTS_ROW_HEIGHT = 25

TREEVIEW_FONT_SIZE_HEADING = 10
SEARCH_RESULTS_FONT_SIZE = 10

# TREEVIEW - Selected User Tree
COLOR_TREEVIEW_SELECTED_USER_LABELS = (
    COLOR_MAIN_TWO  # color for labels (left part) of SelectedUserTreeview
)

FONT_SIZE_SELECTED_USER = 13

# Window Titlebar (title-hex)
COLOR_LIGHT_TITLEBAR = 0x003CECEC
COLOR_DARK_TITLEBAR = 0x001F1F1F
