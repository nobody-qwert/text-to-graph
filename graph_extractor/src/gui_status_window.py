import threading
import queue
import os
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap import ttk
import asyncio
import platform
import subprocess

import abort_manager
import graph_generator as gg
from gui_utils import center_window
from log_utils import get_module_logger

logger = get_module_logger("main-app")

BUTTON_WIDTH = 15

message_queue = queue.Queue()


def open_output_folder(folder_path):
    system_name = platform.system()
    try:
        if system_name == "Windows":
            os.startfile(folder_path)
        elif system_name == "Darwin":  # macOS
            subprocess.Popen(["open", folder_path])
        else:  # Linux and others
            subprocess.Popen(["xdg-open", folder_path])
    except Exception as e:
        logger.exception(f"Could not open folder: {folder_path}. Error: {e}")


def add_status_message(status_window_data, message, tag=None):
    status_text = status_window_data["text_widget"]
    status_text.configure(state=tk.NORMAL)
    # Insert the message with the tag (could be 'error', 'log', etc.)
    if tag is not None:
        status_text.insert(tk.END, f"{message}\n", tag)
    else:
        status_text.insert(tk.END, f"{message}\n")
    status_text.see(tk.END)
    status_text.configure(state=tk.DISABLED)
    status_text.update_idletasks()


def show_status_window(root, selected_files, config):
    root.attributes("-alpha", 0.7)

    status_window = tb.Toplevel(root)
    status_window.withdraw()

    status_window.title("Generation Status")
    status_window.resizable(True, True)

    frame = ttk.Frame(status_window, padding=(5, 5, 5, 0))
    frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    status_text = tk.Text(
        frame,
        wrap=tk.WORD,
        relief=tk.GROOVE,
        borderwidth=2,
        height=10,
        yscrollcommand=scrollbar.set,
        font=("Roboto Mono", 10)
    )
    status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=status_text.yview)

    # ------------------------------------------------------------
    # Here we configure a text tag named "error" that will be red.
    # You can add more tags if you want to style different message types.
    # ------------------------------------------------------------
    status_text.tag_configure("error", foreground="red")

    status_window_data = {
        "text_widget": status_text,
        "should_abort": False,
        "progress_line_index": None,
        "window": status_window,
        "success": None
    }

    button_frame = ttk.Frame(status_window)
    button_frame.pack(side=tk.BOTTOM, pady=10)

    abort_button = ttk.Button(
        button_frame,
        text="Abort",
        command=lambda: abort_processing(status_window_data, abort_button),
        width=BUTTON_WIDTH,
        style="Generic.TButton",
        takefocus=0
    )
    abort_button.pack(side=tk.LEFT)

    def on_ok():
        if status_window_data["success"] and not abort_manager.ABORT_FLAG:
            open_output_folder(config["output_folder"])
        status_window.destroy()

    ok_button = ttk.Button(
        button_frame,
        text="OK",
        command=on_ok,
        width=BUTTON_WIDTH,
        style="Generic.TButton",
        takefocus=0
    )
    ok_button.pack_forget()

    add_status_message(status_window_data, "Starting processing...")

    def worker_thread_func():
        process_files_for_real(selected_files, config, status_window_data)

    t = threading.Thread(target=worker_thread_func, daemon=True)
    t.start()

    def poll_messages():
        while True:
            try:
                msg = message_queue.get_nowait()
            except queue.Empty:
                break
            else:
                if msg["type"] == "log":
                    add_status_message(status_window_data, msg["text"])
                    status_window_data["progress_line_index"] = None

                elif msg["type"] == "error":
                    status_window_data["success"] = False

                    msg_text = f"\n\n                                                  ====   ERROR   ====\n\n{msg['text']}"
                    add_status_message(status_window_data, msg_text, tag="error")
                    status_window_data["progress_line_index"] = None

                elif msg["type"] == "progress":
                    progress_line = msg["text"]
                    status_text.configure(state=tk.NORMAL)
                    if status_window_data["progress_line_index"] is None:
                        status_text.insert(tk.END, "")
                        line_start = status_text.index("end-1l")
                        status_text.insert(line_start, progress_line)
                        status_window_data["progress_line_index"] = line_start
                    else:
                        line_start = status_window_data["progress_line_index"]
                        status_text.delete(line_start, f"{line_start} lineend")
                        status_text.insert(line_start, progress_line)
                    status_text.see(tk.END)
                    status_text.configure(state=tk.DISABLED)
                    status_text.update_idletasks()

                elif msg["type"] == "done":
                    if status_window_data["success"] is None:
                        status_window_data["success"] = True

                    add_status_message(status_window_data, "\n\nProcessing Finished.\n")
                    abort_button.pack_forget()
                    ok_button.pack(side=tk.LEFT, padx=5)

                elif msg["type"] == "aborted":
                    status_window_data["success"] = False

                    add_status_message(status_window_data, "Processing aborted by user.")
                    abort_button.pack_forget()
                    ok_button.pack(side=tk.LEFT, padx=5)

        if t.is_alive():
            status_window.after(10, poll_messages)

    poll_messages()

    status_window.update_idletasks()
    center_window(status_window, root)

    status_window.transient(root)
    status_window.grab_set()
    status_window.focus_force()

    status_window.lift()

    status_window.deiconify()

    root.wait_window(status_window)

    root.attributes("-alpha", 1.0)


def abort_processing(status_window_data, abort_button):
    add_status_message(status_window_data, "\nUser pressed abort. Attempting to stop...")
    status_window_data["should_abort"] = True
    abort_manager.ABORT_FLAG = True
    abort_button.configure(state=tk.DISABLED)


def process_files_for_real(selected_files, config, status_window_data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(
            gg.generate_graph_async(
                selected_files,
                config,
                lambda m, type_name='progress': message_queue.put({"type": type_name, "text": m})
            )
        )
    except Exception as e:
        logger.exception(f"Error processing files")
        message_queue.put({"type": "error", "text": f"{str(e)}"})

    loop.close()

    message_queue.put({"type": "done"})

