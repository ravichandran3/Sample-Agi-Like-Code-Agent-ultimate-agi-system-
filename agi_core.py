import requests
import json
import re
import time
import random
import sqlite3
from collections import deque
from datetime import datetime
import os
import subprocess
import tempfile
import signal
import threading

# ============================================================================
# ULTIMATE AGI CORE - GTX 1650 4GB OPTIMIZED VERSION
# ============================================================================

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "host.docker.internal:11434")
OLLAMA_URL = f"http://{OLLAMA_HOST}/api/generate"

# ALL 11 MODELS - Optimized for 4GB VRAM (sequential loading only)
AGENTS = [
    {"name": "qwen3-unfiltered:latest", "role": "moderator", "personality": "balanced, coordinates discussion",
     "priority": 10, "expertise": ["coordination", "synthesis"], "accuracy_history": [], "max_tokens": 150},
    {"name": "qwen2.5:7b", "role": "analyst", "personality": "detailed, methodical thinker",
     "priority": 8, "expertise": ["analysis", "research"], "accuracy_history": [], "max_tokens": 200},
    {"name": "llama3.2-uncensored:3b", "role": "creative", "personality": "imaginative, unconventional ideas",
     "priority": 6, "expertise": ["creativity", "brainstorming"], "accuracy_history": [], "max_tokens": 180},
    {"name": "qwen2.5-coder:3b", "role": "engineer", "personality": "practical, implementation-focused", "priority": 9,
     "expertise": ["coding", "systems"], "accuracy_history": [], "max_tokens": 200},
    {"name": "mistral-nemo-uncensored:latest", "role": "critic",
     "personality": "challenges assumptions, finds flaws", "priority": 7, "expertise": ["critique", "quality"],
     "accuracy_history": [], "max_tokens": 180},
    {"name": "deepseek-r1:7b", "role": "philosopher", "personality": "explores deeper meaning", "priority": 5,
     "expertise": ["ethics", "reasoning"], "accuracy_history": [], "max_tokens": 220},
    {"name": "deepseek-coder-v2:lite", "role": "optimizer", "personality": "efficiency-focused", "priority": 8,
     "expertise": ["optimization"], "accuracy_history": [], "max_tokens": 180},
    {"name": "phi4-mini-reasoning:latest", "role": "logician", "personality": "step-by-step reasoning", "priority": 9,
     "expertise": ["logic", "verification"], "accuracy_history": [], "max_tokens": 180},
    {"name": "huihui_ai/qwen2.5-coder-abliterate:7b-instruct", "role": "implementer",
     "personality": "writes code examples", "priority": 7, "expertise": ["coding"], "accuracy_history": [],
     "max_tokens": 250},
    {"name": "qwen2.5-coder:3b", "role": "explorer",
     "personality": "researches alternatives", "priority": 6, "expertise": ["research"], "accuracy_history": [],
     "max_tokens": 180},
    {"name": "qwen2.5-coder:7b", "role": "debugger", "personality": "finds errors", "priority": 9,
     "expertise": ["debugging"], "accuracy_history": [], "max_tokens": 200}
]


# ============================================================================
# DOCKER-SAFE CODE EXECUTION
# ============================================================================

class DockerSafeExecutor:
    """Execute code safely inside Docker container - isolated from host"""

    @staticmethod
    def execute_python_code(code, timeout=10):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            process = subprocess.Popen(
                ['python', temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                returncode = process.returncode
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                stdout, stderr = process.communicate()
                return {"success": False, "output": "", "error": f"Execution timeout ({timeout}s)"}
            finally:
                try:
                    os.unlink(temp_file)
                except:
                    pass

            if returncode == 0:
                return {"success": True, "output": stdout, "error": None}
            else:
                return {"success": False, "output": stdout, "error": stderr}

        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}


# ============================================================================
# MEMORY, WEB SEARCH, TOOLS
# ============================================================================

class LongTermMemory:
    def __init__(self, db_path="/app/data/agi_memory.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_db()

    def _initialize_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                category TEXT,
                timestamp TEXT,
                summary TEXT,
                quality_score REAL,
                confidence_score REAL,
                turns_taken INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT UNIQUE,
                definition TEXT,
                source TEXT,
                confidence REAL,
                verified_count INTEGER DEFAULT 1,
                timestamp TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_role TEXT,
                topic_category TEXT,
                accuracy_score REAL,
                confidence_score REAL,
                mistakes_made INTEGER DEFAULT 0,
                corrections_made INTEGER DEFAULT 0,
                timestamp TEXT
            )
        """)
        self.conn.commit()

    def store_conversation(self, topic, category, summary, quality, confidence, turns):
        self.cursor.execute(
            """INSERT INTO conversations (topic, category, timestamp, summary, quality_score, confidence_score, turns_taken) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (topic, category, datetime.now().isoformat(), summary, quality, confidence, turns)
        )
        self.conn.commit()

    def get_stats(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM conversations")
            total_convos = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM knowledge")
            total_knowledge = self.cursor.fetchone()[0]
            return {"conversations": total_convos, "knowledge": total_knowledge}
        except Exception as e:
            print(f"Database stats error: {e}", flush=True)
            return {"conversations": 0, "knowledge": 0}

    def close(self):
        self.conn.close()


class WebSearchTool:
    @staticmethod
    def search_duckduckgo(query, max_results=5):
        try:
            url = "https://api.duckduckgo.com/"
            params = {'q': query, 'format': 'json', 'no_html': 1, 'skip_disambig': 1}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            results = []
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Answer'),
                    'snippet': data.get('Abstract'),
                    'url': data.get('AbstractURL', '')
                })
            for topic in data.get('RelatedTopics', [])[:max_results - 1]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'title': topic.get('Text', '')[:100],
                        'snippet': topic.get('Text', ''),
                        'url': topic.get('FirstURL', '')
                    })
            return {"success": True, "results": results, "query": query}
        except Exception as e:
            return {"success": False, "error": str(e), "query": query}


# ============================================================================
# MAIN AGI SYSTEM FOR WEB
# ============================================================================

class AGISystemWeb:
    """Web-optimized AGI system with progress callbacks - GTX 1650 Optimized"""

    def __init__(self, progress_callback=None):
        self.agents = AGENTS.copy()
        self.memory = LongTermMemory()
        self.executor = DockerSafeExecutor()
        self.web_search = WebSearchTool()
        self.progress_callback = progress_callback
        self.conversation = []
        self.topic = ""
        self.turn_count = 0
        self._load_agent_history()

    def _load_agent_history(self):
        for agent in self.agents:
            agent['historical_accuracy'] = 0.7
            agent['accuracy_history'] = []

    def emit_progress(self, message, data=None):
        if self.progress_callback:
            self.progress_callback({
                "message": message,
                "data": data,
                "timestamp": datetime.now().isoformat()
            })

    def call_model(self, agent, prompt, max_tokens=None):
        if max_tokens is None:
            max_tokens = agent.get('max_tokens', 200)

        try:
            return self._call_model_internal(agent, prompt, max_tokens, use_gpu=True)
        except Exception as e:
            error_str = str(e).lower()
            if any(x in error_str for x in ["out of memory", "cuda", "ggml", "gpu", "vram"]):
                self.emit_progress(f"⚠️ {agent['role']} ({agent['name']}) too big for GPU, trying CPU...")
                try:
                    return self._call_model_internal(agent, prompt, max_tokens, use_gpu=False)
                except Exception as e2:
                    return {"text": f"[Error on CPU too: {e2}]", "success": False, "quality": 0, "confidence": 0}
            raise

    def _call_model_internal(self, agent, prompt, max_tokens, use_gpu=True):
        try:
            payload = {
                "model": agent["name"],
                "prompt": prompt,
                "stream": False,
                "keep_alive": 0,
                "options": {
                    "num_ctx": 1024,
                    "num_predict": max_tokens,
                    "temperature": 0.8,
                    "num_gpu": 999 if use_gpu else 0,
                    "num_thread": 4,
                }
            }

            response = requests.post(OLLAMA_URL, json=payload, timeout=400)

            if response.status_code != 200:
                error_text = response.text
                if "loading" in error_text.lower() or "pull" in error_text.lower():
                    return {
                        "text": f"[Model {agent['name']} not downloaded. Run: ollama pull {agent['name']}]",
                        "success": False,
                        "quality": 0,
                        "confidence": 0
                    }
                return {
                    "text": f"[Error: HTTP {response.status_code} - {error_text[:100]}]",
                    "success": False,
                    "quality": 0,
                    "confidence": 0
                }

            text = response.json().get("response", "").strip()
            text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

            quality = min(0.9, 0.5 + (len(text) / 1000))
            confidence = 0.7 if use_gpu else 0.5

            return {"text": text, "success": True, "quality": quality, "confidence": confidence}

        except requests.exceptions.Timeout:
            return {"text": f"[Timeout: {agent['name']} took too long]", "success": False, "quality": 0,
                    "confidence": 0}
        except Exception as e:
            raise e

    def run_discussion(self, topic, max_turns=20, enable_web=True):
        self.topic = topic
        self.turn_count = 0
        self.conversation = []

        self.emit_progress("🚀 Starting AGI discussion...", {"topic": topic})
        self.emit_progress(f"📝 Using {len(self.agents)} specialized agents (sequential loading for 4GB VRAM)")

        web_context = ""
        if enable_web:
            self.emit_progress("🌐 Searching web for context...")
            web_results = self.web_search.search_duckduckgo(topic)
            if web_results['success'] and web_results['results']:
                web_context = "\n".join([f"- {r['snippet']}" for r in web_results['results'][:3]])
                self.emit_progress(f"✅ Web context added ({len(web_results['results'])} results)")
            else:
                self.emit_progress("⚠️ Web search failed or no results")

        self.emit_progress("👥 Moderator opening discussion...")
        moderator = self.agents[0]

        web_context_section = ""
        if web_context:
            web_context_section = "Context from web search:\n" + web_context + "\n"

        opening_prompt = f"""You are the moderator of an expert panel discussing: {topic}

Your role: Set the stage, introduce the topic clearly, and invite other experts to contribute.

{web_context_section}
Provide a concise introduction (2-3 sentences):"""

        opening = self.call_model(moderator, opening_prompt, moderator['max_tokens'])

        self.conversation.append({
            "turn": 1,
            "agent": moderator['role'],
            "text": opening['text']
        })

        self.emit_progress("💬 Discussion started", {
            "turn": 1,
            "agent": moderator['role'],
            "message": opening['text'][:200] + "..." if len(opening['text']) > 200 else opening['text']
        })

        for turn in range(2, max_turns + 1):
            agent = self._select_agent_for_turn(turn)
            context = self._build_context()
            prompt = self._build_agent_prompt(agent, topic, context, web_context)

            self.emit_progress(f"🤔 {agent['role'].upper()} ({agent['name']}) thinking...", {"turn": turn})

            response = self.call_model(agent, prompt, agent['max_tokens'])

            if response['success']:
                self.conversation.append({
                    "turn": turn,
                    "agent": agent['role'],
                    "text": response['text'],
                    "model": agent['name']
                })

                self.emit_progress("💬 Response added", {
                    "turn": turn,
                    "agent": agent['role'],
                    "message": response['text'][:200] + "..." if len(response['text']) > 200 else response['text']
                })

                time.sleep(0.2)
            else:
                self.emit_progress(f"⚠️ {agent['role']} failed: {response['text'][:100]}", {"turn": turn})
                self.conversation.append({
                    "turn": turn,
                    "agent": agent['role'],
                    "text": f"[System: {agent['role']} encountered an error. Continuing with other experts...]",
                    "model": agent['name'],
                    "error": True
                })

        self.emit_progress("🧠 Generating final answer...")

        full_discussion = self._build_context(last_n=10)

        final_prompt = f"""You are the moderator. Based on the expert discussion below, provide the final comprehensive answer to: {topic}

Expert Discussion:
{full_discussion}

Synthesize the key insights, resolve any contradictions, and provide the best possible answer:"""

        final = self.call_model(moderator, final_prompt, 500)

        self.memory.store_conversation(
            topic=topic,
            category="general",
            summary=final['text'][:1000],
            quality=final['quality'],
            confidence=final['confidence'],
            turns=len(self.conversation)
        )

        self.emit_progress("✅ Discussion complete!", {
            "turns": len(self.conversation),
            "final_answer": final['text']
        })

        return {
            "success": True,
            "topic": topic,
            "turns": len(self.conversation),
            "conversation": self.conversation,
            "final_answer": final['text'],
            "quality": final['quality']
        }

    def _select_agent_for_turn(self, turn):
        if turn <= 5:
            candidates = [a for a in self.agents if a['priority'] >= 8]
        elif turn <= 15:
            candidates = self.agents[1:]
        else:
            candidates = [a for a in self.agents if a['role'] in ['critic', 'philosopher', 'moderator']]

        idx = (turn - 2) % len(candidates)
        return candidates[idx]

    def _build_context(self, last_n=5):
        recent = self.conversation[-last_n:] if len(self.conversation) >= last_n else self.conversation
        context_lines = []
        for c in recent:
            context_lines.append(f"{c['agent'].upper()}: {c['text']}")
        return "\n\n".join(context_lines)

    def _build_agent_prompt(self, agent, topic, context, web_context):
        role_instructions = {
            "moderator": "Coordinate the discussion and synthesize viewpoints.",
            "analyst": "Provide data-driven analysis. Look for patterns and evidence.",
            "creative": "Offer unconventional ideas and creative solutions.",
            "engineer": "Focus on practical implementation and technical feasibility.",
            "critic": "Challenge assumptions and identify flaws in reasoning.",
            "philosopher": "Explore ethical implications and deeper meaning.",
            "optimizer": "Suggest efficiency improvements and optimizations.",
            "logician": "Verify reasoning step-by-step. Check for logical fallacies.",
            "implementer": "Write concrete code examples or specific implementations.",
            "explorer": "Research alternatives and compare different approaches.",
            "debugger": "Find errors and suggest fixes."
        }

        instruction = role_instructions.get(agent['role'], "Contribute your expertise.")

        web_section = ""
        if web_context and agent['role'] in ['analyst', 'researcher', 'explorer']:
            web_section = "Additional context from web search:\n" + web_context + "\n"

        prompt = f"""You are the {agent['role'].upper()} in an expert panel discussing: {topic}

Your specialty: {', '.join(agent['expertise'])}
Your approach: {agent['personality']}
Your task: {instruction}

Recent discussion:
{context}

{web_section}CRITICAL: If you disagree with previous experts, explain why and correct the mistake.
If you agree, build upon their ideas.

Your response (be concise, 2-4 sentences):"""

        return prompt

    def get_memory_stats(self):
        return self.memory.get_stats()

    def close(self):
        self.memory.close()