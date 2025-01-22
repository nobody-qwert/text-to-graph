import ttkbootstrap as tb
from gui_initial_window import build_initial_gui
from gui_config_window import build_config_gui


import tracemalloc

tracemalloc.start()


def main():
    root = tb.Window(themename="journal")
    # root.iconbitmap("graph.ico")

    def show_setting():
        build_config_gui(root)

    build_initial_gui(root, show_setting)
    root.mainloop()


if __name__ == '__main__':
    main()
