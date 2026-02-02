from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import os
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Import after app creation to avoid circular issues
from agi_core import AGISystemWeb

# Global AGI system instance
agi_system = None
current_session = None
# Semaphore to prevent multiple discussions running simultaneously (VRAM protection)
discussion_semaphore = threading.Semaphore(1)

@app.route('/')
def index():
    """Main web UI"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check for Docker"""
    return jsonify({
        "status": "healthy",
        "ollama": check_ollama(),
        "gpu_info": get_gpu_info()
    })

@app.route('/api/stats')
def stats():
    """Get system statistics"""
    global agi_system
    try:
        if agi_system and agi_system.memory:
            return jsonify(agi_system.get_memory_stats())
    except Exception as e:
        print(f"Stats error: {e}", flush=True)
    return jsonify({"conversations": 0, "knowledge": 0})

@app.route('/api/models')
def list_models():
    """List available Ollama models"""
    try:
        import requests
        ollama_host = os.getenv("OLLAMA_HOST", "host.docker.internal:11434")
        response = requests.get(f"http://{ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return jsonify({
                "models": [{"name": m['name'], "size": m.get('size', 0)} for m in models],
                "count": len(models)
            })
    except Exception as e:
        return jsonify({"error": str(e), "models": []})

def check_ollama():
    """Check if Ollama is accessible"""
    import requests
    try:
        ollama_host = os.getenv("OLLAMA_HOST", "host.docker.internal:11434")
        response = requests.get(f"http://{ollama_host}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_gpu_info():
    """Get GPU information if available"""
    try:
        import subprocess
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.used', '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            name, total, used = result.stdout.strip().split(', ')
            return {
                "name": name,
                "memory_total_mb": int(total),
                "memory_used_mb": int(used),
                "available": True
            }
    except:
        pass
    return {"available": False, "message": "No GPU detected or nvidia-smi not available"}

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print("Client connected", flush=True)
    emit('status', {'message': '🧠 Connected to AGI System (GTX 1650 Optimized)'})
    emit('ollama_status', {'connected': check_ollama()})
    gpu_info = get_gpu_info()
    if gpu_info.get('available'):
        emit('gpu_status', {
            'available': True,
            'name': gpu_info['name'],
            'vram': f"{gpu_info['memory_used_mb']}/{gpu_info['memory_total_mb']} MB"
        })
    else:
        emit('gpu_status', {'available': False})

@socketio.on('start_discussion')
def handle_discussion(data):
    """Start AGI discussion with VRAM protection"""
    global agi_system, current_session

    print(f"Received discussion request: {data.get('topic', 'NO TOPIC')}", flush=True)

    # CRITICAL: Only allow one discussion at a time to prevent OOM
    if not discussion_semaphore.acquire(blocking=False):
        emit('error', {'message': '⚠️ Another discussion is running. Please wait for it to complete.'})
        return

    topic = data.get('topic', '')
    enable_web = data.get('enable_web', True)
    max_turns = data.get('max_turns', 20)

    if not topic:
        emit('error', {'message': 'No topic provided'})
        discussion_semaphore.release()
        return

    # Progress callback for real-time updates
    def progress_callback(update):
        socketio.emit('progress', update)

    # Run discussion in background thread
    def run_background():
        global agi_system

        try:
            print("Initializing AGI System...", flush=True)
            agi_system = AGISystemWeb(progress_callback=progress_callback)
            print(f"Starting discussion on: {topic}", flush=True)
            result = agi_system.run_discussion(topic, max_turns, enable_web)
            print("Discussion complete, emitting result...", flush=True)
            socketio.emit('discussion_complete', result)
        except Exception as e:
            print(f"ERROR in discussion: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            socketio.emit('error', {'message': str(e)})
        finally:
            # Don't close agi_system here - keep it for stats
            # Just release the lock
            discussion_semaphore.release()
            print("Discussion lock released", flush=True)

    thread = threading.Thread(target=run_background)
    thread.daemon = True
    thread.start()

    emit('status', {'message': f'🚀 Starting discussion on: {topic}'})

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('Client disconnected', flush=True)

if __name__ == '__main__':
    print("=" * 80, flush=True)
    print("🧠 ULTIMATE AGI SYSTEM - GTX 1650 OPTIMIZED", flush=True)
    print("=" * 80, flush=True)
    print(f"🌐 Web UI: http://localhost:5000", flush=True)
    print(f"🔒 Sequential model loading (4GB VRAM safe)", flush=True)
    print(f"🤖 Ollama: {check_ollama()}", flush=True)
    gpu = get_gpu_info()
    if gpu.get('available'):
        print(f"🎮 GPU: {gpu['name']} ({gpu['memory_total_mb']}MB)", flush=True)
    else:
        print("⚠️  No GPU detected - will use CPU (slow)", flush=True)
    print("=" * 80, flush=True)

    # Use threading mode for SocketIO to avoid eventlet issues
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)