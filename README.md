# 🧠 Multi-Agent AGI System

A sophisticated multi-agent AI system that orchestrates 11 specialized language models to collaboratively solve complex problems through structured discussions. Optimized for GTX 1650 (4GB VRAM).

## 🌟 Features

- **11 Specialized AI Agents**: Each with unique roles (analyst, creative, engineer, critic, philosopher, etc.)
- **Intelligent Discussion Management**: Moderator-led collaborative problem-solving
- **Web Search Integration**: Real-time context from DuckDuckGo
- **Code Execution**: Safe Python code execution in isolated environment
- **Long-Term Memory**: SQLite-based persistent storage of conversations and knowledge
- **Resource Optimization**: Smart GPU/CPU fallback for memory-constrained systems
- **Real-Time Progress Tracking**: WebSocket-based live updates
- **Web Interface**: Flask-based UI for easy interaction

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Interface (Flask)                 │
│                  Real-time Progress Updates              │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  AGI Core System                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Moderator (qwen3-unfiltered)                    │  │
│  │  Coordinates discussion & synthesizes results    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Analyst    │  │   Creative   │  │   Engineer   │ │
│  │  (qwen2.5)   │  │ (llama3.2)   │  │(qwen-coder)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │    Critic    │  │ Philosopher  │  │  Optimizer   │ │
│  │  (mistral)   │  │(deepseek-r1) │  │(deepseek-v2) │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Logician   │  │ Implementer  │  │   Explorer   │ │
│  │   (phi4)     │  │(qwen-ablate) │  │(qwen-coder)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────┐                                       │
│  │   Debugger   │                                       │
│  │(qwen-coder)  │                                       │
│  └──────────────┘                                       │
└──────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌────────────────┐  ┌─────────────────┐  ┌────────────────┐
│  Web Search    │  │  Code Executor  │  │ Long-Term      │
│  (DuckDuckGo)  │  │  (Sandboxed)    │  │ Memory (SQLite)│
└────────────────┘  └─────────────────┘  └────────────────┘
```

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **Ollama**: Installed and running ([Download](https://ollama.ai))
- **GPU**: NVIDIA GTX 1650 (4GB VRAM) or better (optional, falls back to CPU)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: ~20GB for all models

## 🚀 Quick Start

### 1. Install Ollama

**Windows:**
```powershell
# Download from https://ollama.ai/download/windows
# Run the installer
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Pull Required Models

```bash
# Core models (required)
ollama pull qwen3-unfiltered:latest
ollama pull qwen2.5:7b
ollama pull llama3.2-uncensored:3b
ollama pull qwen2.5-coder:3b
ollama pull mistral-nemo-uncensored:latest

# Advanced models (optional)
ollama pull deepseek-r1:7b
ollama pull deepseek-coder-v2:lite
ollama pull phi4-mini-reasoning:latest
ollama pull huihui_ai/qwen2.5-coder-abliterate:7b-instruct
ollama pull qwen2.5-coder:7b
```

### 3. Install Python Dependencies

```bash
cd "e:\Ai model plus code\centralized model from all model script answers\Agi system"
pip install -r requirements.txt
```

### 4. Run the System

**Option A: Web Interface (Recommended)**
```bash
python app.py
```
Then open: `http://localhost:5000`

**Option B: Direct Python Usage**
```python
from agi_core import AGISystemWeb

def progress_callback(data):
    print(f"[{data['timestamp']}] {data['message']}")

agi = AGISystemWeb(progress_callback=progress_callback)
result = agi.run_discussion(
    topic="Explain quantum computing in simple terms",
    max_turns=15,
    enable_web=True
)

print("\n=== Final Answer ===")
print(result['final_answer'])
```

## 🐳 Docker Deployment (Optional)

```bash
# Build the image
docker-compose build

# Run the container
docker-compose up -d

# Access at http://localhost:5000
```

## 📁 Project Structure

```
Agi system/
├── agi_core.py           # Core AGI system logic
├── app.py                # Flask web application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── data/                 # SQLite database storage
│   └── agi_memory.db     # Persistent memory
├── sessions/             # Flask session data
├── static/               # Web UI assets
│   ├── css/
│   └── js/
└── templates/            # HTML templates
    └── index.html
```

## 🎯 Agent Roles & Expertise

| Agent | Model | Role | Expertise | Priority |
|-------|-------|------|-----------|----------|
| **Moderator** | qwen3-unfiltered | Coordinates discussion | Synthesis, coordination | 10 |
| **Analyst** | qwen2.5:7b | Data-driven analysis | Analysis, research | 8 |
| **Creative** | llama3.2-uncensored | Unconventional ideas | Creativity, brainstorming | 6 |
| **Engineer** | qwen2.5-coder:3b | Practical implementation | Coding, systems | 9 |
| **Critic** | mistral-nemo | Challenges assumptions | Critique, quality | 7 |
| **Philosopher** | deepseek-r1:7b | Explores deeper meaning | Ethics, reasoning | 5 |
| **Optimizer** | deepseek-coder-v2 | Efficiency-focused | Optimization | 8 |
| **Logician** | phi4-mini | Step-by-step reasoning | Logic, verification | 9 |
| **Implementer** | qwen-abliterate | Writes code examples | Coding | 7 |
| **Explorer** | qwen2.5-coder:3b | Researches alternatives | Research | 6 |
| **Debugger** | qwen2.5-coder:7b | Finds errors | Debugging | 9 |

## 💡 Usage Examples

### Example 1: Technical Question
```python
result = agi.run_discussion(
    topic="How do I optimize a Python web scraper for 10,000 URLs?",
    max_turns=20,
    enable_web=True
)
```

### Example 2: Creative Problem
```python
result = agi.run_discussion(
    topic="Design a sustainable urban transportation system for 2030",
    max_turns=15,
    enable_web=True
)
```

### Example 3: Code Review
```python
result = agi.run_discussion(
    topic="Review this code and suggest improvements: [paste code]",
    max_turns=10,
    enable_web=False
)
```

## ⚙️ Configuration

### Environment Variables

```bash
# Ollama host (default: localhost:11434)
export OLLAMA_HOST="localhost:11434"

# Database path (default: ./data/agi_memory.db)
export AGI_DB_PATH="./data/agi_memory.db"

# Flask settings
export FLASK_ENV="production"
export FLASK_SECRET_KEY="your-secret-key-here"
```

### Model Configuration

Edit `agi_core.py` to customize model parameters:

```python
MODEL_CONFIG = {
    "context_window": 1024,      # Tokens for context
    "temperature": 0.8,          # Creativity (0.0-1.0)
    "request_timeout": 400,      # Seconds
    "num_threads": 4             # CPU threads
}
```

## 🔧 Troubleshooting

### Issue: "Model not found"
```bash
# Pull the missing model
ollama pull <model-name>
```

### Issue: "Out of memory" / GPU errors
- System automatically falls back to CPU
- Reduce `max_turns` parameter
- Close other GPU-intensive applications

### Issue: Web search returns no results
- DuckDuckGo API can be unreliable
- Set `enable_web=False` to disable web search
- Check internet connection

### Issue: Database locked
- Close other instances of the application
- Delete `data/agi_memory.db.lock` if exists

### Issue: Slow performance
- Reduce number of agents in `AGENTS` list
- Increase `keep_alive` duration to keep models loaded
- Use smaller models (3B instead of 7B)

## 📊 Performance Tips

1. **Keep frequently-used models loaded**: Set `keep_alive: "5m"` instead of `0`
2. **Increase context window**: Change `num_ctx: 4096` for better context
3. **Reduce max_turns**: Use 10-15 turns instead of 20 for faster results
4. **Disable web search**: Set `enable_web=False` for offline usage

## 🔒 Security Notes

⚠️ **Code Execution Warning**: The `DockerSafeExecutor` can execute arbitrary Python code. Only use in trusted environments.

**Recommendations**:
- Run in Docker container for isolation
- Don't expose to public internet without authentication
- Review generated code before execution
- Set resource limits in production

## 🛠️ Development

### Running Tests
```bash
# (Tests not yet implemented)
pytest tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 Known Issues

- ⚠️ **Windows Compatibility**: Some process management code is Linux-specific (see [code_review.md](file:///C:/Users/ravi/.gemini/antigravity/brain/63e109e2-9990-4610-8b90-1564c57caef0/code_review.md))
- ⚠️ **Thread Safety**: SQLite operations may need locking for high concurrency
- ⚠️ **Web Search**: DuckDuckGo API can be unreliable

See the [Code Review](file:///C:/Users/ravi/.gemini/antigravity/brain/63e109e2-9990-4610-8b90-1564c57caef0/code_review.md) for detailed analysis.

## 📈 Roadmap

- [ ] Fix Windows compatibility issues
- [ ] Add authentication for web interface
- [ ] Implement agent performance tracking
- [ ] Add more search providers (Brave, SerpAPI)
- [ ] Support for image/video models
- [ ] Export conversations to PDF/Markdown
- [ ] API endpoints for external integration

## 🤝 Credits

Built with:
- [Ollama](https://ollama.ai) - Local LLM runtime
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [SQLite](https://www.sqlite.org/) - Database
- Various open-source LLMs (Qwen, LLaMA, Mistral, DeepSeek, Phi)

## 📞 Support

For issues and questions:
- Check the [Code Review](file:///C:/Users/ravi/.gemini/antigravity/brain/63e109e2-9990-4610-8b90-1564c57caef0/code_review.md) for known issues
- Review troubleshooting section above
- Open an issue on GitHub (if applicable)

---

**Made with 🧠 by [Ravichandran]**
