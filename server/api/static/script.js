const currentId = Number(document.body.dataset.currentEnigma || 0);
const storageKey = 'enigme_progress_v1';

function loadProgress() {
    try {
        const stored = localStorage.getItem(storageKey);
        return stored ? JSON.parse(stored) : {};
    } catch (error) {
        return {};
    }
}

function saveProgress(progress) {
    localStorage.setItem(storageKey, JSON.stringify(progress));
}

function markCompleted(id) {
    const progress = loadProgress();
    progress[id] = true;
    saveProgress(progress);
    updateSidebar(progress);
}

function updateSidebar(progress) {
    document.querySelectorAll('.step-item').forEach((item) => {
        const number = Number(item.querySelector('.step-number')?.textContent?.trim());
        if (!number) return;
        if (progress[number]) {
            item.classList.add('completed');
            item.title = 'Énigme résolue';
        }
    });
}

function displayAlreadySolved() {
    const panel = document.querySelector('.panel');
    if (!panel) return;
    const answerForm = panel.querySelector('.answer-form');
    if (!answerForm) return;
    const alert = document.createElement('div');
    alert.className = 'message message-hint';
    alert.textContent = 'Cette énigme est déjà résolue dans votre progression locale. Vous pouvez revenir sur une ancienne énigme pour la relire.';
    panel.insertBefore(alert, answerForm);
}

function parseCompletedQuery() {
    const params = new URLSearchParams(window.location.search);
    const completedValue = params.get('completed');
    if (!completedValue) {
        return null;
    }
    const id = Number(completedValue);
    if (Number.isInteger(id) && id > 0) {
        return id;
    }
    return null;
}

function cleanUrl() {
    const url = new URL(window.location.href);
    if (url.searchParams.has('completed')) {
        url.searchParams.delete('completed');
        window.history.replaceState({}, '', url.pathname + url.search);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const progress = loadProgress();
    updateSidebar(progress);

    const completedId = parseCompletedQuery();
    if (completedId) {
        markCompleted(completedId);
        cleanUrl();
    }

    if (currentId && progress[currentId]) {
        displayAlreadySolved();
    }

    const chatLog = document.getElementById('chat-log');
    if (chatLog) {
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    const temperatureInput = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperature-value');
    if (temperatureInput && temperatureValue) {
        const updateTemperatureOutput = () => {
            const value = Number(temperatureInput.value);
            temperatureValue.textContent = value.toFixed(2);
        };
        updateTemperatureOutput();
        temperatureInput.addEventListener('input', updateTemperatureOutput);
    }
});
