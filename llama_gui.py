#!/usr/bin/env python3
"""
Simple GUI interface for interacting with llama.cpp binaries.
This tool provides an easy way to select models, configure parameters,
and run inference with llama.cpp installed via winget.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import os
import platform
import threading


class LlamaCppGUI:
    """Main GUI application for llama.cpp interaction."""

    def __init__(self, root):
        self.root = root
        self.root.title("llama.cpp GUI")
        self.root.geometry("900x700")

        # Initialize variables
        self.model_path = tk.StringVar()
        self.prompt_text = tk.StringVar()
        self.max_tokens = tk.IntVar(value=512)
        self.temperature = tk.DoubleVar(value=0.8)
        self.top_p = tk.DoubleVar(value=0.95)
        self.top_k = tk.IntVar(value=40)
        self.llama_binary = tk.StringVar()
        self.is_running = False
        self.process = None

        # Detect llama.cpp binary
        self.detect_llama_binary()

        # Setup GUI
        self.setup_ui()

    def detect_llama_binary(self):
        """Detect the llama-cli binary path, prioritizing winget installation."""
        # Common winget installation paths on Windows
        if platform.system() == "Windows":
            winget_paths = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages'),
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'llama.cpp'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'llama.cpp'),
            ]

            # Search for llama-cli in winget paths
            for base_path in winget_paths:
                if os.path.exists(base_path):
                    for root, dirs, files in os.walk(base_path):
                        if 'llama-cli.exe' in files:
                            binary_path = os.path.join(root, 'llama-cli.exe')
                            self.llama_binary.set(binary_path)
                            return
                        # Also check for llama-cli without .exe extension
                        if 'llama-cli' in files:
                            binary_path = os.path.join(root, 'llama-cli')
                            self.llama_binary.set(binary_path)
                            return

        # Check if llama-cli is in PATH
        binary_name = 'llama-cli.exe' if platform.system() == "Windows" else 'llama-cli'

        # Check PATH environment variable
        for path_dir in os.environ.get('PATH', '').split(os.pathsep):
            binary_path = os.path.join(path_dir, binary_name)
            if os.path.isfile(binary_path) and os.access(binary_path, os.X_OK):
                self.llama_binary.set(binary_path)
                return

        # Check build directory (for development)
        build_dirs = ['build/bin', './build/bin', '../build/bin']
        for build_dir in build_dirs:
            binary_path = os.path.join(build_dir, binary_name)
            if os.path.isfile(binary_path):
                self.llama_binary.set(os.path.abspath(binary_path))
                return

        # Not found
        self.llama_binary.set("llama-cli not found")

    def setup_ui(self):
        """Setup the GUI interface."""
        # Create main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        current_row = 0

        # Binary path section
        ttk.Label(main_frame, text="llama-cli Binary:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.llama_binary, width=50).grid(row=current_row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_binary).grid(row=current_row, column=2, padx=5, pady=5)
        current_row += 1

        # Model selection section
        ttk.Label(main_frame, text="Model File:").grid(row=current_row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.model_path, width=50).grid(row=current_row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_model).grid(row=current_row, column=2, padx=5, pady=5)
        current_row += 1

        # Parameters section
        params_frame = ttk.LabelFrame(main_frame, text="Inference Parameters", padding="10")
        params_frame.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(3, weight=1)
        current_row += 1

        # Max tokens
        ttk.Label(params_frame, text="Max Tokens:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(params_frame, from_=1, to=4096, textvariable=self.max_tokens, width=15).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Temperature
        ttk.Label(params_frame, text="Temperature:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(params_frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.temperature, width=15).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        # Top-p
        ttk.Label(params_frame, text="Top-p:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(params_frame, from_=0.0, to=1.0, increment=0.05, textvariable=self.top_p, width=15).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Top-k
        ttk.Label(params_frame, text="Top-k:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(params_frame, from_=1, to=100, textvariable=self.top_k, width=15).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        # Prompt section
        ttk.Label(main_frame, text="Prompt:").grid(row=current_row, column=0, sticky=(tk.W, tk.N), pady=5)
        current_row += 1

        self.prompt_entry = scrolledtext.ScrolledText(main_frame, width=70, height=8, wrap=tk.WORD)
        self.prompt_entry.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(current_row, weight=1)
        current_row += 1

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=current_row, column=0, columnspan=3, pady=10)
        current_row += 1

        self.run_button = ttk.Button(button_frame, text="Run Inference", command=self.run_inference)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_inference, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=5)

        # Output section
        ttk.Label(main_frame, text="Output:").grid(row=current_row, column=0, sticky=(tk.W, tk.N), pady=5)
        current_row += 1

        self.output_text = scrolledtext.ScrolledText(main_frame, width=70, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(current_row, weight=2)
        current_row += 1

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

    def browse_binary(self):
        """Browse for llama-cli binary."""
        if platform.system() == "Windows":
            filetypes = [("Executable files", "*.exe"), ("All files", "*.*")]
        else:
            filetypes = [("All files", "*.*")]

        filename = filedialog.askopenfilename(
            title="Select llama-cli binary",
            filetypes=filetypes
        )

        if filename:
            self.llama_binary.set(filename)

    def browse_model(self):
        """Browse for GGUF model file."""
        filename = filedialog.askopenfilename(
            title="Select GGUF model file",
            filetypes=[("GGUF files", "*.gguf"), ("All files", "*.*")]
        )

        if filename:
            self.model_path.set(filename)

    def clear_output(self):
        """Clear the output text area."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def append_output(self, text):
        """Append text to the output area."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def validate_inputs(self):
        """Validate user inputs before running inference."""
        # Check binary path
        binary_path = self.llama_binary.get()
        if not binary_path or binary_path == "llama-cli not found":
            messagebox.showerror("Error", "Please specify the llama-cli binary path.")
            return False

        if not os.path.isfile(binary_path):
            messagebox.showerror("Error", f"Binary not found: {binary_path}")
            return False

        # Check model path
        model_path = self.model_path.get()
        if not model_path:
            messagebox.showerror("Error", "Please select a model file.")
            return False

        if not os.path.isfile(model_path):
            messagebox.showerror("Error", f"Model file not found: {model_path}")
            return False

        # Check prompt
        prompt = self.prompt_entry.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a prompt.")
            return False

        return True

    def run_inference(self):
        """Run llama.cpp inference in a separate thread."""
        if not self.validate_inputs():
            return

        if self.is_running:
            messagebox.showwarning("Warning", "Inference is already running.")
            return

        # Disable run button, enable stop button
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_running = True

        # Clear previous output
        self.clear_output()

        # Start inference in a separate thread
        thread = threading.Thread(target=self._run_inference_thread, daemon=True)
        thread.start()

    def _run_inference_thread(self):
        """Thread function to run inference."""
        binary_path = ""
        try:
            binary_path = self.llama_binary.get()
            model_path = self.model_path.get()
            prompt = self.prompt_entry.get(1.0, tk.END).strip()

            # Build command
            cmd = [
                binary_path,
                "-m", model_path,
                "-p", prompt,
                "-n", str(self.max_tokens.get()),
                "--temp", str(self.temperature.get()),
                "--top-p", str(self.top_p.get()),
                "--top-k", str(self.top_k.get()),
            ]

            self.root.after(0, lambda: self.status_var.set("Running inference..."))
            self.root.after(0, lambda: self.append_output(f"Command: {' '.join(cmd)}\n\n"))

            # Run the process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Read output line by line
            if self.process.stdout:
                for line in self.process.stdout:
                    if not self.is_running:
                        break
                    self.root.after(0, lambda output_line=line: self.append_output(output_line))

            # Wait for process to complete
            self.process.wait()

            returncode = self.process.returncode if self.process else -1
            if returncode == 0:
                self.root.after(0, lambda: self.status_var.set("Inference completed successfully"))
                self.root.after(0, lambda: self.append_output("\n\n=== Inference completed successfully ===\n"))
            else:
                self.root.after(0, lambda: self.status_var.set(f"Inference failed with code {returncode}"))
                self.root.after(0, lambda: self.append_output(f"\n\n=== Inference failed with exit code {returncode} ===\n"))

        except FileNotFoundError:
            self.root.after(0, lambda bp=binary_path: messagebox.showerror("Error", f"Binary not found: {bp}"))
            self.root.after(0, lambda: self.status_var.set("Error: Binary not found"))
        except Exception as error:
            error_msg = str(error)
            self.root.after(0, lambda em=error_msg: messagebox.showerror("Error", f"Failed to run inference: {em}"))
            self.root.after(0, lambda em=error_msg: self.status_var.set(f"Error: {em}"))
        finally:
            self.is_running = False
            self.process = None
            self.root.after(0, lambda: self.run_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))

    def stop_inference(self):
        """Stop the running inference process."""
        if self.process and self.is_running:
            self.is_running = False
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

            self.status_var.set("Inference stopped by user")
            self.append_output("\n\n=== Inference stopped by user ===\n")
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)


def main():
    """Main entry point."""
    root = tk.Tk()
    LlamaCppGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
