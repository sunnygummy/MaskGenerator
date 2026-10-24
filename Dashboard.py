
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
from pathlib import Path


# ============================================================
# APPLICATION PATH
# ============================================================

if getattr(sys, "frozen", False):
    # Running as a packaged EXE
    APP_DIR = Path(sys.executable).resolve().parent
else:
    # Running as a normal Python script
    APP_DIR = Path(__file__).resolve().parent


# ============================================================
# GLOBAL VARIABLES
# ============================================================

folder_path = ""
destination_path = ""


# ============================================================
# PROGRAM CONFIGURATION
# ============================================================

programs = {
    "Random Bullshit Go": {
        "type": "python",
        "path": Path(
            r"C:\Users\VLWeg\Desktop\Research\randombullshitgo\main.py"
        ),
    },

    "Vignetting Prediction": {
        "type": "exe",
        "path": Path("Vignetting") / "Vignetting.exe",
    },
}


# ============================================================
# RUN SELECTED PROGRAM
# ============================================================

def run_script():

    # --------------------------------------------------------
    # Validate input and output folders
    # --------------------------------------------------------

    if not folder_path:
        messagebox.showerror(
            "Missing Input",
            "Please select an input folder."
        )
        return

    if not destination_path:
        messagebox.showerror(
            "Missing Destination",
            "Please select a destination folder."
        )
        return

    # --------------------------------------------------------
    # Identify selected program
    # --------------------------------------------------------

    selected_name = selected_program.get()
    program = programs[selected_name]

    program_path = program["path"]

    # Resolve relative paths from the application directory
    if not program_path.is_absolute():
        program_path = APP_DIR / program_path

    # --------------------------------------------------------
    # Verify program exists
    # --------------------------------------------------------

    if not program_path.is_file():
        messagebox.showerror(
            "Program Not Found",
            f"Could not find the selected program:\n\n"
            f"{program_path}"
        )
        return

    # --------------------------------------------------------
    # Build command
    # --------------------------------------------------------

    if program["type"] == "exe":

        # Packaged prediction executable
        command = [
            str(program_path),
            folder_path,
            "--out",
            destination_path,
        ]

    elif program["type"] == "python":

        # Existing Python script
        command = [
            sys.executable,
            str(program_path),
            folder_path,
        ]

    else:
        messagebox.showerror(
            "Configuration Error",
            f"Unknown program type: {program['type']}"
        )
        return

    # --------------------------------------------------------
    # Launch program
    # --------------------------------------------------------

    try:
        subprocess.Popen(
            command,
            cwd=str(program_path.parent),
            creationflags=subprocess.CREATE_NO_WINDOW
                if sys.platform == "win32"
                else 0,
        )

    except Exception as e:
        messagebox.showerror(
            "Launch Failed",
            f"Could not start {selected_name}.\n\n{e}"
        )


# ============================================================
# SELECT INPUT DIRECTORY
# ============================================================

def select_directory():

    global folder_path

    selected_folder = filedialog.askdirectory(
        title="Select Input Folder"
    )

    if selected_folder:
        folder_path = selected_folder

        input_label.config(
            text=f"Input: {folder_path}"
        )


# ============================================================
# SELECT DESTINATION DIRECTORY
# ============================================================

def select_destination():

    global destination_path

    selected_folder = filedialog.askdirectory(
        title="Select Destination Folder"
    )

    if selected_folder:
        destination_path = selected_folder

        destination_label.config(
            text=f"Destination: {destination_path}"
        )


# ============================================================
# CREATE MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title("Program Selector")
root.geometry("700x330")
root.resizable(True, False)


# ============================================================
# PROGRAM SELECTION
# ============================================================

program_label = tk.Label(
    root,
    text="Select Program:"
)

program_label.pack(pady=(15, 0))


selected_program = tk.StringVar(
    value="Vignetting Prediction"
)

dropdown = ttk.Combobox(
    root,
    width=65,
    textvariable=selected_program,
    values=list(programs.keys()),
    state="readonly",
)

dropdown.pack(pady=8)


# ============================================================
# INPUT FOLDER
# ============================================================

select_button = tk.Button(
    root,
    text="Choose Input Folder",
    command=select_directory,
)

select_button.pack(pady=5)


input_label = tk.Label(
    root,
    text="Input: No folder selected",
    wraplength=660,
)

input_label.pack(pady=5)


# ============================================================
# DESTINATION FOLDER
# ============================================================

destination_button = tk.Button(
    root,
    text="Choose Destination Folder",
    command=select_destination,
)

destination_button.pack(pady=5)


destination_label = tk.Label(
    root,
    text="Destination: No folder selected",
    wraplength=660,
)

destination_label.pack(pady=5)


# ============================================================
# RUN BUTTON
# ============================================================

run_button = tk.Button(
    root,
    text="Run Program",
    command=run_script,
    width=20,
)

run_button.pack(pady=15)


# ============================================================
# START GUI
# ============================================================

root.mainloop()
