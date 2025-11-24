import tkinter as tk
from tkinter import scrolledtext, filedialog
import os
import re

# ----------------------------
# ROOT / MODULES
# ----------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(ROOT_DIR, "modules")

variables = {}
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
# Boolean mapping
# ----------------------------
def map_booleans(expr):
    expr = expr.replace("nor", "not (").replace("either", "(").replace("neither", "not (")
    expr = expr.replace("true", "True").replace("false", "False")
    return expr

# ----------------------------
# Evaluate L-string expressions
# ----------------------------
def eval_brackets(match):
    expr = match.group(1).strip().rstrip(';')
    expr = map_booleans(expr)
    try:
        return str(eval(expr, {}, variables))
    except Exception:
        return f"[{expr}]"

# ----------------------------
# WS Execution Engine
# ----------------------------
def run_ws_file(path):
    if not os.path.isfile(path):
        append_output(f"❌ File not found: {path}\n")
        return

    append_output(f"▶ Running: {path}\n\n")
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    block_stack = []
    i = 0
    while i < len(lines):
        raw_line = lines[i].strip()
        i += 1
        if not raw_line or raw_line.startswith("--"):
            continue

        # ------------------------
        # set variable
        m = re.match(r'set\s+(\w+)\s*=\s*(.+)', raw_line)
        if m:
            var, val = m.groups()
            val = val.strip().rstrip(";")
            try:
                for k in constants:
                    val = val.replace(k, str(constants[k]))
                variables[var] = eval(map_booleans(val), {}, variables)
            except:
                variables[var] = val.strip('"').strip("'")
            continue

        # ------------------------
        # read input
        m = re.match(r'set\s+(\w+)\s*=\s*read\("(.*)"\)', raw_line)
        if m:
            var, prompt = m.groups()
            val = input(prompt)
            variables[var] = val
            append_output(f"{prompt}{val}\n")
            continue

        # ------------------------
        # write
        m = re.match(r'write\(L?"(.*)"\)', raw_line)
        if m:
            text = re.sub(r'\[(.*?)\]', eval_brackets, m.group(1))
            append_output(text + "\n")
            continue

        # ------------------------
        # If / Else / Loops detection (basic)
        # Simplified: store block info
        # Here we can expand for full nested blocks, do-while, for-do, if-for, etc.
        if re.match(r'if\s*\((.*)\)\s*{', raw_line):
            condition = re.match(r'if\s*\((.*)\)\s*{', raw_line).group(1)
            block_stack.append(("if", eval(map_booleans(condition), {}, variables)))
            continue

        if raw_line.startswith("else"):
            m_cond = re.match(r'else\((.*)\)\s*{', raw_line)
            if m_cond:
                condition = m_cond.group(1)
                block_stack.append(("elseif", eval(map_booleans(condition), {}, variables)))
            else:
                block_stack.append(("else", True))
            continue

        if raw_line.startswith("while") or raw_line.startswith("do") or raw_line.startswith("for"):
            # For now, mark loop start (full implementation needs nested stack and iteration)
            block_stack.append(("loop", raw_line))
            continue

        if raw_line == "}":
            if block_stack:
                block_stack.pop()
            continue

    append_output("\n✅ Script finished!\n")

def run_button_action():
    path = script_path_var.get()
    run_ws_file(path)

# ----------------------------
# Tkinter GUI
# ----------------------------
root = tk.Tk()
root.title("🔥 WevScript Console (Heart)")
root.geometry("1000x700")
root.resizable(True, True)

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

output_box = scrolledtext.ScrolledText(root, font=("Consolas", 12), state='disabled', bg="black", fg="white")
output_box.pack(fill='both', expand=True, padx=5, pady=(0,5))

append_output("🔥 WevScript Console (Heart) ready!\n")
append_output("Enter a WS script path and press Run.\n\n")

root.mainloop()
