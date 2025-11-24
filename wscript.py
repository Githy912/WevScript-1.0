import tkinter as tk
from tkinter import scrolledtext, filedialog
import subprocess
import os
import sys

# ----------------------------
# Helper to run WS scripts
# ----------------------------
def run_ws_file(path):
    if not os.path.isfile(path):
        append_output(f"❌ File not found: {path}\n")
        return
    append_output(f"▶ Running: {path}\n\n")
    try:
        # Call Python to execute ws.py interpreter on the script
        # Assuming ws.py is in the same folder as wscript.py
        ws_py = os.path.join(ROOT_DIR, "ws.py")
        if not os.path.isfile(ws_py):
            append_output(f"❌ ws.py not found in {ROOT_DIR}\n")
            return

        # Run the script and capture output
        process = subprocess.Popen(
            [sys.executable, ws_py, path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        if stdout:
            append_output(stdout)
        if stderr:
            append_output(stderr)
    except Exception as e:
        append_output(f"❌ Error running script: {e}\n")
    append_output("\n✅ Script finished!\n")

# ----------------------------
# Tkinter GUI console
# ----------------------------
def append_output(text):
    output_box.configure(state='normal')
    output_box.insert(tk.END, text)
    output_box.see(tk.END)
    output_box.configure(state='disabled')

def clear_output():
    output_box.configure(state='normal')
    output_box.delete('1.0', tk.END)
    output_box.configure(state='disabled')

def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select a WS file",
        filetypes=[("WevScript Files", "*.ws")]
    )
    if file_path:
        script_path_var.set(file_path)

def run_button_action():
    path = script_path_var.get()
    run_ws_file(path)

# ----------------------------
# Setup main window
# ----------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

root = tk.Tk()
root.title("WevScript Console")
root.geometry("800x600")
root.resizable(True, True)

# Path input
script_path_var = tk.StringVar()
path_frame = tk.Frame(root)
path_frame.pack(fill='x', padx=5, pady=5)

path_entry = tk.Entry(path_frame, textvariable=script_path_var, font=("Consolas", 12))
path_entry.pack(side='left', fill='x', expand=True, padx=(0,5))

browse_button = tk.Button(path_frame, text="Browse", command=browse_file)
browse_button.pack(side='left', padx=(0,5))

run_button = tk.Button(path_frame, text="Run Script", command=run_button_action)
run_button.pack(side='left', padx=(0,5))

clear_button = tk.Button(path_frame, text="Clear Output", command=clear_output)
clear_button.pack(side='left')

# Output console
output_box = scrolledtext.ScrolledText(root, font=("Consolas", 12), state='disabled', bg="black", fg="white")
output_box.pack(fill='both', expand=True, padx=5, pady=(0,5))

append_output("🔥 WevScript Console ready!\n")
append_output("Enter a WS script path and press Run.\n\n")

root.mainloop()
