// Socket.IO connection
const socket = io();

// DOM elements
const topicInput = document.getElementById('topic-input');
const enableWebCheckbox = document.getElementById('enable-web');
const maxTurnsSlider = document.getElementById('max-turns');
const turnsValue = document.getElementById('turns-value');
const startBtn = document.getElementById('start-btn');
const progressSection = document.getElementById('progress-section');
const progressLog = document.getElementById('progress-log');
const progressFill = document.getElementById('progress-fill');
const conversationSection = document.getElementById('conversation-section');
const conversation = document.getElementById('conversation');
const answerSection = document.getElementById('answer-section');
const finalAnswer = document.getElementById('final-answer');
const answerQuality = document.getElementById('answer-quality');
const answerTurns = document.getElementById('answer-turns');
const ollamaStatus = document.getElementById('ollama-status');
const gpuStatus = document.getElementById('gpu-status');
const memoryStats = document.getElementById('memory-stats');

// Update turns slider value
maxTurnsSlider.addEventListener('input', (e) => {
    turnsValue.textContent = e.target.value;
});

// Start discussion button
startBtn.addEventListener('click', () => {
    const topic = topicInput.value.trim();

    if (!topic) {
        alert('Please enter a question or topic!');
        return;
    }

    // Reset UI
    conversation.innerHTML = '';
    progressLog.innerHTML = '';
    finalAnswer.textContent = '';
    progressFill.style.width = '0%';

    progressSection.style.display = 'block';
    conversationSection.style.display = 'block';
    answerSection.style.display = 'none';

    startBtn.disabled = true;
    startBtn.textContent = '⏳ Discussion in progress...';

    // Start discussion
    socket.emit('start_discussion', {
        topic: topic,
        enable_web: enableWebCheckbox.checked,
        max_turns: parseInt(maxTurnsSlider.value)
    });
});

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to AGI System');
});

socket.on('status', (data) => {
    addProgressItem(data.message, 'info');
});

socket.on('ollama_status', (data) => {
    if (data.connected) {
        ollamaStatus.textContent = '✅ Ollama Connected';
        ollamaStatus.classList.add('connected');
        ollamaStatus.classList.remove('disconnected');
    } else {
        ollamaStatus.textContent = '❌ Ollama Disconnected';
        ollamaStatus.classList.add('disconnected');
        ollamaStatus.classList.remove('connected');
    }
});

socket.on('gpu_status', (data) => {
    if (data.available) {
        gpuStatus.textContent = `🎮 ${data.name} (${data.vram})`;
        gpuStatus.classList.add('connected');
    } else {
        gpuStatus.textContent = '⚠️ CPU Mode (Slow)';
        gpuStatus.classList.add('disconnected');
    }
});

socket.on('progress', (data) => {
    addProgressItem(data.message, 'progress');

    // Update conversation if it's a response
    if (data.data && data.data.agent && data.data.message) {
        addConversationMessage(
            data.data.agent,
            data.data.message,
            data.data.turn
        );
    }

    // Update progress bar
    if (data.data && data.data.turn) {
        const maxTurns = parseInt(maxTurnsSlider.value);
        const progress = (data.data.turn / maxTurns) * 100;
        progressFill.style.width = `${progress}%`;
    }
});

socket.on('discussion_complete', (data) => {
    addProgressItem('✅ Discussion complete!', 'success');

    // Show final answer
    answerSection.style.display = 'block';
    finalAnswer.textContent = data.final_answer;
    answerQuality.textContent = `📊 Quality: ${(data.quality * 100).toFixed(0)}%`;
    answerTurns.textContent = `💬 ${data.turns} turns`;

    progressFill.style.width = '100%';

    // Re-enable button
    startBtn.disabled = false;
    startBtn.textContent = '🚀 Start New Discussion';

    // Update stats
    loadStats();

    // Scroll to answer
    answerSection.scrollIntoView({ behavior: 'smooth' });
});

socket.on('error', (data) => {
    addProgressItem(`❌ Error: ${data.message}`, 'error');
    startBtn.disabled = false;
    startBtn.textContent = '🚀 Start Discussion';
});

// Helper functions
function addProgressItem(message, type = 'info') {
    const item = document.createElement('div');
    item.className = 'progress-item';
    item.textContent = `${getCurrentTime()} ${message}`;
    progressLog.appendChild(item);
    progressLog.scrollTop = progressLog.scrollHeight;
}

function addConversationMessage(agent, text, turn) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';

    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="agent-name">🎭 ${agent.toUpperCase()}</span>
            <span class="turn-number">Turn ${turn}</span>
        </div>
        <div class="message-text">${escapeHtml(text)}</div>
    `;

    conversation.appendChild(messageDiv);
    conversation.scrollTop = conversation.scrollHeight;
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            memoryStats.textContent = `💾 ${data.conversations} conversations • ${data.knowledge} knowledge entries`;
        })
        .catch(err => {
            console.error('Failed to load stats:', err);
        });
}

// Load stats on page load
loadStats();