# SlickCTk

Additional widgets and biased defaults to extend CustomTKinter (work in progress).

## New Widgets

### SlickContextMenu

"Right-click" / context menus.

- Easy to create - just pass in a dictionary with button names and functions. (`dict[str, Callable]`)
- Supports submenus - just pass in another dictionary as the value of the button name key. (`dict[str, dict[str, Callable]`)
- Technically supports endless nesting of submenus, but good UX would probably dictate not going past one or two levels (`dict[str, dict[str, Callable | dict[str, Callable | dict...]]`)
- Automatically handles menu spill (adjusting left<>right and up<>down to stay inside the app window).
- Menu placement accounts for DPI / screen scaling

### SlickSearchbar (searchbars)
- Placeholder text dynamically added/removed
- X button for clearing the searchbar text

## Biased Defaults

### SlickFrame
- Default corner radius = 0 (overrides default rounded corner)
- Left-click Focus binding (let frames take focus when clicked on)
- Grid Propogation = False (prevents the frame from resizing if widgets are added/removed from grid dynamically)

### SlickTreeview
- Style overrides