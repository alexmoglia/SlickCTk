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
    * wrapper for funcs in menu_choices to handle closing menus when button clicked
    * set submen-button color to hover color when submenu open (right now it reverts to non-hovered color when you enter the submenu)
"""

import tkinter as tk
from typing import Callable
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
        self,
        parent,
        menu_choices: dict[str, Callable | dict[str, Callable | dict]],
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            fg_color=MENU_COLOR_BACKGROUND,
            border_color=MENU_COLOR_OUTLINE,
            corner_radius=MENU_CORNER_RADIUS_ROUNDED,
            border_width=1,
            **kwargs,
        )

        self.root: CTk = parent
        self.dpi_scaler: DPIScaler = DPIScaler()
        self.len_menu_choices: int = len(menu_choices)

        self.menu_subframe = _ContextMenuSubframe(self, self.root, menu_choices)
        self.menu_subframe.pack(
            expand=True,
            fill="both",
            padx=MENU_PADDING_X,
            pady=MENU_PADDING_Y,
        )

        self.descendants: list[tk.Misc] = self.get_all_descendants(self)  # NOT USED

        # self.bind("<FocusOut>", lambda e: self.check_should_menu_close())

    def handle_right_click(self, event) -> None:
        """Get the corrected x and y for menu placement and open the menu"""
        self.close_all_submenus()
        x, y = self.calc_menu_position(event.x_root, event.y_root)
        self.open_menu(x, y)

    def calc_menu_position(
        self, x_in: int, y_in: int, menu_depth: int = 1, parent_menu_width: int = 0
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
            print("==================================")
            print(f"Window h, w: {window_height, window_width}")
            print(f"Menu h, w: {menu_height, menu_width}")
            print(f"Event x, y: {x_in, y_in}")
            print(f"Root x, y: {root_x, root_y}")
            print(f"Screen x, y: {screen_x, screen_y}")
            print(f"Scren x, y end: {screen_x_end, screen_y_end}")
            print(f"DPI Normalized x, y: {normalized_x, normalized_y}")
            print(f"Final x, y: {x, y}")

        # INITIAL VALUES
        submenu_shift: int = 4

        scale_factor: float = self.dpi_scaler.get_scale_factor()

        window_height: int = self.root.winfo_height()
        window_width: int = self.root.winfo_width()

        menu_height: int = self.winfo_reqheight()
        menu_width: int = self.winfo_reqwidth()

        root_x: int = self.root.winfo_rootx()
        root_y: int = self.root.winfo_rooty()

        # SCREEN ADJUST (Adjust x,y for window size and placement)
        screen_x: float = x_in - root_x
        screen_y: float = y_in - root_y

        screen_x_end: float = screen_x + menu_width
        screen_y_end: float = screen_y + menu_height

        # DPI ADJUST (adjust x,y for monitor dpi/scaling)
        normalized_x: float = screen_x / scale_factor
        normalized_y: float = screen_y / scale_factor

        x: float = normalized_x
        y: float = normalized_y

        # WINDOW-EDGE ADJUST (Adjust x,y if menu would spill off screen)
        if screen_y_end > window_height:
            # Adjusting by screen_spill will open the menu as close as possible to the
            # original y position, so that the bottom edge of the menu will be touching
            # the edge of the app window. Adjusting by menu_height will invert the menu
            # so that it opens upwards instead of downwards from the original y position.
            # The order of menu items is not changed in either case.

            screen_y_spill: float = screen_y_end - window_height
            y = y - (screen_y_spill / scale_factor)
            # y = y - (menu_height / scale_factor)  # ALTERNATE METHOD

        if screen_x_end > window_width:
            # The original x position is adjusted by the menu's width to effectively flip
            # the menu on the y axis, so that it opens to the left of the x position
            # instead of right. If the menu being opened is a submenu, it's menu_depth
            # will have the int value 2, which we use to move the submenu's x position by
            # twice the menu's width (so as to prevent it from opening on top of the main
            # menu). We also add or subtract a small amount from x so as to let the
            # submenu slightly overlap with the main menu.

            # screen_x_spill: float = screen_x_end - window_width  # NOT USED

            if menu_depth == 1:
                x = x - (menu_width / scale_factor)
                # x = x - (normalized_x_spill / scale_factor)  # ALTERNATE METHOD

            elif menu_depth > 1:
                x = (
                    x
                    - ((parent_menu_width + menu_width) / scale_factor)
                    + submenu_shift
                )
        else:
            if menu_depth > 1:
                x = x - submenu_shift

        print(f"pre-x: {x}")

        if x < 0:
            x = (window_width - menu_width) / scale_factor

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
        self.close_all_submenus()
        self.place_forget()

    def close_all_submenus(self) -> None:
        for submenu in self.menu_subframe.descendant_submenus:
            self.focus_set()
            submenu.close_menu()

    def check_should_menu_close(self) -> None:
        """Check if menu should close. Mouse must be hovering over menu or
        submenu in order to stay open)"""
        print("IN CHECK SHOULD MENU CLOSE")
        if not self.is_any_submenu_hovered() or not self.is_any_submenu_open():
            self.close_menu()

    def is_any_submenu_hovered(self) -> bool:
        """Get the hovered widget's parent (a string representing the tkinter hierarchy
        chain) and return True if the submenu's name is in the hierarchy string.
        Example:
            return ".!slickcontextmenu2" in ".!slickcontextmenu2.!_contextmenusubframe
            .!contextmenubutton"
        """
        hovered_widget = self.get_widget_at_mouse()

        print(f"{hovered_widget} in {self.menu_subframe.descendant_submenus}")

        return hovered_widget in self.menu_subframe.descendant_submenus

    def is_any_submenu_open(self) -> bool:
        for submenu in self.menu_subframe.descendant_submenus:
            if submenu.winfo_ismapped():
                return True
        return False

    def get_widget_at_mouse(self):
        """Get the mouse's x and y position and find the widget in that position"""
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        return widget

    def get_all_descendants(self, widget: CTkFrame) -> list[tk.Misc]:
        descendants: list = []
        children: list = widget.winfo_children()
        for child in children:
            descendants.append(child)
            # Recurse into child's children with list.extend(func)
            descendants.extend(self.get_all_descendants(child))

        return descendants


class _ContextMenuSubframe(CTkFrame):
    def __init__(
        self,
        parent,
        root: CTk,
        menu_choices: dict[str, Callable | dict[str, Callable | dict]],
    ) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        self.root: CTk = root
        self.parent: SlickContextMenu = parent
        self.submenu_is_open = False
        self.descendant_submenus: list[SlickContextMenu] = []

        self.process_menu_choices(menu_choices)

        # self.descendants: list = self.parent.get_all_descendants(self)

    def process_menu_choices(self, menu_choices: dict) -> None:
        """Iterate through dict and create buttons and submenus"""

        for button_text, button_content in menu_choices.items():
            text_padding = "    "
            button_text: str = rf"{text_padding}{button_text}"

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
        submenu.bind("<FocusIn>", self.focus_set)
        submenu.bind(
            "<FocusOut>",
            lambda e: self.delay_check_submenu_should_close(submenu, button),
        )

        button.bind("<Enter>", lambda e: self.submenu_button_hover_in(submenu, button))
        button.bind(
            "<Leave>", lambda e: self.delay_check_submenu_should_close(submenu, button)
        )

        self.descendant_submenus.append(submenu)

    def submenu_button_hover_in(
        self, submenu: SlickContextMenu, button: SubmenuButton
    ) -> None:
        """Open submenu when submenu-button hovered if not already open."""
        self.delay_check_submenu_should_open(submenu, button)

    def delay_check_submenu_should_open(
        self, submenu: SlickContextMenu, button: SubmenuButton
    ) -> None:
        self.after(200, lambda: self.check_submenu_should_open(submenu, button))

    def check_submenu_should_open(
        self, submenu: SlickContextMenu, button: SubmenuButton
    ) -> None:
        """Submenu will open if the Mainmenu is visible, the Submenu isn't already open,
        and if the Submenu button is being hovered. Any Submenu already open is closed
        before opening the new one to ensure the undesired submenu doesn't stay open
        longer than it should."""
        if (
            self.parent.winfo_ismapped()
            and not submenu.winfo_ismapped()
            and self.is_submenu_button_hovered(button)
        ):
            self.parent.close_all_submenus()
            self.open_submenu(submenu, button)

    def open_submenu(self, submenu: SlickContextMenu, button: SubmenuButton) -> None:
        """Calculate x,y for submenu and open it."""
        x, y = self.calc_submenu_position(submenu, button)
        submenu.open_menu(x, y)

    def calc_submenu_position(
        self, submenu: SlickContextMenu, button: SubmenuButton
    ) -> tuple[float, float]:
        """Submenus need to be offset so that they don't open on top of the main menu.
        First, we set the inital x position by getting the main menu's rootx position and
        adding it's own width to it, which gives us an x position farther to the right.
        If the submenu needs to open to the left of the main menu, that will be handled
        in the calc_menu_position() method.

        Second, we set the initial y position by finding the y position of the submenu
        button and subtracting a small amount, which gives us a y position farther up.
        Moving it up slightly make it easier for the user to stay inside the submenu when
        moving the mouse quickly.

        Since Submenus are themselves instances of SlickContextMenus, we use the
        calc_menu_position() method to apply more adjustments to the x position. The
        menu_depth argument is used as a multiplier to shift the submenu appropriately
        when there in spill."""

        def __print_debug() -> None:
            print(f"{self.parent.winfo_rootx()=}")
            print(f"{self.parent.winfo_width()=}")
            print(f"{self.parent.winfo_reqwidth()=}")
            print(f"{shift_submenu_x=}")
            print(f"{shift_submenu_y=}")

        shift_y_amount: int = 4

        shift_submenu_x: int = self.parent.winfo_rootx() + self.parent.winfo_width()
        shift_submenu_y: int = button.winfo_rooty() - shift_y_amount
        parent_menu_width: int = self.parent.winfo_width()

        if PRINT_DEBUG:
            __print_debug()

        return submenu.calc_menu_position(
            shift_submenu_x,
            shift_submenu_y,
            menu_depth=2,
            parent_menu_width=parent_menu_width,
        )

    def delay_check_submenu_should_close(
        self, submenu: SlickContextMenu, button: SubmenuButton
    ) -> None:
        """Delay checking if the submenu should close. This requires the user to
        intentionally satisfy one of the requirements for longer than an instant check
        would take, and also fudges the time of the check so the user can leave one of
        the conditions and return. For example, if you move your mouse too quickly from
        the submenu button to the submenu, you might accidentally exit the submenu button
        before entering the submenu - if we did an instant check, the menu would close
        when the user didn't want it to."""
        self.after(500, lambda: self.check_submenu_should_close(submenu, button))

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
        """Check if the submenu-button is being hovered over. The actual widget being
        hovered is usually a CTkLabel or CTkCanvas, so we actually check if the hovered
        widget's master is the submenu-button itself."""

        return self.get_widget_at_mouse().master is button

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
        "Submenu Button with a really long name for testing": {
            "Sub-Copy": lambda: print("Sub-Copy"),
            "Sub-Cut": lambda: print("Sub-Cut"),
            "Sub-Paste": lambda: print("Sub-Paste"),
        },
        "Button with a really long name": lambda: print("Copy"),
        "Cut1": lambda: print("Cut"),
        "Paste1": lambda: print("Paste"),
        "Submenu1": {
            "Sub-Copy1": lambda: print("Sub-Copy"),
            "Sub-Cut1": lambda: print("Sub-Cut"),
            "SubSubMenu With a long name too for testing": {
                "Sub-Copy1": lambda: print("Sub-Copy"),
                "Sub-Cut1": lambda: print("Sub-Cut"),
                "SubSubSubmenu3": {
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
    app.bind("<FocusIn>", lambda e: print(e.widget))

    app.mainloop()

    print("==================================")
