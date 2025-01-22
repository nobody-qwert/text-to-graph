import tkinter as tk


class Tooltip:
    def __init__(self, widget, text="", delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        self.mouse_x = 0
        self.mouse_y = 0

        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)

    def on_enter(self, event=None):
        self.schedule_show()

    def on_leave(self, event=None):
        self.schedule_hide()
        self.hide_tooltip()

    def on_motion(self, event):
        self.mouse_x = event.x_root
        self.mouse_y = event.y_root

    def schedule_show(self):
        self.schedule_hide()
        self.id = self.widget.after(self.delay, self.show_tooltip)

    def schedule_hide(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show_tooltip(self):
        if self.tipwindow or not self.text:
            return

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)

        offset_x = 15
        offset_y = 15
        tw.wm_geometry(f"+{self.mouse_x + offset_x}+{self.mouse_y + offset_y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Roboto Mono", "8", "normal")
        )
        label.pack(ipadx=1)

    def hide_tooltip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    def update_text(self, text):
        self.text = text
