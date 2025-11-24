import tkinter as tk
from tkinter import scrolledtext, filedialog
import os, subprocess, sys

# ----------------------------
# Root directories
# ----------------------------
ROOT_DIR = r"D:\WS"
MODULES_DIR = os.path.join(ROOT_DIR, "modules")
os.makedirs(MODULES_DIR, exist_ok=True)

# ----------------------------
# IDE
# ----------------------------
class WSIDE:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥 WevScript IDE")
        self.root.geometry("1000x700")

        # Editor
        self.editor = scrolledtext.ScrolledText(self.root, font=("Consolas", 12))
        self.editor.pack(fill="both", expand=True)

        # Button frame
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(fill="x")
        self.open_btn = tk.Button(self.btn_frame, text="Open", command=self.open_file)
        self.open_btn.pack(side="left", padx=5, pady=5)
        self.save_btn = tk.Button(self.btn_frame, text="Save", command=self.save_file)
        self.save_btn.pack(side="left", padx=5, pady=5)
        self.run_btn = tk.Button(self.btn_frame, text="Run", command=self.run_script)
        self.run_btn.pack(side="left", padx=5, pady=5)
        self.clear_btn = tk.Button(self.btn_frame, text="Clear Output", command=self.clear_output)
        self.clear_btn.pack(side="left", padx=5, pady=5)

        # Output box
        self.output = scrolledtext.ScrolledText(self.root, bg="black", fg="lime",
                                                insertbackground="lime", font=("Consolas", 12), height=10)
        self.output.pack(fill="x")

        self.current_file = None

    # ----------------------------
    # Output helpers
    # ----------------------------
    def append_output(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def clear_output(self):
        self.output.delete("1.0", tk.END)

    # ----------------------------
    # File operations
    # ----------------------------
    def open_file(self):
        file = filedialog.askopenfilename(filetypes=[("WevScript Files","*.ws"),("All Files","*.*")])
        if file:
            with open(file,"r",encoding="utf-8") as f:
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", f.read())
            self.current_file = file
            self.append_output(f"📂 Opened {file}")

    def save_file(self):
        if not self.current_file:
            file = filedialog.asksaveasfilename(defaultextension=".ws", filetypes=[("WevScript Files","*.ws"),("All Files","*.*")])
            if not file:
                return
            self.current_file = file
        with open(self.current_file,"w",encoding="utf-8") as f:
            f.write(self.editor.get("1.0", tk.END))
        self.append_output(f"💾 Saved {self.current_file}")

    # ----------------------------
    # Run script
    # ----------------------------
    def run_script(self):
        if not self.current_file:
            self.append_output("❌ Save a file first!")
            return
        self.append_output(f"▶ Running {self.current_file} ...")
        try:
            # Run using wscript.py (Tkinter console)
            subprocess.run([sys.executable, os.path.join(ROOT_DIR, "wscript.py")],
                           input=self.editor.get("1.0", tk.END), text=True)
            self.append_output("✅ Script finished!")
        except Exception as e:
            self.append_output(f"❌ Error: {e}")

    # ----------------------------
    # Main loop
    # ----------------------------
    def run(self):
        self.root.mainloop()

# ----------------------------
# Launch IDE
# ----------------------------
if __name__ == "__main__":
    ide = WSIDE()
    ide.run()
