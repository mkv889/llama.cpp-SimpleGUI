# llama.cpp GUI - Usage Examples

This document provides practical examples of using the llama.cpp GUI.

## Basic Usage Example

### 1. Starting the GUI

```bash
# Navigate to the llama.cpp directory
cd /path/to/llama.cpp

# Run the GUI
python llama_gui.py
```

### 2. First-Time Setup

When you first launch the GUI, you'll see:

```
┌─────────────────────────────────────────────────────────┐
│ llama.cpp GUI                                           │
├─────────────────────────────────────────────────────────┤
│ llama-cli Binary: [/path/to/llama-cli.exe] [Browse...] │
│ Model File:       [                      ] [Browse...] │
├─────────────────────────────────────────────────────────┤
│ Inference Parameters                                    │
│   Max Tokens: [512]     Temperature: [0.8]              │
│   Top-p:      [0.95]    Top-k:       [40]               │
├─────────────────────────────────────────────────────────┤
│ Prompt:                                                 │
│ ┌─────────────────────────────────────────────────────┐│
│ │                                                     ││
│ └─────────────────────────────────────────────────────┘│
│ [Run Inference] [Stop] [Clear Output]                  │
├─────────────────────────────────────────────────────────┤
│ Output:                                                 │
│ ┌─────────────────────────────────────────────────────┐│
│ │                                                     ││
│ └─────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────┤
│ Ready                                                   │
└─────────────────────────────────────────────────────────┘
```

## Example Scenarios

### Scenario 1: Simple Text Completion

**Goal**: Generate a continuation of a story

**Steps**:
1. Select model: `llama-2-7b.Q4_K_M.gguf`
2. Set parameters:
   - Max Tokens: 256
   - Temperature: 0.7
   - Top-p: 0.9
   - Top-k: 40
3. Enter prompt:
   ```
   Once upon a time in a magical forest, there lived
   ```
4. Click "Run Inference"
5. View the generated story continuation in the output area

**Expected Output**:
```
Command: llama-cli -m llama-2-7b.Q4_K_M.gguf -p "Once upon a time..." -n 256 --temp 0.7 --top-p 0.9 --top-k 40

Once upon a time in a magical forest, there lived a young fairy named Luna.
She had sparkling wings and could make flowers bloom with just a touch...
[continuing story text]

=== Inference completed successfully ===
```

### Scenario 2: Code Generation

**Goal**: Generate Python code

**Steps**:
1. Select model: `codellama-7b-instruct.Q4_K_M.gguf`
2. Set parameters:
   - Max Tokens: 512
   - Temperature: 0.2 (lower for more deterministic code)
   - Top-p: 0.95
   - Top-k: 40
3. Enter prompt:
   ```
   Write a Python function to calculate the Fibonacci sequence up to n terms:
   ```
4. Click "Run Inference"

**Expected Output**:
```python
def fibonacci(n):
    """
    Calculate the Fibonacci sequence up to n terms.
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib
```

### Scenario 3: Question Answering (Chat Model)

**Goal**: Ask questions to a chat model

**Steps**:
1. Select model: `llama-2-7b-chat.Q4_K_M.gguf`
2. Set parameters:
   - Max Tokens: 512
   - Temperature: 0.8
   - Top-p: 0.95
   - Top-k: 40
3. Enter prompt (using chat format):
   ```
   [INST] Explain how photosynthesis works in simple terms. [/INST]
   ```
4. Click "Run Inference"

### Scenario 4: Creative Writing with High Temperature

**Goal**: Generate creative and diverse text

**Steps**:
1. Select your model
2. Set parameters:
   - Max Tokens: 512
   - Temperature: 1.2 (higher for more creativity)
   - Top-p: 0.95
   - Top-k: 40
3. Enter a creative prompt
4. Click "Run Inference"

### Scenario 5: Deterministic Generation

**Goal**: Get consistent, deterministic output

**Steps**:
1. Select your model
2. Set parameters:
   - Max Tokens: 256
   - Temperature: 0.0 (or very low like 0.1)
   - Top-p: 1.0
   - Top-k: 1
3. Enter your prompt
4. Click "Run Inference"

**Note**: With temperature 0, the model will always generate the same output for the same prompt.

## Parameter Guidelines

### Max Tokens
- **Short answers**: 128-256
- **Medium responses**: 512-1024
- **Long form content**: 2048-4096

### Temperature
- **0.0-0.3**: Factual, deterministic (good for code, facts)
- **0.4-0.7**: Balanced (good for general use)
- **0.8-1.0**: Creative (good for stories, brainstorming)
- **1.1-2.0**: Very creative, may be less coherent

### Top-p (Nucleus Sampling)
- **0.9-0.95**: Recommended default
- **Higher (0.95-1.0)**: More diverse outputs
- **Lower (0.5-0.9)**: More focused outputs

### Top-k
- **20-40**: Recommended default
- **Higher (50-100)**: More diverse word choices
- **Lower (1-20)**: More predictable text

## Troubleshooting Examples

### Problem: Binary Not Found

**Error Message**: "llama-cli not found"

**Solution**:
1. Click "Browse..." next to "llama-cli Binary"
2. Navigate to your llama.cpp installation:
   - Windows (winget): `C:\Users\<username>\AppData\Local\Microsoft\WinGet\Packages\`
   - Manual install: `C:\Program Files\llama.cpp\bin\`
   - Built from source: `<llama.cpp-dir>\build\bin\`
3. Select `llama-cli.exe`

### Problem: Out of Memory

**Error Message**: "Failed to allocate memory" or similar

**Solution**:
1. Reduce "Max Tokens" (try 256 or 128)
2. Use a smaller/more quantized model (e.g., Q4_K_M instead of Q8_0)
3. Close other applications to free memory

### Problem: Slow Generation

**Observation**: Text generates very slowly

**Solution**:
1. Use a more quantized model (Q4_K_M is a good balance)
2. Reduce "Max Tokens"
3. Check that you're using GPU acceleration if available
4. Ensure no other heavy processes are running

## Tips and Tricks

### 1. Save Your Favorites
- Keep a text file with your favorite prompts
- Note which parameter combinations work best for different tasks

### 2. Experiment with Parameters
- Try different temperatures to see what works best for your use case
- Start conservative and adjust based on results

### 3. Use Appropriate Models
- Chat models for conversations (e.g., llama-2-chat)
- Code models for programming (e.g., codellama)
- Base models for completion tasks

### 4. Prompt Engineering
- Be specific in your prompts
- Provide examples when possible
- Use appropriate formatting for chat models

### 5. Monitor Output
- Watch the output area for errors or warnings
- The status bar shows progress and completion status

## Advanced Usage

### Running Multiple Inferences
1. Complete first inference
2. Review output
3. Modify prompt or parameters
4. Click "Clear Output" if desired
5. Click "Run Inference" again

### Stopping Long-Running Inference
- Click "Stop" button at any time
- The process will terminate gracefully
- Partial output will remain visible

### Copying Output
1. Click in the output area
2. Use Ctrl+A (or Cmd+A on Mac) to select all
3. Use Ctrl+C (or Cmd+C on Mac) to copy
4. Paste into your preferred application

## Common Use Cases

1. **Content Writing**: Blog posts, articles, creative stories
2. **Code Generation**: Functions, classes, scripts
3. **Question Answering**: Research, learning, explanations
4. **Text Completion**: Finishing sentences, paragraphs, or documents
5. **Brainstorming**: Ideas, solutions, alternatives
6. **Translation**: Language translation (if model supports it)
7. **Summarization**: Condensing longer texts (prompt engineering required)
8. **Chat**: Interactive conversations with chat-tuned models
