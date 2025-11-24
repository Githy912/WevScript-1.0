import tkinter as tk
from tkinter import scrolledtext, filedialog
import os, sys, re, urllib.request

# ----------------------------
# Root directories
# ----------------------------
ROOT_DIR = r"D:\WS"
MODULES_DIR = os.path.join(ROOT_DIR, "modules")
os.makedirs(MODULES_DIR, exist_ok=True)

# ----------------------------
# Constants & helpers
# ----------------------------
constants = {"PI": 3.14159265359, "E": 2.71828182846}
installed_modules = {}

def fetch_module(url, save_as=None):
    """Download WS module into MODULES_DIR"""
    try:
        data = urllib.request.urlopen(url).read().decode("utf-8")
        if not save_as:
            save_as = os.path.basename(url)
        save_path = os.path.join(MODULES_DIR, save_as)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(data)
        installed_modules[save_as] = save_path
        return f"[LIB] Module {save_as} installed to modules folder."
    except Exception as e:
        return f"[LIB ERROR] {e}"

def evaluate_expr(expr, variables):
    """Evaluate WS expressions"""
    try:
        for k,v in variables.items():
            expr = expr.replace(k,str(v))
        for k,v in constants.items():
            expr = expr.replace(k,str(v))
        return eval(expr)
    except Exception as e:
        return f"[ERROR] {e}"

# ----------------------------
# WS Interpreter
# ----------------------------
class WSInterpreter:
    def __init__(self):
        self.vars = {}

    def exec_line(self, line):
        line = line.strip()
        if not line or line.startswith("--"):
            return ""
        lc = line.lower()

        if lc == "help":
            return "Commands: help, exit, list_modules, fetch <url>"
        if lc == "exit":
            sys.exit(0)
        if lc == "list_modules":
            return "Installed Modules: " + (", ".join(installed_modules.keys()) if installed_modules else "[None]")
        if lc.startswith("fetch"):
            parts = line.split(maxsplit=1)
            if len(parts) == 1:
                return "[LIB ERROR] Usage: fetch <url>"
            url = parts[1].strip()
            return fetch_module(url)

        # write()
        m = re.match(r'write\((.*)\)', line, re.IGNORECASE)
        if m:
            val = m.group(1).strip().strip('"').strip("'")
            val = val.replace("[","{").replace("]","}")
            return val.format(**self.vars)

        # set var = expr
        m = re.match(r'set (\w+)\s*=\s*(.*)', line, re.IGNORECASE)
        if m:
            var, expr = m.group(1), m.group(2)
            self.vars[var] = evaluate_expr(expr, self.vars)
            return ""

        # supply()
        m = re.match(r'supply\(["\'](.*)["\']\)', line, re.IGNORECASE)
        if m:
            mod = m.group(1)
            mod_path = os.path.join(MODULES_DIR, mod)
            if mod in installed_modules:
                return f"[LIB] Module {mod} loaded."
            elif os.path.isfile(mod_path):
                installed_modules[mod] = mod_path
                return f"[LIB] Module {mod} loaded from modules folder."
            else:
                return f"[LIB ERROR] Module {mod} not found."
        return f"[UNKNOWN] {line}"

# ----------------------------
# Tkinter Console
# ----------------------------
class WSConsole:
    def __init__(self):
        self.interpreter = WSInterpreter()
        self.root = tk.Tk()
        self.root.title("🔥 WevScript Console")
        self.root.geometry("800x500")

        # Output
        self.output = scrolledtext.ScrolledText(
            self.root, bg="black", fg="lime", insertbackground="lime", font=("Consolas", 12)
        )
        self.output.pack(fill="both", expand=True)

        # Input
        self.input = tk.Entry(self.root, bg="black", fg="white", insertbackground="white", font=("Consolas", 12))
        self.input.pack(fill="x")
        self.input.bind("<Return>", self.run_command)

        # Buttons
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(fill="x")
        self.run_btn = tk.Button(self.btn_frame, text="Run Script", command=self.browse_and_run)
        self.run_btn.pack(side="left")
        self.clear_btn = tk.Button(self.btn_frame, text="Clear", command=self.clear)
        self.clear_btn.pack(side="left")

        self.append_text("🖥️ WevScript Console ready! Type 'help' for commands or run a .ws script.")

    def append_text(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def clear(self):
        self.output.delete("1.0", tk.END)

    def browse_and_run(self):
        file = filedialog.askopenfilename(filetypes=[("WevScript Files","*.ws"),("All Files","*.*")])
        if file:
            self.run_script(file)

    def run_script(self, path):
        if not os.path.isfile(path):
            self.append_text(f"❌ File not found: {path}")
            return
        self.append_text(f"▶ Running script: {path}")
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                out = self.interpreter.exec_line(line.strip())
                if out:
                    self.append_text(out)
        self.append_text("✅ Script finished!")

    def run_command(self, event=None):
        cmd = self.input.get().strip()
        self.input.delete(0, tk.END)
        if not cmd:
            return
        self.append_text(f"> {cmd}")
        out = self.interpreter.exec_line(cmd)
        if out:
            self.append_text(out)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    console = WSConsole()
    console.run()
