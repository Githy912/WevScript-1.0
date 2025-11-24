import tkinter as tk
from tkinter import scrolledtext, filedialog
import os
import re

# ----------------------------
# ROOT / MODULES
# ----------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(ROOT_DIR, "modules")

# ----------------------------
# Built-in constants / modules
# ----------------------------
constants = {}
# Load constants.wsmod if exists
constants_path = os.path.join(MODULES_DIR, "constants.wsmod")
if os.path.isfile(constants_path):
    with open(constants_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("--"):
                continue
            parts = line.split("=")
            if len(parts) == 2:
                key, val = parts
                constants[key.strip()] = val.strip()

# ----------------------------
# Helpers
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

# ----------------------------
# WS Execution Engine
# ----------------------------
variables = {}

def run_ws_file(path):
    if not os.path.isfile(path):
        append_output(f"❌ File not found: {path}\n")
        return

    append_output(f"▶ Running: {path}\n\n")

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("--"):
            continue  # skip empty or comment lines

        # set variable: set a = 10
        m = re.match(r'set\s+(\w+)\s*=\s*(.+)', line)
        if m:
            var, val = m.groups()
            try:
                # replace constants
                for k in constants:
                    val = val.replace(k, str(constants[k]))
                variables[var] = eval(val, {}, variables)
            except:
                variables[var] = val.strip('"').strip("'")
            continue

        # write: write("Hello")
        m = re.match(r'write\(L?"(.*)"\)', line)
        if m:
            text = m.group(1)
            # replace [var] with value
            text = re.sub(r'\[(\w+)\]', lambda x: str(variables.get(x.group(1), x.group(1))), text)
            append_output(text + "\n")
            continue

        # read: set a = read("Prompt")
        m = re.match(r'set\s+(\w+)\s*=\s*read\("(.*)"\)', line)
        if m:
            var, prompt = m.groups()
            try:
                val = input(prompt)
                variables[var] = val
                append_output(f"{prompt}{val}\n")
            except:
                variables[var] = ""
            continue

        # TODO: add more WS syntax support (if, loops, etc.)

    append_output("\n✅ Script finished!\n")

def run_button_action():
    path = script_path_var.get()
    run_ws_file(path)

# ----------------------------
# Tkinter GUI
# ----------------------------
root = tk.Tk()
root.title("WevScript Console (Heart)")
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

append_output("🔥 WevScript Console (Heart) ready!\n")
append_output("Enter a WS script path and press Run.\n\n")

root.mainloop()
