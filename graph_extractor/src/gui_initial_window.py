import os
import threading
from ttkbootstrap import ttk
import llm_api
import config as cfg
from gui_main_window import build_main_gui
from gui_style_definitions import configure_button_styles

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 380


def show_error_message_and_close(root, parent_frame, error_message, error_title, show_settings_callback, config):
    for child in parent_frame.winfo_children():
        child.destroy()

    parent_frame.rowconfigure(0, weight=1)  # Top spacer
    parent_frame.rowconfigure(1, weight=0)  # Row for "Error" label
    parent_frame.rowconfigure(2, weight=0)  # Row for error message
    parent_frame.rowconfigure(3, weight=0)  # Row for OK button
    parent_frame.rowconfigure(4, weight=1)  # Bottom spacer
    parent_frame.columnconfigure(0, weight=1)

    bold_error_label = ttk.Label(
        parent_frame,
        text=error_title,
        foreground="red",
        anchor="center",
        font=("Roboto Mono", 16, "bold")
    )
    bold_error_label.grid(row=1, column=0, sticky="n", pady=(0, 5))

    message_label = ttk.Label(
        parent_frame,
        text=error_message,
        foreground="red",
        wraplength=400,
        anchor="center",
        font=("Roboto Mono", 12)
    )
    message_label.grid(row=2, column=0, sticky="n", pady=(0, 10))

    def on_ok_clicked():
        show_settings_callback()

    ok_button = ttk.Button(
        parent_frame,
        text="OK",
        style="OkButton.TButton",
        command=on_ok_clicked
    )
    ok_button.grid(row=3, column=0, sticky="n")


def build_initial_gui(root, show_settings_callback):
    root.title("Config Check")
    root.resizable(False, False)

    configure_button_styles(root)
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill="both", expand=True)

    if not os.path.exists(cfg.default_config['config_file']):
        show_settings_callback()
        return

    config, error_messages = cfg.load_config()

    print(error_messages)

    if error_messages is not None:
        show_error_message_and_close(
            root,
            main_frame,
            "\n".join(error_messages),
            error_title=f"Error in {config['config_file']}",
            show_settings_callback=show_settings_callback,
            config=cfg.default_config
        )
    else:
        cfg.print_config(config)
        extended_config = cfg.build_extended_config(config)
        cfg.print_config(config)

        llm_api.set_llm_config(config)

        loading_label = ttk.Label(
            main_frame,
            text="Testing Tools & API connection ... Please wait",
            anchor="center",
            font=("Roboto Mono", 11)
        )
        loading_label.pack(pady=20)

        progress_bar = ttk.Progressbar(main_frame, mode='indeterminate', length=200)
        progress_bar.pack(pady=10)
        progress_bar.start(10)

        def finish_api_test(error_message):
            progress_bar.stop()
            loading_label.pack_forget()
            progress_bar.pack_forget()

            if error_message:
                show_error_message_and_close(root, main_frame, error_message, "API Error", show_settings_callback, cfg.default_config)
            else:
                build_main_gui(root, show_settings_callback, extended_config)

        def test_api_thread():
            cfg.detect_external_pdf_extractor_tool(config)
            error_message = llm_api.test_api(config)
            root.after(0, lambda: finish_api_test(error_message))

        def start_test_api():
            t = threading.Thread(target=test_api_thread, daemon=True)
            t.start()

        root.after(10, start_test_api)

    root.update_idletasks()
    root.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
