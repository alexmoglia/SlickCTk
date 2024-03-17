# pylint: disable=missing-class-docstring, missing-function-docstring


"""
SlickContextMenu is a context-menu based on customtkinter frames and buttons, primarily 
designed for use as a right-click menu. SlickContextMenus automatically account for 
potential monitor DPI scaling, and have two options for handling menu spill (overflow).

Your SlickContextMenu should be initialized within the root widget to ensure the
open_menu() function works as expected; see the docstring in open_menu for more info. 
    
One note: Since these menus are based on CTk Frames, they cannot (to my knowledge) 
exist outside the edge of your app. In other words, an exceptionally long context-menu 
opened in a non-fullscreen app window will not spill out into the empty space around 
your app, but will try to fit inside the app window. An alternative would have been to 
build context-menus from CTk toplevel windows, but the main app window clearly loses 
focus when you do it this way, which I found jarring. Test the programs you use, I've 
found some (like notepad++) have a right-click menu that expands beyond 
the size of the window, but others (like vscode) do not.

TODO
    * Scrollbar in context-menu, appears when too many options for available size
    * Context-menu height & width defaults / mins / maxs
    * > arrow added to submenu strings, justified to right side
    * white space padding on button text
    * focus lost closes main menu, hover off submenu closes submenu 
"""

import tkinter as tk
from typing import Callable, Any
from customtkinter import CTkFrame, CTk
from SlickCTk.slick_buttons import ContextMenuButton, SubmenuButton
from SlickCTk.utilities.dpi_scaler import DPIScaler

from SlickCTk.slick_settings import (
    MENU_COLOR_BACKGROUND,
    MENU_COLOR_OUTLINE,
    MENU_PADDING_X,
    MENU_PADDING_Y,
    MENU_CORNER_RADIUS_ROUNDED,
)

PRINT_DEBUG: bool = False


class SlickContextMenu(CTkFrame):
    def __init__(
        self, parent, menu_choices: dict[str, Callable | dict], **kwargs
    ) -> None:
        super().__init__(
            parent,
            fg_color=MENU_COLOR_BACKGROUND,
            border_color=MENU_COLOR_OUTLINE,
            corner_radius=MENU_CORNER_RADIUS_ROUNDED,
            border_width=1,
            **kwargs,
        )

        self.root: Any = parent
        self.dpi_scaler = DPIScaler()
        self.len_menu_choices: int = len(menu_choices)

        self.menu_subframe = _ContextMenuSubframe(self, self.root, menu_choices)
        self.menu_subframe.pack(
            expand=True,
            fill="both",
            padx=MENU_PADDING_X,
            pady=MENU_PADDING_Y,
        )

        self.descendants: list = self.get_all_descendants(self)

        # self.bind("<Leave>", lambda e: self.check_should_menu_close())
        # self.bind("<FocusIn>", lambda e: print("IN"))
        self.bind("<FocusOut>", lambda e: self.check_should_menu_close())

    def handle_right_click(self, event) -> None:
        """Get the corrected x and y for menu placement and open the menu"""
        x, y = self.calc_menu_position(event.x_root, event.y_root)
        self.open_menu(x, y)

    def calc_menu_position(
        self, x_in: int, y_in: int, menu_depth: int = 1
    ) -> tuple[float, float]:
        """Adjusts input x and y coordinates to open a menu in the right location. When
        this function is called by a mouse click, `x` and `y` should be event.x_root and
        event.y_root. Submenus also use this function, in which case `x` is the main
        menu's x position + its width (in order to offset the submenu), and `y` is the
        submenu button's y position - a small amount (improves UX).

        Quick overview:
            1. Adjust x and y so they are relative to the root widget's position.
            2. Adjust x and y so they are not affected by DPI differences.
            3. Check whether the menu opening in the currently calculated position
                would result in the menu spilling off the window, and handle if so.
            4. Check if the menu is a submenu and offset x appropriately.

        event.x_root, event.y_root:
            The event's x and y coordinates relative to the entire screen (and
            importantly, NOT relative to the parent widget nor the app window). This
            value can't be trusted - it assumes the app is fullscreen. Any window that
            is not fullscreen will return inaccurate event coordinates.

        winfo_rootx(), winfo_rooty():
            Gets the the x and y coordinates of the upper left corner of the specified
            widget relative to it's parent widget.

            SlickContextMenu should be initialized in the root widget (ctk.Ctk), so
            that we can use self.parent.winfo_rootx() in this function to get the upper
            left corner of the root widget itself, ie. the window's (x0, y0)
            coordinates.

        Given the above, we adjust the event x and y coordinates before placing the
        context-menu frame by taking into account the app's window size. We also
        account for possible monitor scaling with the DPIScaler module, and have two
        options for handling menu spill.

        An example, with a non-fullscreen window:

            > Values:
                Screen size:  1920  x  1080
                Window size:  1520  x   780
                Gutter size:   400  x   300  # empty space between window and screen

            > For simplicity, imagine the user requests a context-menu in the top left
            corner of the app
                Expectation: (x, y = 0, 0) # event should be relative to app
                Reality:     (x, y = 200, 200) # event is relative to screensize

                event.x_root, event.y_root = 200, 200

            > To adjust, we can get the x,y coordinates of the upper left corner of the
            root window, and subtract those values from the event coords.

                event.x_root - self.parent.winfo_rootx()
                event.y_root - self.parent.winfo_rooty()

        """

        def __print_debug() -> None:
            if PRINT_DEBUG:
                print("==================================")
                print(f"Window height: {window_height}")
                print(f"Window width:  {window_width}")
                print(f"Context-menu height: {menu_height}")
                print(f"Context-menu width: {menu_width}")
                print(f"Normalized x, y: {normalized_x, normalized_y}")
                print(f"Normalized x end: {normalized_x_end}")
                print(f"Normalized y end: {normalized_y_end}")
                print(f"Normalized x spill: {normalized_x_spill}")
                print(f"Normalized y spill: {normalized_y_spill}")
                print(f"Final x, y: {x, y}")

        submenu_shift: int = 6

        scale_factor: float = self.dpi_scaler.get_scale_factor()

        window_height: int = self.root.winfo_height()
        window_width: int = self.root.winfo_width()

        menu_height: int = self.winfo_height()
        menu_width: int = self.winfo_width()

        root_x: int = self.root.winfo_rootx()
        root_y: int = self.root.winfo_rooty()

        normalized_x: float = (x_in - root_x) / scale_factor
        normalized_y: float = (y_in - root_y) / scale_factor

        normalized_x_end: float = (normalized_x * scale_factor) + menu_width
        normalized_y_end: float = (normalized_y * scale_factor) + menu_height

        normalized_x_spill: float = normalized_x_end - window_width
        normalized_y_spill: float = normalized_y_end - window_height

        x: float = normalized_x
        y: float = normalized_y

        if normalized_y_end > window_height:
            # Adjust the place(x,y) coords if the menu will spill over the edge of the
            # root window. Adjusting by normalized_spill will open the menu as close to
            # the event position, and the edge of the menu will be up against the edge of
            # the window. Adjusting by menu_height will invert the menu so that it opens
            # upwards from the point of origin (or left instead of right, in the case of
            # x). The order of menu items are not changed in either case.

            y = y - (normalized_y_spill / scale_factor)
            # y = y - (menu_height / scale_factor)

        if normalized_x_end > window_width:
            if menu_depth == 1:
                x = x - (menu_width * menu_depth / scale_factor)
                # x = x - (normalized_x_spill / scale_factor)
            elif menu_depth > 1:
                x = x - (menu_width * menu_depth / scale_factor) + submenu_shift
        else:
            if menu_depth > 1:
                x = x - submenu_shift

        if PRINT_DEBUG:
            __print_debug()

        return x, y

    def open_menu(self, x: float, y: float) -> None:
        """Open the SlickContextMenu at the passed coords, and give focus to menu"""
        self.place(x=x, y=y)
        self.focus_set()

    def configure_window(self) -> None:
        self.dpi_scaler.get_dpi_current_monitor()

    def close_menu(self) -> None:
        """Close the SlickContextMenu"""
        self.place_forget()

    def check_should_menu_close(self) -> None:
        """Check if submenu should close. Mouse must be hovering over submenu-button or
        submenu in order to stay open)"""

        print(f"Checking if {self} should close")

        if self.is_any_submenu_hovered():
            pass
        else:
            self.close_menu()

    def is_any_submenu_hovered(self) -> bool:
        """Get the hovered widget's parent (a string representing the tkinter hierarchy
        chain) and return True if the submenu's name is in the hierarchy string.
        Example:
            return ".!slickcontextmenu2" in ".!slickcontextmenu2.!_contextmenusubframe
            .!contextmenubutton"
        """
        hovered_widget = self.get_widget_at_mouse()
        return hovered_widget in self.descendants

    def get_widget_at_mouse(self):
        """Get the mouse's x and y position and find the widget in that position"""
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        return widget

    def get_all_descendants(self, widget) -> list:
        descendants: list = []
        children: list = widget.winfo_children()
        for child in children:
            descendants.append(child)
            # Recurse into child's children with list.extend(func)
            descendants.extend(self.get_all_descendants(child))

        return descendants


class _ContextMenuSubframe(CTkFrame):
    def __init__(self, parent, root: CTk, menu_choices: dict) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        self.parent: SlickContextMenu = parent
        self.root: CTk = root
        self.submenu_is_open = False
        self.process_menu_choices(menu_choices)
        # self.get_widget_at_mouse()

    def process_menu_choices(self, menu_choices: dict) -> None:
        """Iterate through dict and create buttons and submenus"""

        for button_text, button_content in menu_choices.items():
            if isinstance(button_content, Callable):
                self.add_button(button_text, button_content)

            elif isinstance(button_content, dict):
                button: SubmenuButton = self.add_submenu_button(button_text)
                self.add_submenu(button, button_content)

    def add_button(self, button_text: str, button_command: Callable) -> None:
        """Create and place menu button"""
        button = ContextMenuButton(self, text=button_text, command=button_command)
        button.pack(expand=True, fill="both")

    def add_submenu_button(self, button_text: str) -> SubmenuButton:
        """Create and place submenu button"""
        button = SubmenuButton(self, text=button_text, command=None)
        button.pack(expand=True, fill="both")
        return button

    def add_submenu(self, button: SubmenuButton, menu_subitems: dict) -> None:
        """Create submenu and add hover bindings"""

        submenu = SlickContextMenu(self.root, menu_subitems)
        submenu.bind(
            "<Leave>", lambda e: self.check_submenu_should_close(submenu, button)
        )

        button.bind("<Enter>", lambda e: self.submenu_button_hover_in(submenu, button))
        button.bind(
            "<Leave>", lambda e: self.check_submenu_should_close(submenu, button)
        )

    def submenu_button_hover_in(
        self, submenu: SlickContextMenu, button: SubmenuButton
    ) -> None:
        """Hover controls for submenu-hover-buttons (the button in the main main that
        causes a submenu frame to open when the button is hovered over; not the buttons
        in the submenu themselves)"""

        x, y = self.calc_submenu_position(submenu, button)

        submenu.open_menu(x, y)

    def calc_submenu_position(
        self, submenu: SlickContextMenu, button: SubmenuButton
    ) -> tuple[float, float]:
        """Submenus need to be offset so that they don't open on top of the main menu.
        First, we set the inital x position by getting the main menu's rootx position and
        adding it's own width to it, which gives us an x position farther to the right.
        Second, we set the initial y position by finding the y position of the submenu
        button and subtracting a small amount, which gives us a y position farther up.

        Since Submenus are themselves instances of SlickContextMenus, we use the
        calc_menu_position() func to apply more adjustments to the x position. The
        menu_depth argument is used as a multiplier to shift the submenu appropriately
        when there in spill."""

        def __print_debug() -> None:
            print(f"{self.parent.winfo_rootx()=}")
            print(f"{self.parent.winfo_width()=}")

        shift_submenu_x: int = self.parent.winfo_rootx() + self.parent.winfo_width()
        shift_submenu_y: int = button.winfo_rooty() - 10

        if PRINT_DEBUG:
            __print_debug()

        return submenu.calc_menu_position(
            shift_submenu_x, shift_submenu_y, menu_depth=2
        )

    def check_submenu_should_close(
        self, submenu: SlickContextMenu, button: SubmenuButton
    ) -> None:
        """Check if submenu should close. Mouse must be hovering over submenu-button or
        submenu in order to stay open)"""
        if self.is_submenu_button_hovered(button) or self.is_submenu_hovered(submenu):
            pass
        else:
            submenu.close_menu()

    def is_submenu_button_hovered(self, button: SubmenuButton) -> bool:
        """Check if the submenu-button is being hovered over"""
        return self.get_widget_at_mouse() == button

    def is_submenu_hovered(self, submenu: SlickContextMenu) -> bool:
        """Get the hovered widget's parent (a string representing the tkinter hierarchy
        chain) and return True if the submenu's name is in the hierarchy string.
        Example:
            return ".!slickcontextmenu2" in ".!slickcontextmenu2.!_contextmenusubframe
            .!contextmenubutton"
        """

        hovered_widget: str = self.get_widget_at_mouse().winfo_parent()
        return submenu.winfo_name() in hovered_widget

    def get_widget_at_mouse(self) -> tk.Misc:
        """Get the mouse's x and y position and find the widget in that position"""
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)

        if widget is not None:
            return widget
        else:
            return self


if __name__ == "__main__":
    import customtkinter as ctk

    app = ctk.CTk()
    app.title("SlickContextMenu Demo")
    app.geometry("600x400")

    menu_dict: dict[str, Callable | dict] = {
        "Copy": lambda: print("Copy"),
        "Cut": lambda: print("Cut"),
        "Paste": lambda: print("Paste"),
        "Submenu": {
            "Sub-Copy": lambda: print("Sub-Copy"),
            "Sub-Cut": lambda: print("Sub-Cut"),
            "Sub-Paste": lambda: print("Sub-Paste"),
        },
        "Copy1": lambda: print("Copy"),
        "Cut1": lambda: print("Cut"),
        "Paste1": lambda: print("Paste"),
        "Submenu1": {
            "Sub-Copy1": lambda: print("Sub-Copy"),
            "Sub-Cut1": lambda: print("Sub-Cut"),
            "SubSubMenu": {
                "Sub-Copy1": lambda: print("Sub-Copy"),
                "Sub-Cut1": lambda: print("Sub-Cut"),
                "SubSubMenu": {
                    "Sub-Copy1": lambda: print("Sub-Copy"),
                    "Sub-Cut1": lambda: print("Sub-Cut"),
                    "Sub-Paste1": lambda: print("Sub-Paste"),
                },
            },
        },
    }

    menu = SlickContextMenu(app, menu_dict)

    app.bind("<Button-3>", menu.handle_right_click)
    app.bind("<ButtonPress-1>", lambda e: menu.close_menu())
    app.bind("<Configure>", lambda e: menu.configure_window())

    menu.open_menu(0, 0)
    menu.close_menu()

    app.mainloop()

    print("==================================")
