from customtkinter import CTkFrame
from slick_settings import COLOR_OUTLINES, FRAME_BORDER_WIDTH


class SlickFrame(CTkFrame):
    """Overrides CustomTkinter defaults

    Effects:

        Default corner radius = 0
            If you use a toplevel Frame as a wrapper for the entire app, and the color
            of that frame doesn't match the app background, the rounded edges will be
            very noticeable against the right angle of the app window. In my opinion,
            non-rounded is a better default for what is essentially Tk's wrapper widget.

        Left-click Focus binding
            Frames normally do not take focus when clicked. This binding allows other
            widgets to lose focus when the user clicks in an "empty" area of the app,
            which aligns with modern user expectations. For example, an Entry widget
            will lose focus when the user clicks in an "empty" area next to it.

        Grid Propogation = False
            If a Frame adds and removes widgets with the Grid method, the Frame will
            dynamically resize which can cause unexpected style and visual changes and
            issues. Turning this off seems like a better default to me, but can easily
            overridden in class instances by setting grid_proporate=True.
    """

    def __init__(
        self, parent, corner_radius: int = 0, fg_color: str = "transparent", **kwargs
    ) -> None:
        super().__init__(
            parent, corner_radius=corner_radius, fg_color=fg_color, **kwargs
        )

        # Allows Frames to take focus
        self.bind("<ButtonPress-1>", lambda e: self.take_focus())

        # Prevent frame from resizing to grid content
        self.grid_propagate(False)

    def take_focus(self) -> None:
        """Change focus to selected (clicked) frame"""
        self.focus_set()


class SlickFrameOutlined(SlickFrame):
    def __init__(
        self,
        parent,
        border_color=COLOR_OUTLINES,
        border_width=FRAME_BORDER_WIDTH,
        **kwargs
    ) -> None:
        super().__init__(
            parent, border_color=border_color, border_width=border_width, **kwargs
        )


if __name__ == "__main__":
    import customtkinter as ctk
    from slick_searchbar import SlickSearchbar

    app = ctk.CTk()
    app.title("SlickFrame Demo")
    app.geometry("300x300")

    frame = SlickFrame(app)
    label = ctk.CTkLabel(
        frame,
        text=(
            "SlickFrames take focus when clicked; test it by clicking in the searchbar and then clicking in any 'empty' space (not text)."
        ),
        wraplength=260,
    )
    label.pack(padx=20, pady=30)
    SlickSearchbar(frame).pack(pady=10)

    frame_lined = SlickFrameOutlined(frame, fg_color="#181818")
    ctk.CTkLabel(frame_lined, text="SlickFrameOutlined variant").pack(pady=25)
    frame_lined.pack(expand=True, fill="both", padx=30, pady=30)
    frame.pack(expand=True, fill="both")
    app.mainloop()
