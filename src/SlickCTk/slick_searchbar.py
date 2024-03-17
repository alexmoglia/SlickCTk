"""
Slick Searchbar

Features: 
    - Placeholder text auto added and removed
    - custom X button to clear search field, auto added and removed

TODO:
    - Animated/expandable searchbar (small initial width, click in and it expands [to 
    the right or from the center out in both directions])
    
"""

from tkinter import Canvas, font
from customtkinter import CTkEntry, StringVar
from utilities.dpi_scaler import DPIScaler
from slick_settings import (
    COLOR_APP_BACKGROUND,
    COLOR_TEXT,
    SEARCHBAR_COLOR_OUTLINE,
    SEARCHBAR_COLOR_OUTLINE_FOCUS,
    SEARCHBAR_COLOR_PLACEHOLDER,
    SEARCHBAR_FONT,
    SEARCHBAR_X_FONT,
)


class SlickSearchbar(CTkEntry):
    """Custom Searchbar

    Features:

        Placeholder Text
            Added/removed when the Searchbar gains/loses focus

        "X" Button (Clear text)
            Appears after the first character is typed in the Searchbar; removed
            when the Searchbar is empty.

    """

    def __init__(
        self,
        parent,
        placeholder: str = "Search...",
        height: int = 10,
        width: int = 250,
        corner_radius: int = 20,
        font: tuple[str, int] = SEARCHBAR_FONT,
        text_color: str = SEARCHBAR_COLOR_PLACEHOLDER,
        fg_color: str = "transparent",
        border_color: str = SEARCHBAR_COLOR_OUTLINE,
        border_width: int = 2,
        **kwargs,
    ):
        self.search_term = StringVar(parent, "Search...")
        self.placeholder = placeholder

        super().__init__(
            parent,
            width=width,
            corner_radius=corner_radius,
            font=font,
            text_color=text_color,
            fg_color=fg_color,
            border_color=border_color,
            border_width=border_width,
            textvariable=self.search_term,
            placeholder_text=placeholder,
            **kwargs,
        )

        self.search_placeholder = placeholder
        self.dpi = DPIScaler()

        # TRACE
        self.search_term.trace("w", lambda *args: self.trace_search_term())

        # BIND
        self.bind("<FocusIn>", lambda e: self.on_focus_in())
        self.bind("<FocusOut>", lambda e: self.on_focus_out())
        self.bind("<Configure>", lambda e: self.on_window_configure())

        # self.button_x = _XButton(self)
        self.button_x = _XButtonCanvas(self)

    def on_focus_in(self) -> None:
        """Set colors, check to clear placeholder text"""
        self.configure(
            text_color=COLOR_TEXT,
            border_color=SEARCHBAR_COLOR_OUTLINE_FOCUS,
        )

        if self.search_term.get() == self.search_placeholder:
            # delete placeholder text when search box gains focus
            self.delete(0, len(self.search_term.get()))

    def on_focus_out(self):
        """Set colors, check to reset placeholder text"""
        self.configure(
            text_color=SEARCHBAR_COLOR_PLACEHOLDER,
            border_color=SEARCHBAR_COLOR_OUTLINE,
        )

        # if search_term is empty, reset placeholder text
        if len(self.search_term.get()) < 1:
            self.search_term.set(self.search_placeholder)
            self.button_x.place_forget()

    def on_window_configure(self):
        """Redraw the X button if monitor/dpi change"""
        self.trace_search_term()

    def trace_search_term(self):
        """Add the "X" button if any text is entered in search"""
        scale_factor = self.dpi.get_scale_factor()
        search = self.search_term.get()

        if len(search) > 0 and search != self.placeholder:
            if scale_factor == 1:
                self.button_x.place(relx=0.90, rely=0.15)
            else:
                self.button_x.place(relx=0.91, rely=0.213)
        else:
            self.button_x.place_forget()


class _XButtonCanvas(Canvas):
    def __init__(
        self,
        parent,
        height: int = 18,
        width: int = 18,
        background: str = COLOR_APP_BACKGROUND,
        borderwidth=0,
        highlightthickness=0,
        cursor: str = "hand2",
        closeenough: float = 0,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            height=height,
            width=width,
            background=background,
            borderwidth=borderwidth,
            highlightthickness=highlightthickness,
            cursor=cursor,
            closeenough=closeenough,
            **kwargs,
        )

        self.parent: SlickSearchbar = parent

        x_font = font.Font(family=SEARCHBAR_X_FONT, size=15)

        self.x_button = self.create_text(
            7,
            7,
            text="x",
            font=x_font,
            anchor="center",
            fill=SEARCHBAR_COLOR_PLACEHOLDER,
        )

        self.x_id = self.find_all()[0]
        print(f"x button id: {self.x_id}")

        self.bind("<1>", lambda e: self.on_button_click())  # Mouse 1
        self.bind("<Enter>", lambda e: self.on_button_hover())  # Hover in
        self.bind("<Leave>", lambda e: self.on_button_hover())  # Hover out

    def on_button_click(self) -> None:
        """X Button click handler"""
        self.parent.delete(0, len(self.parent.search_term.get()))
        self.itemconfigure(self.x_id, fill=SEARCHBAR_COLOR_PLACEHOLDER)
        self.place_forget()
        self.parent.focus_set()

    def on_button_hover(self) -> None:
        """X button hover handler"""
        if self.itemcget(self.x_id, "fill") == SEARCHBAR_COLOR_PLACEHOLDER:
            self.itemconfigure(self.x_id, fill=COLOR_TEXT)
        else:
            self.itemconfigure(self.x_id, fill=SEARCHBAR_COLOR_PLACEHOLDER)


if __name__ == "__main__":
    import customtkinter as ctk
    from slick_frames import SlickFrame

    app = ctk.CTk()
    app.title("SlickSearchbar Demo")
    app.geometry("300x100")
    frame = SlickFrame(app, fg_color=COLOR_APP_BACKGROUND)
    SlickSearchbar(frame).pack(pady=30)
    frame.pack(expand=True, fill="both")
    app.mainloop()
