import os
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import ttk
from config import CONFIG_TEMPLATE
from gui_initial_window import build_initial_gui

import config as cfg


def build_config_gui(root):
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Settings")

    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # ---------------------------------------------------------------------------------------

    api_allowed_values = CONFIG_TEMPLATE["api"]["allowed_values"] or []
    model_allowed_values = CONFIG_TEMPLATE["model"]["allowed_values"] or []
    llm_min, llm_max = CONFIG_TEMPLATE["llm_timeout"]["range"]
    max_con_min, max_con_max = CONFIG_TEMPLATE["max_concurrent_requests"]["range"]

    # ---------------------------------------------------------------------------------------

    config = cfg.default_config

    if os.path.exists(cfg.default_config['config_file']):
        config, error_messages = cfg.load_config()

    # ---------------------------------------------------------------------------------------

    api_var = tk.StringVar(value=config.get("api", api_allowed_values[0] if api_allowed_values else ""))
    model_var = tk.StringVar(value=config.get("model", model_allowed_values[0] if model_allowed_values else ""))
    api_key_var = tk.StringVar(value=config.get("api_key", ""))
    max_concurrent_var = tk.StringVar(value=str(config.get("max_concurrent_requests", 5)))
    llm_timeout_var = tk.StringVar(value=str(config.get("llm_timeout", 30)))
    tool_var = tk.StringVar(value=config.get("doc_parser_tool", ""))

    # ---------------------------------------------------------------------------------------

    api_label = ttk.Label(main_frame, text="API Provider", style="Config.TLabel")
    api_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

    api_combobox = ttk.Combobox(
        main_frame,
        textvariable=api_var,
        style="Config.TCombobox",
        values=api_allowed_values,
        state="readonly"
    )
    api_combobox.grid(row=0, column=1, sticky=tk.W, padx=0, pady=(0, 5))

    # ---------------------------------------------------------------------------------------

    model_label = ttk.Label(main_frame, text="Model", style="Config.TLabel")
    model_label.grid(row=1, column=0, sticky=tk.W, pady=5)

    model_combobox = ttk.Combobox(
        main_frame,
        textvariable=model_var,
        style="Config.TCombobox",
        values=model_allowed_values,
        state="readonly"
    )
    model_combobox.grid(row=1, column=1, sticky=tk.W, padx=0, pady=5)

    # ---------------------------------------------------------------------------------------
    api_combobox.bind("<FocusIn>", lambda event: event.widget.selection_clear())
    model_combobox.bind("<FocusIn>", lambda event: event.widget.selection_clear())
    # ---------------------------------------------------------------------------------------

    def validate_text_length(input_text):
        return len(input_text) <= 1024

    validate_text_length_command = root.register(validate_text_length)

    def validate_small_field(input_text):
        return len(input_text) <= 3

    validate_small_field_command = root.register(validate_small_field)

    # ---------------------------------------------------------------------------------------

    api_key_label = ttk.Label(main_frame, text="API Key", style="Config.TLabel")
    api_key_label.grid(row=2, column=0, sticky=tk.W, pady=5)

    api_key_entry = ttk.Entry(
        main_frame,
        textvariable=api_key_var,
        style="Config.TEntry",
        width=50,
        validate="key",
        validatecommand=(validate_text_length_command, "%P")
    )

    api_key_entry.grid(row=2, column=1, sticky=tk.W, padx=0, pady=5)

    # ---------------------------------------------------------------------------------------

    max_con_label = ttk.Label(
        main_frame,
        text=f"Max Requests ({max_con_min}-{max_con_max})",
        style="Config.TLabel"
    )
    max_con_label.grid(row=3, column=0, sticky=tk.W, pady=5)

    max_con_entry = ttk.Entry(
        main_frame,
        textvariable=max_concurrent_var,
        style="Config.TEntry",
        width=5,
        validate="key",
        validatecommand=(validate_small_field_command, "%P")
    )
    max_con_entry.grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)

    # ---------------------------------------------------------------------------------------

    timeout_label = ttk.Label(
        main_frame,
        text=f"API Timeout ({llm_min}-{llm_max})",
        style="Config.TLabel"
    )
    timeout_label.grid(row=4, column=0, sticky=tk.W, pady=5)

    timeout_entry = ttk.Entry(
        main_frame,
        textvariable=llm_timeout_var,
        style="Config.TEntry",
        width=5,
        validate="key",
        validatecommand=(validate_small_field_command, "%P")
    )
    timeout_entry.grid(row=4, column=1, sticky=tk.W, padx=0, pady=5)

    # ---------------------------------------------------------------------------------------

    tool_label = ttk.Label(main_frame, text="External Tool", style="Config.TLabel")
    tool_label.grid(row=5, column=0, sticky=tk.W, pady=5)

    tool_entry = ttk.Entry(
        main_frame,
        textvariable=tool_var,
        style="Config.TEntry",
        width=50,
        validate="key",
        validatecommand=(validate_text_length_command, "%P")
    )

    tool_entry.grid(row=5, column=1, sticky=tk.W, padx=0, pady=5)

    # ---------------------------------------------------------------------------------------

    def save_config():
        try:
            max_concurrent = int(max_concurrent_var.get())
        except ValueError:
            max_concurrent = 5

        try:
            llm_timeout = int(llm_timeout_var.get())
        except ValueError:
            llm_timeout = 30

        config["api"] = api_var.get()
        config["model"] = model_var.get()
        config["api_key"] = api_key_var.get()
        config["max_concurrent_requests"] = max_concurrent
        config["llm_timeout"] = llm_timeout
        config["doc_parser_tool"] = tool_var.get()

        errors = cfg.validate_config(config, ignore_config_filename_field=True)
        if errors:
            errors_str = ""
            for e in errors:
                if len(errors_str) > 0:
                    errors_str = errors_str + "\n"
                errors_str = errors_str + e
            messagebox.showinfo("Invalid config", errors_str)
        else:
            cfg.save_config(config)

            main_frame.destroy()
            build_initial_gui(root, show_settings_callback=show_settings)
            return

    def show_settings():
        build_config_gui(root)

    save_button = ttk.Button(
        main_frame,
        text="Save & Exit",
        style="OkButton.TButton",
        command=save_config
    )

    main_frame.rowconfigure(6, weight=1)
    main_frame.rowconfigure(7, weight=0)

    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    save_button.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 10))

    root.update_idletasks()
