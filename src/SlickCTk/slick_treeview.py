# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring,

from tkinter.ttk import Treeview, Style
from SlickCTk.slick_settings import (
    TREEVIEW_COLOR_HEADING,
    TREEVIEW_COLOR_TEXT,
    TREEVIEW_COLOR_ROW_SELECTED,
    TREEVIEW_COLOR_ROW_SELECTED_FOCUS_LOST,
    TREEVIEW_COLOR_ROW_BACKGROUND,
    TREEVIEW_FONT_SIZE_HEADING,
    SEARCH_RESULTS_FONT_SIZE,
    SEARCH_RESULTS_ROW_HEIGHT,
)


class SlickTreeview(Treeview):
    def __init__(self, parent, selectmode="browse", show="headings", **kwargs):
        super().__init__(parent, selectmode=selectmode, show=show, **kwargs)

        self.row_values: list = []

        self.bind("<ButtonRelease-1>", self.on_click)  # left-click on row
        self.bind("<<TreeviewSelect>>", lambda e: self.on_treeview_selection())
        self.bind("<FocusIn>", lambda e: self.on_tree_focus_in())  # update style
        self.bind("<FocusOut>", lambda e: self.on_tree_focus_out())  # update style

    def on_click(self, event):
        # Region will be "heading", "cell", "separator", or "tree"
        region = self.identify("region", event.x, event.y)
        
        if region != "cell":  # only process click if on a cell (row)
            return None
        
        # selected_rows = self.selection() # multi-select
        clicked_row = self.identify_row(event.y)  # find clicked treeview item
        # clicked_column = self.identify_column(event.x)
        
        return self.select_row(clicked_row)  # return row values for copying

    def select_row(self, row):
        self.selection_set(row)  # set treeview selection to row
        self.focus(row)  # set focus to row
        self.see(row)  # ensure selected row is visible (scrolls to row if req.)

        # get row's content (a dict), then pull out the values object (a list)
        self.row_values = self.item(row)["values"]

        return self.row_values

    def on_treeview_selection(self) -> None:
        # get row's content (a dict), then pull out the values object (a list)
        self.row_values = self.item(self.selection())["values"]

    def on_tree_focus_in(self) -> None:
        match self.cget("style"):  # get current treeview's style
            case "TreeviewCustomFocusLost.Treeview":
                self.configure(style="TreeviewCustom.Treeview")

    def on_tree_focus_out(self) -> None:
        match self.cget("style"):  # get current treeview's style
            case "TreeviewCustom.Treeview":
                self.configure(style="TreeviewCustomFocusLost.Treeview")


# TKINTER STYLING (for Treeviews)
class SlickStyleTreeview(Style):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.theme_use("default")

        # Treeview Headings
        self.configure(
            "Treeview.Heading",
            background=TREEVIEW_COLOR_HEADING,
            foreground="white",
            relief="flat",
            padding=3,
            font=(None, TREEVIEW_FONT_SIZE_HEADING),
        )
        self.map(
            "Treeview.Heading", background=[("active", TREEVIEW_COLOR_HEADING)]
        )  # removes heading hover color

        # Treeview Defaults (inherited by all other "newname.Treeview" styles)
        self.configure(
            "Treeview",
            background=TREEVIEW_COLOR_ROW_BACKGROUND,  # row background color
            foreground=TREEVIEW_COLOR_TEXT,  # row text color
            rowheight=SEARCH_RESULTS_ROW_HEIGHT,
            fieldbackground="transparent",  # area behind rows, viz. when (# rows < h)
            borderwidth=0,
            font=(
                None,
                SEARCH_RESULTS_FONT_SIZE,
            ),  # `None` let's us change the font size without changing the font
        )

        # Treeview Cells (SELECTED)
        self.theme_create("TreeviewCustom.Treeview")
        self.map(
            "TreeviewSearch.Treeview",
            background=[("selected", TREEVIEW_COLOR_ROW_SELECTED)],
        )

        # Treeview Cells (FOCUS LOST)
        self.theme_create("TreeviewCustomFocusLost.Treeview")
        self.map(
            "TreeviewSearchFocusLost.Treeview",
            background=[("selected", TREEVIEW_COLOR_ROW_SELECTED_FOCUS_LOST)],
        )


if __name__ == "__main__":
    import customtkinter as ctk
    from SlickCTk.slick_frames import SlickFrameOutlined

    app = ctk.CTk()
    app.title("SlickTreeview Demo")
    app.geometry("300x300")
    SlickStyleTreeview(app)

    frame = SlickFrameOutlined(app)
    tr = SlickTreeview(frame, columns=("col_1", "col_2"))

    tr.heading(anchor="w", column="col_1", text="Column 1")
    tr.heading(anchor="w", column="col_2", text="Column 2")
    tr.column("col_1", minwidth=50, width=50)
    tr.column("col_2", minwidth=50, width=50)

    tr.pack(expand=True, fill="both", padx=2, pady=2)

    frame.pack(expand=True, fill="both", padx=30, pady=30)
    app.mainloop()
