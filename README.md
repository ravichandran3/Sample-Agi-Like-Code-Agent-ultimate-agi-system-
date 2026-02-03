# 🧠 Ultimate AGI System

A fully functional Artificial General Intelligence system using 11 local AI models working together through Ollama. Optimized for NVIDIA GTX 1650 4GB VRAM.

## ✨ Features

### 🤖 Multi-Model Intelligence
- **11 AI Models** working collaboratively
- **Adaptive Mode Selection** - automatically chooses the right approach:
  - **Instant Mode**: Simple questions (~5 seconds)
  - **Fast Mode**: Medium complexity (~1.5 minutes, 3 models)
  - **Full Mode**: Complex tasks (~11 minutes, all 11 models)

### 🌐 Web Capabilities
- **URL Reading**: Automatically reads and understands web pages
- **GitHub Analysis**: Analyzes repository structure and code
- **Web Search**: DuckDuckGo integration for research
- **Real-time Web UI**: Flask + SocketIO interface

### 🧩 Intelligence Features
- **Long-term Memory**: SQLite-based persistent knowledge
- **RAG (Retrieval-Augmented Generation)**: Ollama embeddings
- **Peer Teaching**: Agents learn from each other's corrections
- **Chain-of-Thought Reasoning**: Step-by-step problem solving
- **Self-Learning**: Gets smarter over time

### 🛠️ Technical Capabilities
- **Safe Code Execution**: Docker-isolated Python execution
- **Complexity Detection**: Auto-routes questions to appropriate models
- **Progress Tracking**: Real-time updates on thinking process
- **VRAM Optimization**: Sequential model loading for 4GB GPUs

---

## 📋 Prerequisites

### System Requirements
- **OS**: Windows, Linux, or macOS
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: NVIDIA GTX 1650 (4GB VRAM) or better (optional but recommended)
- **Storage**: ~30GB for models

### Software Dependencies
- **Python 3.8+**
- **Ollama** ([Download](https://ollama.ai/))
- **Git** (for cloning)

---

## 🚀 Quick Start

### 1. Install Ollama

```bash
# Windows/Mac: Download from https://ollama.ai/
# Linux:
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Pull Required Models

```bash
# Core models (required for full system)
ollama pull qwen3-unfiltered:latest
ollama pull qwen2.5-coder:7b
ollama pull qwen2.5-coder:3b
ollama pull mtaylor91/llama3.2-uncensored:3b
ollama pull gdisney/mistral-nemo-uncensored:latest
ollama pull deepseek-r1:14b
ollama pull deepseek-coder-v2:lite
ollama pull phi4-mini-reasoning:latest
ollama pull huihui_ai/qwen2.5-coder-abliterate:7b-instruct
ollama pull WhiteRabbitNeo/WhiteRabbitNeo-2.5-Qwen-2.5-Coder-7B:latest
ollama pull hf.co/mradermacher/Qwen2.5-7B-Instruct-1M-abliterated-GGUF:Q6_K

# For RAG (embeddings)
ollama pull nomic-embed-text

# Optional: For vision capabilities
ollama pull llava:latest
```

### 3. Clone and Setup

```bash
git clone <your-repo-url>
cd "Agi system"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Run AGI

#### Option A: Interactive CLI (Smart Mode)
```bash
python agi_smart.py
```

#### Option B: Web Interface
```bash
python app.py
# Open browser to http://localhost:5000
```

#### Option C: Specific Modes

**Fast Mode (3B models only)**
```bash
python agi_realistic.py
```

**Full Mode (All 11 models)**
```bash
python agi_all_11_models.py
```

**Instant Mode (Single fast model with RAG)**
```bash
python agi_core_instant.py
```

---

## 💡 Usage Examples

### Simple Question
```python
from agi_smart import SmartHybridAGI

agi = SmartHybridAGI()
answer = agi.ask("What is 2+2?")
# Uses: Instant mode (~5 seconds)
```

### URL Analysis
```python
answer = agi.ask("What is this article about? https://example.com/article")
# Automatically reads and analyzes the webpage
```

### Complex Research
```python
answer = agi.ask("Explain quantum computing and compare different qubit implementations")
# Uses: Full AGI mode with all 11 models (~11 minutes)
```

### GitHub Repository Analysis
```python
answer = agi.ask("What is https://github.com/microsoft/vscode? Explain the architecture")
# Analyzes repository structure, README, and provides insights
```

---

## 🏗️ Architecture

### System Components

```
agi_system/
├── agi_smart.py              # Main entry - adaptive complexity routing
├── agi_core_instant.py       # Fast mode with RAG and reasoning
├── agi_realistic.py          # Medium mode (3B models)
├── agi_all_11_models.py      # Full mode (all 11 models)
├── agi_core.py               # Web-optimized with callbacks
├── agi_core_full.py          # Complete system with all features
├── app.py                    # Flask web interface
├── complexity_analyzer.py    # Question complexity detection
└── data/
    └── agi_memory.db         # Long-term memory database
```

### Model Roles

Each AI model has a specialized role:

| Model | Role | Expertise |
|-------|------|-----------|
| qwen3-unfiltered | Moderator | Coordination, synthesis |
| qwen2.5-coder:7b | Analyst | Code analysis, debugging |
| llama3.2-uncensored:3b | Creative | Novel solutions, creativity |
| qwen2.5-coder:3b | Engineer | Implementation, coding |
| mistral-nemo-uncensored | Critic | Quality check, improvement |
| deepseek-r1:14b | Philosopher | Deep reasoning, ethics |
| deepseek-coder-v2:lite | Optimizer | Performance, efficiency |
| phi4-mini-reasoning | Logician | Logical reasoning, math |
| qwen2.5-coder-abliterate | Implementer | Practical solutions |
| WhiteRabbitNeo | Explorer | Novel approaches, research |
| Qwen2.5-abliterated | Debugger | Error detection, fixes |

---

## ⚙️ Configuration

### Environment Variables

```bash
# Ollama configuration
export OLLAMA_HOST="localhost:11434"

# For Docker deployment
export OLLAMA_HOST="host.docker.internal:11434"
```

### Performance Tuning

**For 4GB VRAM (GTX 1650)**:
- Use `agi_realistic.py` (fast 3B models only)
- Sequential model loading only
- Default timeout: 120 seconds

**For 8GB+ VRAM**:
- Can use `agi_all_11_models.py`
- Parallel model preloading enabled
- Increased timeout: 180 seconds

---

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up --build

# Access web UI
http://localhost:5000
```

**Note**: Ensure Ollama is accessible from Docker container using `host.docker.internal`.

---

## 🧪 Testing

### Test URL Reading
```bash
python test_agi_url.py
```

### Test Multi-Model System
```bash
python test_agi.py
```

### Test Smart Routing
```bash
python test_smart.py
```

---

## 📊 Performance Benchmarks

| Mode | Models | Avg Time | Best For |
|------|--------|----------|----------|
| Instant | 1 (+ RAG) | ~5s | Math, facts, simple queries |
| Fast | 3 (3B) | ~1.5min | General questions |
| Full | 11 (mixed) | ~11min | Complex analysis, research |

---

## 🔧 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
ollama list

# Test connection
curl http://localhost:11434/api/tags
```

### VRAM Out of Memory
- Use `agi_realistic.py` instead of `agi_all_11_models.py`
- Reduce number of models
- Ensure sequential loading (not parallel)

### Slow Response Times
- Check GPU utilization
- Reduce `max_turns` parameter
- Use smaller models (3B instead of 7B)

### URL Reading Fails
- Check internet connection
- Verify URL is accessible
- Some sites may block scraping

---

## 🛣️ Roadmap

### Completed ✅
- [x] Multi-model collaboration (11 models)
- [x] URL reading and web scraping
- [x] Long-term memory system
- [x] RAG with embeddings
- [x] Web interface
- [x] Adaptive complexity detection

### In Progress 🚧
- [ ] Advanced tool system (file ops, system commands)
- [ ] Vision capabilities (image analysis)
- [ ] Task planning and execution

### Planned 📋
- [ ] Audio processing (speech-to-text)
- [ ] Plugin system
- [ ] REST API
- [ ] Mobile app

---

## 📖 API Reference

### SmartHybridAGI

```python
from agi_smart import SmartHybridAGI

agi = SmartHybridAGI()

# Ask a question
answer = agi.ask(question: str) -> str
```

### TrueAGI (Instant Mode)

```python
from agi_core_instant import TrueAGI

agi = TrueAGI()

# Think and respond
answer = agi.think(question: str) -> str

# Read URL
content = agi.read_url(url: str) -> str

# Read GitHub repo
content = agi.read_github_repo(url: str) -> str
```

### MaxSpeedAGI (Full Mode)

```python
from agi_all_11_models import MaxSpeedAGI

agi = MaxSpeedAGI()

# All 11 models discuss
answer = agi.discuss(question: str) -> str
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- New AI model integrations
- Tool implementations
- Performance optimizations
- Documentation improvements
- Bug reports and fixes

---

## 📄 License

[Specify your license here]

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **LangChain** - AI framework inspiration
- **All AI Model Creators** - For the amazing models
- **Community** - For feedback and contributions

---

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Check the wiki

---

## ⚠️ Important Notes

- This system requires significant computational resources
- Some models may have usage restrictions
- Web scraping should respect robots.txt
- Always verify AI outputs for critical applications
- The system learns from interactions - quality improves over time

---

## 🎯 Example Use Cases

### Research Assistant
```python
agi.ask("Research the latest developments in quantum computing and summarize key breakthroughs")
```

### Code Analysis
```python
agi.ask("Analyze this repository: https://github.com/user/repo and suggest improvements")
```

### Learning Aid
```python
agi.ask("Explain neural networks like I'm 10 years old")
```

### Problem Solving
```python
agi.ask("I have a Python error: [error message]. How do I fix it?")
```

---

**Built with 🧠 by combining the power of 11 AI models**
"# agi-start" 
