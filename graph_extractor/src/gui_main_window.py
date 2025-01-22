import os
import tkinter as tk
from tkinter import filedialog
from ttkbootstrap import ttk
from ttkbootstrap.dialogs import Messagebox
import config as cfg
import abort_manager
from gui_status_window import show_status_window
from gui_tooltip import Tooltip

BUTTON_WIDTH = 15

selected_files = []


def browse_files(rebuild_gui_callback):
    new_files = filedialog.askopenfilenames(
        title="Select PDF Files",
        filetypes=(("PDF Files", "*.pdf"), ("All Files", "*.*"))
    )
    if new_files:
        for path in new_files:
            if path not in selected_files:
                selected_files.append(path)
        rebuild_gui_callback()


def generate(root, config):
    if not selected_files:
        Messagebox.show_warning("Warning", "No PDF files selected.")
        return
    abort_manager.ABORT_FLAG = False
    show_status_window(root, selected_files, config)


def clear_all_files(rebuild_gui_callback):
    selected_files.clear()
    rebuild_gui_callback()


def remove_file(file_path, rebuild_gui_callback):
    if file_path in selected_files:
        selected_files.remove(file_path)
    rebuild_gui_callback()


def build_main_gui(root, show_settings_callback, config):
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Knowledge Graph Generator")

    if "merge_document_graphs" not in config:
        config["merge_document_graphs"] = False

    if "optimization_on" not in config:
        config["optimization_on"] = False

    if "resolution_state" not in config:
        config["resolution_state"] = "normal"

    def toggle_merge_graphs():
        config["merge_document_graphs"] = not config["merge_document_graphs"]
        update_merge_graphs_button()
        merge_graphs_button_tooltip.update_text(get_merge_graphs_button_tooltip_text())

    def update_merge_graphs_button():
        merge_graphs_button.configure(text=get_merge_graphs_button_text())

    def get_merge_graphs_button_text():
        if config["merge_document_graphs"]:
            return "▶ Combined"
        else:
            return "▶ Individual"

    def get_merge_graphs_button_tooltip_text():
        if config["merge_document_graphs"]:
            return "Combine Documents into one Graph"
        else:
            return "Create individual Graph for each Document"

    def get_optimization_tooltip_text():
        if config["optimization_on"]:
            return "Caching Active\nsaving time & reducing cost"
        else:
            return "Caching Disabled\ngenerate graphs from scratch"

    def show_setting():
        show_settings_callback()
        return

    def toggle_optimization():
        config["optimization_on"] = not config["optimization_on"]
        update_optimization_button()
        optimize_button_tooltip.update_text(get_optimization_tooltip_text())

    def update_optimization_button():
        if config["optimization_on"]:
            optimize_button.configure(style="OptimizeOn.TButton")
        else:
            optimize_button.configure(style="OptimizeOff.TButton")

    def get_resolution_tooltip_text():
        if config["resolution_state"] == "normal":
            return "Fast & Cost Effective"
        else:
            return "More Insights (Longer Processing)"

    def get_resolution_caption():
        if config["resolution_state"] == "normal":
            return "▶ Normal"
        else:
            return "▶ High Detail"

    def toggle_resolution():
        if config["resolution_state"] == "normal":
            cfg.set_resolution(config, "high")
        else:
            cfg.set_resolution(config, "normal")
        update_resolution_button()
        resolution_button_tooltip.update_text(get_resolution_tooltip_text())

    def update_resolution_button():
        resolution_button.configure(text=get_resolution_caption())

    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    top_frame = ttk.Frame(main_frame)
    top_frame.pack(side=tk.TOP, fill=tk.X)

    # -------------------------------------------------------------------------
    browse_button = ttk.Button(
        top_frame,
        text="Browse PDF Files",
        command=lambda: browse_files(
            lambda: build_main_gui(root, show_settings_callback, config)
        ),
        width=BUTTON_WIDTH,
        style="BrowseOrange.TButton",
        takefocus=0
    )
    browse_button.pack(side=tk.LEFT)
    # -------------------------------------------------------------------------
    clear_button = ttk.Button(
        top_frame,
        text="Clear All",
        command=lambda: clear_all_files(
            lambda: build_main_gui(root, show_settings_callback, config)
        ),
        width=int(BUTTON_WIDTH * 0.75),
        style="Generic.TButton",
        takefocus=0
    )
    clear_button.pack(side=tk.LEFT, padx=(10, 10))
    # -------------------------------------------------------------------------
    optimize_button = ttk.Button(
        top_frame,
        text="♻️",
        command=toggle_optimization,
        style="OptimizeOn.TButton" if config["optimization_on"] else "OptimizeOff.TButton",
        takefocus=0
    )
    optimize_button.pack(side=tk.RIGHT, padx=(5, 0))

    optimize_button_tooltip = Tooltip(
        optimize_button,
        text=get_optimization_tooltip_text(),
        delay=200
    )

    # -------------------------------------------------------------------------

    config_button = ttk.Button(
        top_frame,
        text="⚙️",
        command=show_setting,
        style="Settings.TButton",
        takefocus=0
    )
    config_button.pack(side=tk.RIGHT, padx=(5, 0))

    config_button_tooltip = Tooltip(
        config_button,
        text="Change Settings",
        delay=200
    )

    # -------------------------------------------------------------------------

    middle_frame = ttk.Frame(main_frame)
    middle_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    canvas = tk.Canvas(middle_frame, highlightthickness=0)
    scrollbar = ttk.Scrollbar(middle_frame, orient=tk.VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    files_container = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=files_container, anchor="nw")

    for file_path in selected_files:
        row_frame = ttk.Frame(files_container)
        row_frame.pack(fill=tk.X, pady=2)

        remove_btn = ttk.Button(
            row_frame,
            text="X",
            style="XRemove.TButton",
            width=2,
            command=lambda f=file_path: remove_file(
                f,
                lambda: build_main_gui(root, show_settings_callback, config)
            ),
            takefocus=0
        )
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))

        file_label = ttk.Label(row_frame, text=os.path.basename(file_path), anchor="w", font=("Roboto Mono", 10))
        file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _on_mousewheel(event):
        if event.num == 4:  # Linux scroll up
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            canvas.yview_scroll(1, "units")
        else:
            # Windows/Mac: event.delta is 120 or -120 for a single scroll
            canvas.yview_scroll(int(-event.delta / 120), "units")

    def on_enter_canvas(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

    def on_leave_canvas(event):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    def update_scrollbar_visibility():
        files_container.update_idletasks()
        required_height = files_container.winfo_reqheight()
        current_height = canvas.winfo_height()

        if required_height > current_height:
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.bind("<Enter>", on_enter_canvas)
            canvas.bind("<Leave>", on_leave_canvas)
        else:
            scrollbar.pack_forget()
            canvas.unbind("<Enter>")
            canvas.unbind("<Leave>")
            canvas.yview_moveto(0)

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        update_scrollbar_visibility()

    files_container.bind("<Configure>", on_frame_configure)

    bottom_frame = ttk.Frame(main_frame)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # -------------------------------------------------------------------------
    generate_button = ttk.Button(
        bottom_frame,
        text="Generate Graphs",
        command=lambda: generate(root, config),
        width=BUTTON_WIDTH,
        style="GenerateGraph.TButton",
        takefocus=0
    )
    generate_button.pack(side=tk.LEFT, padx=5)
    # -------------------------------------------------------------------------
    if selected_files:
        clear_button.config(state="normal")
        generate_button.config(state="normal")
    else:
        clear_button.config(state="disabled")
        generate_button.config(state="disabled")
    # -------------------------------------------------------------------------
    resolution_button = ttk.Button(
        bottom_frame,
        text=get_resolution_caption(),
        command=toggle_resolution,
        style="Resolution.TButton",
        takefocus=0,
        width=11
    )
    resolution_button.pack(side=tk.LEFT, padx=(5, 0))

    resolution_button_tooltip = Tooltip(
        resolution_button,
        text=get_resolution_tooltip_text(),
        delay=200
    )

    # -------------------------------------------------------------------------
    info_label = ttk.Label(
        bottom_frame,
        text="ℹ",
        style="InfoLabel.TLabel"
    )
    info_label.pack(side=tk.RIGHT, padx=(10, 0))

    pdf_tool_name = 'internal'
    if config['doc_parser_tool']:
        pdf_tool_name = config['doc_parser_tool']

    info_tooltip = Tooltip(
        info_label,
        text=f"API: {config['api']}\n"
             f"Model: {config['model']}\n"
             f"API Max Parallel Request: {config['max_concurrent_requests']}\n"
             f"API Timeout: {config['llm_timeout']}s\n"
             f"PDF Extractor: {pdf_tool_name}",
        delay=200
    )

    # -------------------------------------------------------------------------

    merge_graphs_button = ttk.Button(
        bottom_frame,
        text=get_merge_graphs_button_text(),
        command=toggle_merge_graphs,
        style="Resolution.TButton",
        takefocus=0
    )
    merge_graphs_button.pack(side=tk.LEFT, padx=(5, 0))

    merge_graphs_button_tooltip = Tooltip(
        merge_graphs_button,
        text=get_merge_graphs_button_tooltip_text(),
        delay=200
    )

    # -------------------------------------------------------------------------

    update_scrollbar_visibility()
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    root.update_idletasks()

