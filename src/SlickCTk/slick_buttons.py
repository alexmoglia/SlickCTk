# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring,

from tkinter import Variable
from typing import Callable, Tuple, Union, Optional, Any
from customtkinter import CTkButton
from customtkinter.windows.widgets.font import CTkFont
from customtkinter.windows.widgets.image import CTkImage
from SlickCTk.slick_settings import (
    BUTTON_COLOR_TEXT,
    BUTTON_COLOR_BACKGROUND,
    BUTTON_COLOR_HOVER,
    BUTTON_CORNER_RADIUS,
    MENU_BUTTON_COLOR_BACKGROUND,
    MENU_BUTTON_COLOR_HOVER,
    MENU_BUTTON_CORNER_RADIUS,
    BUTTON_ACTION_WIDTH,
    BUTTON_ACTION_HEIGHT,
)


class SlickButton(CTkButton):
    def __init__(
        self,
        master: Any,
        width: int = 140,
        height: int = 28,
        corner_radius: Optional[int] = BUTTON_CORNER_RADIUS,
        border_width: Optional[int] | None = None,
        border_spacing: int = 2,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = BUTTON_COLOR_BACKGROUND,
        hover_color: Optional[Union[str, Tuple[str, str]]] = BUTTON_COLOR_HOVER,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = BUTTON_COLOR_TEXT,
        text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
        background_corner_colors: Union[
            Tuple[Union[str, Tuple[str, str]]], None
        ] = None,
        round_width_to_even_numbers: bool = True,
        round_height_to_even_numbers: bool = True,
        text: str = "Slick Button",
        font: Optional[Union[tuple, CTkFont]] = None,
        textvariable: Union[Variable, None] = None,
        image: Union[CTkImage, "ImageTk.PhotoImage", None] = None,
        state: str = "normal",
        hover: bool = True,
        command: Union[Callable[[], None], None] = None,
        compound: str = "left",
        anchor: str = "center",
        cursor: str = "hand2",
        **kwargs,
    ):
        super().__init__(
            master,
            width,
            height,
            corner_radius,
            border_width,
            border_spacing,
            bg_color,
            fg_color,
            hover_color,
            border_color,
            text_color,
            text_color_disabled,
            background_corner_colors,
            round_width_to_even_numbers,
            round_height_to_even_numbers,
            text,
            font,
            textvariable,
            image,
            state,
            hover,
            command,
            compound,
            anchor,
            cursor=cursor,
            **kwargs,
        )


class ContextMenuButton(SlickButton):
    def __init__(
        self,
        parent,
        anchor: str = "w",
        text: str = "Menu Button",
        fg_color: str = MENU_BUTTON_COLOR_BACKGROUND,
        hover_color: str = MENU_BUTTON_COLOR_HOVER,
        corner_radius: int = MENU_BUTTON_CORNER_RADIUS,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            text=text,
            fg_color=fg_color,
            hover_color=hover_color,
            corner_radius=corner_radius,
            anchor=anchor,
            **kwargs,
        )


class SubmenuButton(SlickButton):
    def __init__(
        self,
        parent,
        anchor: str = "w",
        text: str = "Menu Button",
        fg_color: str = MENU_BUTTON_COLOR_BACKGROUND,
        hover_color: str = MENU_BUTTON_COLOR_HOVER,
        corner_radius: int = MENU_BUTTON_CORNER_RADIUS,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            text=text,
            fg_color=fg_color,
            hover_color=hover_color,
            corner_radius=corner_radius,
            anchor=anchor,
            **kwargs,
        )

        # self.after_idle(self.format_button_text)
        # self.after(1, self.format_button_text)

    def format_button_text(self) -> None:
        text_width: int = self.winfo_width() - 2
        button_text: str = self.cget("text")
        print(f"text width: {text_width}")
        print(f"buttontext: {button_text}")
        padded_text: str = f"{button_text:<{text_width}} >"
        self.configure(text=padded_text)


class ActionButton(SlickButton):
    def __init__(
        self,
        parent,
        text: str = "Action Button",
        width: int = BUTTON_ACTION_WIDTH,
        height: int = BUTTON_ACTION_HEIGHT,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            text=text,
            width=width,
            height=height,
            **kwargs,
        )


if __name__ == "__main__":
    import customtkinter as ctk

    app = ctk.CTk()
    app.geometry("300x300")
    SlickButton(app).pack(pady=20)
    ContextMenuButton(app).pack(pady=20)
    ActionButton(app).pack(pady=20)
    app.mainloop()
