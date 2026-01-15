# llama.cpp SimpleGUI

A lightweight, cross-platform Tkinter GUI for running llama.cpp locally. The repo
ships with two frontends:

- **llama_gui.py**: Run single prompts with `llama-cli` and stream output live.
- **llama_server_gui.py**: Configure and monitor the OpenAI-compatible
  `llama-server` endpoint for use by other applications.

## Features

### Inference GUI (llama_gui.py)

- Automatic detection of `llama-cli` (winget, PATH, common build folders)
- Model file browser for GGUF files
- Common inference controls (max tokens, temperature, top-p, top-k)
- Streaming output with start/stop controls

### Server GUI (llama_server_gui.py)

- Configure host/port for the OpenAI-compatible endpoint
- Set model path, temperature, context size, and thread count
- Start/stop server process with restart-on-change controls
- Live monitoring of server health and loaded model via `/health` and `/v1/models`

## Requirements

- Python 3.6+
- Tkinter (bundled with most Python installs)
- llama.cpp binaries:
  - `llama-cli` for the inference GUI
  - `llama-server` (or `server`) for the server GUI

## Installation

1. Install llama.cpp:
   - **Windows**: `winget install llama.cpp`
   - **Other platforms**: Build from source or download binaries from
     [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
2. No additional Python dependencies are required.

## Quick Start

### Run the Inference GUI

```bash
python llama_gui.py
# or
chmod +x llama_gui.py
./llama_gui.py
```

### Run the Server GUI

```bash
python llama_server_gui.py
# or
chmod +x llama_server_gui.py
./llama_server_gui.py
```

The server GUI displays an OpenAI-compatible base URL (for example
`http://127.0.0.1:8080/v1`) that other applications can use.

## Using the Inference GUI

1. Confirm or browse to the `llama-cli` binary.
2. Select a `.gguf` model file.
3. Configure max tokens, temperature, top-p, and top-k.
4. Enter your prompt and click **Run Inference**.
5. Use **Stop** to terminate long-running output.

## Using the Server GUI

1. Confirm or browse to the `llama-server`/`server` binary.
2. Select the `.gguf` model you want to host.
3. Configure host/port and server parameters (temperature, context size, threads).
4. Click **Start Server** to launch the endpoint.
5. Use **Restart with Settings** to apply updated values.
6. Confirm status and loaded model in the monitoring panel.

Example health check:

```bash
curl http://127.0.0.1:8080/health
```

Example model listing (OpenAI-compatible):

```bash
curl http://127.0.0.1:8080/v1/models
```

## Binary Detection

Both GUIs search in the following order:

1. **Windows winget paths** (when applicable):
   - `%LOCALAPPDATA%\Microsoft\WinGet\Packages\`
   - `%PROGRAMFILES%\llama.cpp\`
   - `%PROGRAMFILES(X86)%\llama.cpp\`
2. **System PATH** (`llama-cli`, `llama-server` / `server`)
3. **Local builds**: `build/bin`, `./build/bin`, `../build/bin`

If a binary is not found, use the **Browse...** button to locate it manually.

## Command Examples

Inference GUI builds commands like:

```bash
llama-cli -m <model> -p <prompt> -n <max_tokens> --temp <temperature> --top-p <top_p> --top-k <top_k>
```

Server GUI builds commands like:

```bash
llama-server --model <model> --host <host> --port <port> --temp <temperature> --ctx-size <context> --threads <threads>
```

## Troubleshooting

### Binary Not Found

- Confirm llama.cpp is installed or built locally.
- Use **Browse...** to select the correct binary.
- On Windows, verify the installation with `winget list llama.cpp`.

### Model File Issues

- Ensure the file has a `.gguf` extension and is readable.
- Confirm the model matches your llama.cpp build.

### Server Endpoint Offline

- Ensure the server is running and not blocked by a firewall.
- Confirm the host/port configuration matches the client.
- Check the output panel for startup errors.

## More Examples

See [EXAMPLE_GUI_USAGE.md](EXAMPLE_GUI_USAGE.md) for detailed walkthroughs and
parameter tips.
