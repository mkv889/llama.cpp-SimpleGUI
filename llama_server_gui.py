#!/usr/bin/env python3
"""
GUI interface for configuring, running, and monitoring llama.cpp's server.
This tool manages an OpenAI-compatible endpoint with real-time status updates.
"""

import json
import os
import platform
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from urllib import error as url_error
from urllib import request as url_request


class LlamaCppServerGUI:
    """GUI application for running and monitoring llama.cpp server."""

    RESTART_POLL_DELAY_MS = 100

    def __init__(self, root):
        self.root = root
        self.root.title("llama.cpp Server GUI")
        self.root.geometry("980x760")

        # Initialize variables
        self.server_binary = tk.StringVar()
        self.model_path = tk.StringVar()
        self.host = tk.StringVar(value="127.0.0.1")
        self.port = tk.IntVar(value=8080)
        self.temperature = tk.DoubleVar(value=0.8)
        self.context_size = tk.IntVar(value=4096)
        self.threads = tk.IntVar(value=8)
        self.endpoint_url = tk.StringVar()
        self.server_status = tk.StringVar(value="Stopped")
        self.current_model = tk.StringVar(value="Unknown")
        self.is_running = False
        self.process = None

        # Detect llama.cpp server binary
        self.detect_server_binary()

        # Setup GUI
        self.setup_ui()
        self.update_endpoint_url()

        # Start monitoring loop
        self.root.after(2000, self.poll_server_status)

    def detect_server_binary(self):
        """Detect the llama-server binary path, prioritizing winget installation."""
        binary_basenames = ["llama-server", "server"]
        if platform.system() == "Windows":
            binary_names = [f"{name}.exe" for name in binary_basenames]
        else:
            binary_names = binary_basenames

        # Common winget installation paths on Windows
        if platform.system() == "Windows":
            winget_paths = []
            local_appdata = os.environ.get("LOCALAPPDATA")
            program_files = os.environ.get("PROGRAMFILES")
            program_files_x86 = os.environ.get("PROGRAMFILES(X86)")

            if local_appdata:
                winget_paths.append(os.path.join(local_appdata, "Microsoft", "WinGet", "Packages"))
            if program_files:
                winget_paths.append(os.path.join(program_files, "llama.cpp"))
            if program_files_x86:
                winget_paths.append(os.path.join(program_files_x86, "llama.cpp"))

            for base_path in winget_paths:
                if os.path.exists(base_path):
                    for walk_root, dirs, files in os.walk(base_path):
                        depth = os.path.relpath(walk_root, base_path).count(os.sep)
                        if depth > 4:
                            dirs[:] = []
                            continue
                        for candidate in binary_names:
                            if candidate in files:
                                binary_path = os.path.join(walk_root, candidate)
                                self.server_binary.set(binary_path)
                                return

        for path_dir in filter(None, os.environ.get("PATH", "").split(os.pathsep)):
            for candidate in binary_names:
                binary_path = os.path.join(path_dir, candidate)
                if os.path.isfile(binary_path) and os.access(binary_path, os.X_OK):
                    self.server_binary.set(binary_path)
                    return

        build_dirs = ["build/bin", "./build/bin", "../build/bin"]
        for build_dir in build_dirs:
            for candidate in binary_names:
                binary_path = os.path.join(build_dir, candidate)
                if os.path.isfile(binary_path):
                    self.server_binary.set(os.path.abspath(binary_path))
                    return

        self.server_binary.set("llama-server not found")

    def setup_ui(self):
        """Setup the GUI interface."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        current_row = 0

        ttk.Label(main_frame, text="llama-server Binary:").grid(
            row=current_row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.server_binary, width=50).grid(
            row=current_row, column=1, sticky=(tk.W, tk.E), pady=5
        )
        ttk.Button(main_frame, text="Browse...", command=self.browse_binary).grid(
            row=current_row, column=2, padx=5, pady=5
        )
        current_row += 1

        ttk.Label(main_frame, text="Model File:").grid(
            row=current_row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.model_path, width=50).grid(
            row=current_row, column=1, sticky=(tk.W, tk.E), pady=5
        )
        ttk.Button(main_frame, text="Browse...", command=self.browse_model).grid(
            row=current_row, column=2, padx=5, pady=5
        )
        current_row += 1

        endpoint_frame = ttk.LabelFrame(main_frame, text="Endpoint Configuration", padding="10")
        endpoint_frame.grid(
            row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )
        endpoint_frame.columnconfigure(1, weight=1)
        endpoint_frame.columnconfigure(3, weight=1)
        current_row += 1

        ttk.Label(endpoint_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        host_entry = ttk.Entry(endpoint_frame, textvariable=self.host, width=20)
        host_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(endpoint_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        port_entry = ttk.Spinbox(endpoint_frame, from_=1, to=65535, textvariable=self.port, width=10)
        port_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(endpoint_frame, text="OpenAI Base URL:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        endpoint_entry = ttk.Entry(endpoint_frame, textvariable=self.endpoint_url, width=45, state="readonly")
        endpoint_entry.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)

        self.host.trace_add("write", self.update_endpoint_url)
        self.port.trace_add("write", self.update_endpoint_url)

        params_frame = ttk.LabelFrame(main_frame, text="Server Parameters", padding="10")
        params_frame.grid(
            row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(3, weight=1)
        current_row += 1

        ttk.Label(params_frame, text="Temperature:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Spinbox(
            params_frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.temperature, width=15
        ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(params_frame, text="Context Size:").grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=5
        )
        ttk.Spinbox(
            params_frame, from_=256, to=32768, increment=256, textvariable=self.context_size, width=15
        ).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(params_frame, text="Threads:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Spinbox(params_frame, from_=1, to=256, textvariable=self.threads, width=15).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )

        monitor_frame = ttk.LabelFrame(main_frame, text="Monitoring", padding="10")
        monitor_frame.grid(
            row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )
        monitor_frame.columnconfigure(1, weight=1)
        current_row += 1

        ttk.Label(monitor_frame, text="Server Status:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(monitor_frame, textvariable=self.server_status).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )
        ttk.Label(monitor_frame, text="Loaded Model:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(monitor_frame, textvariable=self.current_model).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        ttk.Button(monitor_frame, text="Refresh Now", command=self.poll_server_status).grid(
            row=0, column=2, rowspan=2, padx=5, pady=5
        )

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=current_row, column=0, columnspan=3, pady=10)
        current_row += 1

        self.start_button = ttk.Button(button_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.apply_button = ttk.Button(
            button_frame, text="Restart with Settings", command=self.apply_settings
        )
        self.apply_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=5)

        ttk.Label(main_frame, text="Server Output:").grid(
            row=current_row, column=0, sticky=(tk.W, tk.N), pady=5
        )
        current_row += 1

        self.output_text = scrolledtext.ScrolledText(
            main_frame, width=80, height=16, wrap=tk.WORD, state=tk.DISABLED
        )
        self.output_text.grid(
            row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )
        main_frame.rowconfigure(current_row, weight=2)
        current_row += 1

        self.status_var = tk.StringVar(value="Ready to start server.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

    def update_endpoint_url(self, *_):
        """Update the OpenAI-compatible endpoint URL."""
        host = self.host.get().strip() or "127.0.0.1"
        try:
            port = self.port.get()
        except tk.TclError:
            port = 8080

        if not isinstance(port, int) or port < 1 or port > 65535:
            port = 8080

        self.endpoint_url.set(f"http://{host}:{port}/v1")

    def browse_binary(self):
        """Browse for llama-server binary."""
        if platform.system() == "Windows":
            filetypes = [("Executable files", "*.exe"), ("All files", "*.*")]
        else:
            filetypes = [("All files", "*.*")]

        filename = filedialog.askopenfilename(title="Select llama-server binary", filetypes=filetypes)

        if filename:
            self.server_binary.set(filename)

    def browse_model(self):
        """Browse for GGUF model file."""
        filename = filedialog.askopenfilename(
            title="Select GGUF model file", filetypes=[("GGUF files", "*.gguf"), ("All files", "*.*")]
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

    def set_button_states(self, start_state, stop_state, apply_state):
        """Set the control button states together."""
        self.start_button.config(state=start_state)
        self.stop_button.config(state=stop_state)
        self.apply_button.config(state=apply_state)

    def validate_inputs(self):
        """Validate user inputs before running server."""
        binary_path = self.server_binary.get()
        if not binary_path or binary_path == "llama-server not found":
            messagebox.showerror("Error", "Please specify the llama-server binary path.")
            return False

        if not os.path.isfile(binary_path):
            messagebox.showerror("Error", f"Binary not found: {binary_path}")
            return False

        model_path = self.model_path.get()
        if not model_path:
            messagebox.showerror("Error", "Please select a model file.")
            return False

        if not os.path.isfile(model_path):
            messagebox.showerror("Error", f"Model file not found: {model_path}")
            return False

        if not self.host.get().strip():
            messagebox.showerror("Error", "Please enter a host address.")
            return False

        try:
            port = self.port.get()
            if port < 1 or port > 65535:
                raise ValueError("Port out of range")
        except (tk.TclError, ValueError):
            messagebox.showerror("Error", "Please enter a valid port (1-65535).")
            return False

        return True

    def build_command(self):
        """Build the llama-server command based on settings."""
        cmd = [
            self.server_binary.get(),
            "--model",
            self.model_path.get(),
            "--host",
            self.host.get().strip(),
            "--port",
            str(self.port.get()),
            "--temp",
            str(self.temperature.get()),
            "--ctx-size",
            str(self.context_size.get()),
            "--threads",
            str(self.threads.get()),
        ]
        return cmd

    def start_server(self):
        """Start the llama.cpp server in a separate thread."""
        if not self.validate_inputs():
            return

        if self.is_running:
            messagebox.showwarning("Warning", "Server is already running.")
            return

        self.is_running = True
        self.set_button_states(tk.DISABLED, tk.NORMAL, tk.NORMAL)
        self.server_status.set("Starting...")
        self.clear_output()

        thread = threading.Thread(target=self._run_server_thread, daemon=True)
        thread.start()

    def apply_settings(self):
        """Apply new settings by restarting the server if needed."""
        if self.is_running:
            if not messagebox.askyesno(
                "Restart Server", "Apply settings by restarting the server now?"
            ):
                return
            self.stop_server()
            self._restart_server_after_stop()
            return
        self.start_server()

    def _restart_server_after_stop(self, delay_ms=None):
        """Restart the server once the previous process has fully stopped."""
        if delay_ms is None:
            delay_ms = self.RESTART_POLL_DELAY_MS

        if self.is_running:
            self._schedule_restart_check(delay_ms)
            return
        process = self.process
        if process is None:
            self.start_server()
            return
        if process.poll() is None:
            self._schedule_restart_check(delay_ms)
            return
        self.start_server()

    def _schedule_restart_check(self, delay_ms):
        """Schedule the next restart readiness check."""
        self.root.after(delay_ms, self._restart_server_after_stop, delay_ms)

    def _run_server_thread(self):
        """Thread function to run the llama.cpp server."""
        try:
            binary_path = self.server_binary.get()
            cmd = self.build_command()
            self.root.after(0, self.status_var.set, "Launching llama.cpp server...")
            self.root.after(0, self.append_output, f"Command: {' '.join(cmd)}\n\n")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            self.root.after(0, self.server_status.set, "Running")

            if self.process.stdout:
                for line in self.process.stdout:
                    if not self.is_running:
                        break
                    self.root.after(0, self.append_output, line)

            self.process.wait()

            returncode = self.process.returncode if self.process else -1
            if returncode == 0 and self.is_running:
                self.root.after(0, self.status_var.set, "Server exited normally.")
            elif returncode != 0:
                self.root.after(0, self.status_var.set, f"Server exited with code {returncode}.")

        except FileNotFoundError:
            self.root.after(0, messagebox.showerror, "Error", f"Binary not found: {binary_path}")
            self.root.after(0, self.status_var.set, "Error: Binary not found")
        except Exception as error:
            error_msg = str(error)
            self.root.after(0, messagebox.showerror, "Error", f"Failed to start server: {error_msg}")
            self.root.after(0, self.status_var.set, f"Error: {error_msg}")
        finally:
            self.is_running = False
            self.process = None
            self.root.after(0, self.set_button_states, tk.NORMAL, tk.DISABLED, tk.NORMAL)
            self.root.after(0, self.server_status.set, "Stopped")

    def stop_server(self):
        """Stop the running server process."""
        if self.process and self.is_running:
            self.is_running = False
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

            self.status_var.set("Server stopped by user.")
            self.append_output("\n\n=== Server stopped by user ===\n")
            self.set_button_states(tk.NORMAL, tk.DISABLED, tk.NORMAL)
            self.server_status.set("Stopped")

    def poll_server_status(self):
        """Poll the server for status and loaded model information."""
        base_url = self.endpoint_url.get().strip()
        if not base_url:
            self.server_status.set("Invalid endpoint")
            self.current_model.set("Unknown")
            self.root.after(5000, self.poll_server_status)
            return

        health_url = base_url.replace("/v1", "/health")
        models_url = f"{base_url}/models"
        status_label = "Offline"
        model_label = "Unknown"

        try:
            with url_request.urlopen(health_url, timeout=2) as response:
                if response.status == 200:
                    status_label = "Online"
        except (url_error.URLError, ValueError):
            status_label = "Offline"

        if status_label == "Online":
            try:
                with url_request.urlopen(models_url, timeout=2) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                    data = payload.get("data", [])
                    if data:
                        model_label = data[0].get("id", "Unknown")
            except (url_error.URLError, ValueError, json.JSONDecodeError):
                model_label = "Unknown"

        self.server_status.set(status_label)
        self.current_model.set(model_label)
        self.root.after(5000, self.poll_server_status)


def main():
    """Main entry point."""
    root = tk.Tk()
    LlamaCppServerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
