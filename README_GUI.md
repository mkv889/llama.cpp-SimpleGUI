# llama.cpp GUI Interface

A simple, user-friendly GUI interface for interacting with llama.cpp locally on Windows (and other platforms).

## Features

- **Automatic Binary Detection**: Automatically detects llama.cpp binaries installed via winget on Windows
- **Model Selection**: Easy file browser for selecting GGUF model files
- **Inference Parameters**: Configure common parameters like:
  - Max tokens (1-4096)
  - Temperature (0.0-2.0)
  - Top-p (0.0-1.0)
  - Top-k (1-100)
- **Prompt Input**: Multi-line text area for entering prompts
- **Real-time Output**: Live streaming of inference output
- **Process Control**: Start, stop, and monitor inference execution
- **Cross-platform**: Built with Tkinter for compatibility across Windows, macOS, and Linux

## Requirements

- Python 3.6 or higher
- Tkinter (usually included with Python)
- llama.cpp binaries installed (via winget on Windows or built from source)

## Installation

1. Ensure llama.cpp is installed:
   - **Windows**: `winget install llama.cpp` (or download from releases)
   - **Other platforms/Installation Methods**: See the official [llama.cpp repo.](https://github.com/ggml-org/llama.cpp)

2. No additional Python packages are required - the GUI uses only standard library modules!

## Usage

### Running the GUI

```bash
# Simply run the script
python llama_gui.py

# Or make it executable and run directly
chmod +x llama_gui.py
./llama_gui.py
```

### Using the GUI

1. **Binary Path**: The GUI will automatically detect your llama-cli binary. If not found, use the "Browse..." button to locate it manually.

2. **Select Model**: Click "Browse..." next to "Model File" to select your GGUF model file.

3. **Configure Parameters**: Adjust inference parameters as needed:
   - **Max Tokens**: Maximum number of tokens to generate
   - **Temperature**: Controls randomness (higher = more random)
   - **Top-p**: Nucleus sampling parameter
   - **Top-k**: Top-k sampling parameter

4. **Enter Prompt**: Type your prompt in the text area.

5. **Run Inference**: Click "Run Inference" to start generation. Output will stream in real-time to the output area.

6. **Stop Inference**: Click "Stop" to terminate the running inference process if needed.

## Example Workflow

1. Launch the GUI
2. Verify the binary path shows your llama-cli location
3. Browse and select a model (e.g., `llama-2-7b-chat.Q4_K_M.gguf`)
4. Enter a prompt like: "Explain quantum computing in simple terms."
5. Adjust parameters (e.g., max tokens: 256, temperature: 0.7)
6. Click "Run Inference"
7. Watch as the model generates text in real-time
8. Copy the output or run another inference with different parameters

## Binary Detection

The GUI automatically searches for llama-cli in the following locations (in order):

1. **Windows winget paths**:
   - `%LOCALAPPDATA%\Microsoft\WinGet\Packages\`
   - `%PROGRAMFILES%\llama.cpp\`
   - `%PROGRAMFILES(X86)%\llama.cpp\`

2. **System PATH**: Checks if `llama-cli` is in your PATH environment variable

3. **Local build**: Looks for `build/bin/llama-cli` in common build directories

If the binary is not found automatically, you can manually browse to its location.

## Troubleshooting

### Binary Not Found

If the GUI shows "llama-cli not found":
1. Verify llama.cpp is installed correctly
2. Use the "Browse..." button to manually locate the binary
3. On Windows, check winget installation: `winget list llama.cpp`

### Model File Issues

If you get model loading errors:
1. Ensure the file has a `.gguf` extension
2. Verify the file is not corrupted
3. Check you have read permissions for the file

### Inference Errors

If inference fails:
1. Check the output area for error messages
2. Verify your model file is compatible with your llama.cpp version
3. Try reducing max_tokens if you're running out of memory
4. Ensure the binary has execute permissions (Linux/macOS)

## Technical Details

- **GUI Framework**: Tkinter (Python standard library)
- **Process Execution**: Uses `subprocess.Popen` for running llama-cli
- **Threading**: Inference runs in a separate thread to keep GUI responsive
- **Output Streaming**: Real-time line-by-line output streaming

## Command Line Arguments

The GUI builds commands like:
```bash
llama-cli -m <model> -p <prompt> -n <max_tokens> --temp <temperature> --top-p <top_p> --top-k <top_k>
```

## License

This GUI tool is part of the llama.cpp project and is licensed under the MIT License.
