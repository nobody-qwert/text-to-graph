import tkinter as tk


def center_window(window: tk.Toplevel, reference: tk.Toplevel = None) -> None:
    window.update_idletasks()

    if reference is not None:
        ref_x = reference.winfo_rootx()
        ref_y = reference.winfo_rooty()
        ref_w = reference.winfo_width()
        ref_h = reference.winfo_height()

        win_w = window.winfo_width()
        win_h = window.winfo_height()

        x = ref_x + (ref_w - win_w) // 2
        y = ref_y
    else:
        screen_w = window.winfo_screenwidth()
        screen_h = window.winfo_screenheight()

        win_w = window.winfo_width()
        win_h = window.winfo_height()

        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2

    window.geometry(f"{win_w}x{win_h}+{x}+{y}")
