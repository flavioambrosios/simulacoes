(function () {
    'use strict';

    const config = window.AI_TUTOR_CONFIG || {};
    const simulationKey = config.simulationKey || 'lei-de-coulomb';
    if (!config.enabled || window.__aiTutorLoaded) {
        return;
    }
    window.__aiTutorLoaded = true;

    const exerciseContainer = document.getElementById('exerciseContainer');
    if (!exerciseContainer) {
        return;
    }

    const history = [];
    let currentQuestion = '';
    let panel;
    let transcript;
    let status;
    let input;
    let sendButton;

    injectStyles();
    ensureHelpButton();

    const observer = new MutationObserver(function () {
        ensureHelpButton();
        const nextQuestion = getExerciseQuestion();
        if (nextQuestion && currentQuestion && nextQuestion !== currentQuestion) {
            history.length = 0;
            if (transcript) {
                transcript.replaceChildren();
                addMessage('Tutor', 'Questão nova. Vamos pensar nela passo a passo.', 'assistant');
            }
        }
        currentQuestion = nextQuestion;
    });

    observer.observe(exerciseContainer, { childList: true, subtree: true });

    const exercisesModal = document.getElementById('exercisesModal') || document.getElementById('exerciseModal');
    if (exercisesModal) {
        const closeWhenExerciseEnds = new MutationObserver(function () {
            if (getComputedStyle(exercisesModal).display === 'none' || getComputedStyle(exerciseContainer).display === 'none') {
                closePanel();
            }
        });
        closeWhenExerciseEnds.observe(exercisesModal, { attributes: true, attributeFilter: ['style'] });
        closeWhenExerciseEnds.observe(exerciseContainer, { attributes: true, attributeFilter: ['style'] });
    }

    function injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .ai-tutor-launcher {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-height: 42px;
                margin: 12px 8px 4px 0;
                padding: 9px 14px;
                border: 1px solid #087f8c;
                border-radius: 6px;
                background: #087f8c;
                color: #fff;
                font: inherit;
                font-weight: 600;
                cursor: pointer;
            }
            .ai-tutor-launcher:hover { background: #066a75; }
            .ai-tutor-panel {
                position: fixed;
                z-index: 10020;
                right: 20px;
                bottom: 20px;
                display: flex;
                flex-direction: column;
                width: min(390px, calc(100vw - 32px));
                height: min(520px, calc(100dvh - 40px));
                overflow: hidden;
                border: 1px solid #b8c9cb;
                border-radius: 8px;
                background: #fff;
                color: #172b2e;
                box-shadow: 0 10px 35px rgba(0, 35, 40, .24);
                font: 15px/1.45 system-ui, sans-serif;
            }
            .ai-tutor-panel[hidden] { display: none; }
            .ai-tutor-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 12px 14px;
                background: #eaf4f3;
                border-bottom: 1px solid #d1e0df;
            }
            .ai-tutor-header h2 { margin: 0; font-size: 16px; }
            .ai-tutor-close {
                width: 36px;
                height: 36px;
                border: 0;
                border-radius: 4px;
                background: transparent;
                color: #172b2e;
                font-size: 24px;
                cursor: pointer;
            }
            .ai-tutor-transcript {
                display: flex;
                flex: 1;
                flex-direction: column;
                gap: 10px;
                overflow-y: auto;
                padding: 14px;
            }
            .ai-tutor-message {
                max-width: 92%;
                padding: 9px 11px;
                border-radius: 6px;
                white-space: pre-wrap;
                overflow-wrap: anywhere;
            }
            .ai-tutor-message.assistant { align-self: flex-start; background: #edf3f2; }
            .ai-tutor-message.user { align-self: flex-end; background: #d8eef0; }
            .ai-tutor-status {
                min-height: 20px;
                margin: 0;
                padding: 0 14px 8px;
                color: #52676a;
                font-size: 13px;
            }
            .ai-tutor-form { display: grid; gap: 8px; padding: 12px 14px 14px; border-top: 1px solid #d1e0df; }
            .ai-tutor-input {
                width: 100%;
                min-height: 72px;
                resize: vertical;
                box-sizing: border-box;
                padding: 9px;
                border: 1px solid #91a7aa;
                border-radius: 5px;
                color: #172b2e;
                font: inherit;
            }
            .ai-tutor-send {
                justify-self: end;
                min-height: 40px;
                padding: 8px 15px;
                border: 0;
                border-radius: 5px;
                background: #087f8c;
                color: #fff;
                font: inherit;
                font-weight: 600;
                cursor: pointer;
            }
            .ai-tutor-send:disabled { opacity: .6; cursor: wait; }
            @media (max-width: 520px) {
                .ai-tutor-panel { right: 8px; bottom: 8px; width: calc(100vw - 16px); height: min(72dvh, 520px); }
            }
        `;
        document.head.appendChild(style);
    }

    function ensureHelpButton() {
        const exercise = exerciseContainer.querySelector('.exercise');
        if (!exercise || exercise.querySelector('.ai-tutor-launcher')) {
            return;
        }

        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'ai-tutor-launcher';
        button.textContent = 'Pedir uma dica ao tutor';
        button.setAttribute('aria-haspopup', 'dialog');
        button.addEventListener('click', openPanel);
        exercise.appendChild(button);
    }

    function getExerciseQuestion() {
        const exercise = exerciseContainer.querySelector('.exercise');
        const question = exercise && exercise.querySelector('p');
        return question ? question.textContent.trim().slice(0, 1200) : '';
    }

    function ensurePanel() {
        if (panel) {
            return;
        }

        panel = document.createElement('section');
        panel.className = 'ai-tutor-panel';
        panel.hidden = true;
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-modal', 'false');
        panel.setAttribute('aria-label', 'Tutor de Física');
        panel.innerHTML = `
            <div class="ai-tutor-header">
                <h2>Tutor de Física</h2>
                <button type="button" class="ai-tutor-close" aria-label="Fechar tutor">&times;</button>
            </div>
            <div class="ai-tutor-transcript" aria-live="polite"></div>
            <p class="ai-tutor-status" role="status"></p>
            <form class="ai-tutor-form">
                <label for="aiTutorInput">O que está te fazendo pensar?</label>
                <textarea class="ai-tutor-input" id="aiTutorInput" maxlength="600" required></textarea>
                <button type="submit" class="ai-tutor-send">Enviar</button>
            </form>
        `;
        document.body.appendChild(panel);

        transcript = panel.querySelector('.ai-tutor-transcript');
        status = panel.querySelector('.ai-tutor-status');
        input = panel.querySelector('.ai-tutor-input');
        sendButton = panel.querySelector('.ai-tutor-send');
        panel.querySelector('.ai-tutor-close').addEventListener('click', closePanel);
        panel.querySelector('form').addEventListener('submit', sendMessage);
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && panel && !panel.hidden) {
                closePanel();
            }
        });
    }

    function openPanel() {
        ensurePanel();
        currentQuestion = getExerciseQuestion();
        panel.hidden = false;
        input.focus();
        if (!transcript.childElementCount) {
            addMessage('Tutor', 'Vamos pensar juntos. O que você já percebeu sobre as grandezas do problema?', 'assistant');
        }
        if (!config.apiUrl) {
            status.textContent = 'O serviço do tutor ainda precisa ser configurado.';
        } else {
            status.textContent = 'A conversa não envia nome nem dados pessoais.';
        }
    }

    function closePanel() {
        if (panel) {
            panel.hidden = true;
        }
    }

    function addMessage(label, text, role) {
        const message = document.createElement('div');
        message.className = 'ai-tutor-message ' + role;
        message.textContent = label + ': ' + text;
        transcript.appendChild(message);
        transcript.scrollTop = transcript.scrollHeight;
    }

    async function sendMessage(event) {
        event.preventDefault();
        const text = input.value.trim();
        if (!text) {
            return;
        }
        if (!config.apiUrl) {
            status.textContent = 'O endereço do serviço ainda não foi configurado.';
            return;
        }

        addMessage('Você', text, 'user');
        input.value = '';
        status.textContent = 'O tutor está pensando em uma pergunta para você...';
        sendButton.disabled = true;

        try {
            const response = await fetch(config.apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    simulation_key: simulationKey,
                    exercise_question: currentQuestion,
                    history: history.slice(-8),
                    message: text
                })
            });
            const payload = await response.json().catch(function () { return {}; });
            if (!response.ok) {
                throw new Error(payload.detail || 'Não foi possível obter uma dica agora.');
            }
            addMessage('Tutor', payload.reply, 'assistant');
            history.push({ role: 'user', content: text }, { role: 'assistant', content: payload.reply });
            if (history.length > 8) {
                history.splice(0, history.length - 8);
            }
            status.textContent = 'Tente explicar seu raciocínio ou peça outra pista.';
        } catch (error) {
            status.textContent = error.message || 'O tutor está indisponível. Tente novamente mais tarde.';
        } finally {
            sendButton.disabled = false;
            input.focus();
        }
    }
})();