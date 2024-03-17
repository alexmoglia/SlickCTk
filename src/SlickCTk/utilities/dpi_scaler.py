# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=missing-class-docstring,


try:
    from ctypes import windll, c_uint, byref
    import win32api
except ImportError as e:
    print(f"Import Error: {e}")

DEFAULT_DPI: int = 96  # DPI used during app design
PROCESS_PER_MONITOR_DPI_AWARE: int = 2
MDT_EFFECTIVE_DPI: int = 0
MONITOR_DEFAULTTONEAREST: int = 2


class DPIScaler:
    def __init__(self) -> None:
        windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

        # Arbitrary default values, must differ for later comparison
        self.previous_monitor_handle: int = 0
        self.current_monitor_handle: int = 1

        self.current_monitor_dpi = 0

        self.get_scale_factor()
        self.get_dpi_current_monitor()

    def get_dpi(self, monitor_handle: int) -> int:
        dpi_x: c_uint = c_uint()
        dpi_y: c_uint = c_uint()

        windll.shcore.GetDpiForMonitor(
            monitor_handle, MDT_EFFECTIVE_DPI, byref(dpi_x), byref(dpi_y)
        )

        print(f"Monitor Handle: {monitor_handle} | DPI: {dpi_x.value}x{dpi_y.value}")

        assert dpi_x.value == dpi_y.value
        return dpi_x.value

    def get_dpi_current_monitor(self) -> int:
        window_id = windll.user32.GetForegroundWindow()  # Get app's window ID

        # Locate nearest monitor (monitor containing the majority of app window)
        self.current_monitor_handle = windll.user32.MonitorFromWindow(
            window_id, MONITOR_DEFAULTTONEAREST
        )

        # Only run get_dpi() if current monitor changes
        if self.current_monitor_handle != self.previous_monitor_handle:
            # get dpi for current monitor
            self.current_monitor_dpi: int = self.get_dpi(self.current_monitor_handle)

            # update tracking var with current monitor
            self.previous_monitor_handle = self.current_monitor_handle

        return self.current_monitor_dpi  # return dpi

    def get_dpi_all_monitors(self) -> None:
        monitors = win32api.EnumDisplayMonitors()
        for monitor in monitors:
            monitor_handle: int = monitor[0].handle
            self.get_dpi(monitor_handle)

    def get_scale_factor(self) -> float:
        self.scale_factor: float = self.get_dpi_current_monitor() / DEFAULT_DPI
        return self.scale_factor

    def scale_up(self, original_size: int) -> int:
        new_size: int = round(original_size * self.scale_factor)
        print(f"Scaling {original_size} up to {new_size}")
        return int(new_size)

    def scale_down(self, original_size: int) -> int:
        new_size: int = round(original_size / self.scale_factor)
        print(f"Scaling {original_size} down to {new_size}")
        return int(new_size)


if __name__ == "__main__":
    DPIScaler()
