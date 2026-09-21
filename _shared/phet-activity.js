(function () {
    'use strict';

    const config = window.PHET_ACTIVITY_CONFIG || {};
    const simulationName = config.simulationName || document.title;
    const storageKey = 'phet-activity:' + (config.storageKey || simulationName.toLowerCase().replace(/[^a-z0-9]+/g, '-'));
    const sheetUrl = 'https://script.google.com/macros/s/AKfycbye5ZFZ95mUfkdUD_iZvFEvHUPww7-t_dKZQaDtvC72PqJhJtdPLs3FHeNFG6SfztXlVQ/exec';
    const emailUrl = 'https://script.google.com/macros/s/AKfycbyVQeiZ9lxSy86Lp-85VlJWRXamY2uc_-s9dCo472uLkeg_ezHeGdQPjl4HAH7Uonfi/exec';
    const teacherEmail = 'flavio.ambrosio@edu.se.df.gov.br';
    const exercises = config.exercises || [];
    let currentExercise = 0;
    let score = 0;
    let skipped = 0;
    let attempts = 0;
    let selected = null;
    let results = [];
    let speaking = false;
    let speechIndex = 0;

    const $ = id => document.getElementById(id);
    const stateKey = storageKey + ':state';

    function saveState() {
        localStorage.setItem(stateKey, JSON.stringify({ currentExercise, score, skipped, attempts, selected, results, conclusion: $('conclusionText')?.value || '', form: readForm() }));
        const status = $('saveStatus');
        if (status) status.textContent = 'Progresso salvo neste dispositivo.';
    }

    function readForm() {
        return ['studentName', 'studentGrade', 'studentClass', 'studentEmail', 'criticismInput', 'suggestionInput', 'finalConclusion'].reduce((data, id) => {
            data[id] = $(id)?.value || '';
            return data;
        }, {});
    }

    function restoreState() {
        try {
            const saved = JSON.parse(localStorage.getItem(stateKey) || 'null');
            if (!saved) return false;
            currentExercise = Number(saved.currentExercise) || 0;
            score = Number(saved.score) || 0;
            skipped = Number(saved.skipped) || 0;
            attempts = Number(saved.attempts) || 0;
            selected = saved.selected ?? null;
            results = Array.isArray(saved.results) ? saved.results : [];
            const form = saved.form || {};
            Object.keys(form).forEach(id => { if ($(id)) $(id).value = form[id]; });
            if ($('conclusionText')) $('conclusionText').value = saved.conclusion || '';
            return true;
        } catch (error) { return false; }
    }

    function updateProgress() {
        const bar = $('progress');
        bar.innerHTML = exercises.map((_, index) => `<span class="progress-item ${index < currentExercise ? 'completed' : ''} ${index === currentExercise ? 'active' : ''}">${index + 1}</span>`).join('');
    }

    function renderExercise() {
        if (currentExercise >= exercises.length) { showConclusion(); return; }
        updateProgress();
        const exercise = exercises[currentExercise];
        const chosen = selected;
        $('exerciseContainer').innerHTML = `<article class="exercise"><h3>Questão ${currentExercise + 1} de ${exercises.length}</h3><p>${exercise.question}</p><div class="options">${exercise.options.map((option, index) => `<button type="button" class="option ${chosen === index ? 'selected' : ''}" data-index="${index}">${option}</button>`).join('')}</div><div class="result" id="resultBox"></div><button type="button" class="check-btn" id="checkButton">Verificar resposta</button></article>`;
        document.querySelectorAll('.option').forEach(button => button.addEventListener('click', () => { selected = Number(button.dataset.index); document.querySelectorAll('.option').forEach(item => item.classList.remove('selected')); button.classList.add('selected'); saveState(); }));
        $('checkButton').addEventListener('click', checkAnswer);
    }

    function checkAnswer() {
        const exercise = exercises[currentExercise];
        const resultBox = $('resultBox');
        if (selected === null) { resultBox.textContent = 'Selecione uma alternativa antes de verificar.'; resultBox.className = 'result error'; return; }
        document.querySelectorAll('.option').forEach((button, index) => {
            button.disabled = true;
            if (index === exercise.answer) button.classList.add('correct');
            if (index === selected && selected !== exercise.answer) button.classList.add('incorrect');
        });
        if (selected === exercise.answer) {
            score++;
            results.push({ exercise: currentExercise, correct: true, skipped: false, attempts: attempts + 1 });
            resultBox.textContent = 'Correto! ' + exercise.explanation;
            resultBox.className = 'result success';
            $('checkButton').disabled = true;
            saveState();
            setTimeout(nextExercise, 1100);
            return;
        }
        attempts++;
        resultBox.innerHTML = `<strong>Incorreto.</strong> ${exercise.explanation}<div class="button-row"><button type="button" id="tryAgainButton">Tentar novamente</button><button type="button" id="skipButton">Pular questão</button></div>`;
        resultBox.className = 'result error';
        $('tryAgainButton').addEventListener('click', tryAgain);
        $('skipButton').addEventListener('click', skipExercise);
        saveState();
    }

    function tryAgain() {
        const old = exercises[currentExercise];
        const next = typeof old.variant === 'function' ? old.variant() : old;
        exercises[currentExercise] = Object.assign({}, next);
        selected = null;
        renderExercise();
        saveState();
    }

    function skipExercise() {
        skipped++;
        results.push({ exercise: currentExercise, correct: false, skipped: true, attempts });
        nextExercise();
    }

    function nextExercise() {
        currentExercise++;
        attempts = 0;
        selected = null;
        saveState();
        renderExercise();
    }

    function openExercises() {
        $('exerciseModal').style.display = 'flex';
        if (!restoreState() || currentExercise >= exercises.length) { currentExercise = 0; score = 0; skipped = 0; attempts = 0; selected = null; results = []; }
        $('exerciseView').style.display = 'block'; $('conclusionView').style.display = 'none'; $('resultView').style.display = 'none';
        renderExercise();
    }

    function showConclusion() {
        $('exerciseView').style.display = 'none'; $('conclusionView').style.display = 'block'; $('resultView').style.display = 'none';
        $('conclusionText').value = $('conclusionText').value || '';
        saveState();
    }

    function showResults() {
        const conclusion = $('conclusionText').value.trim();
        if (!conclusion) { alert('Escreva uma conclusão antes de continuar.'); return; }
        $('exerciseView').style.display = 'none'; $('conclusionView').style.display = 'none'; $('resultView').style.display = 'block';
        $('resultsSummary').innerHTML = `<p>Questões: ${exercises.length}</p><p>Acertos: ${score}</p><p>Questões puladas: ${skipped}</p><p>Nota: ${Math.round(score / exercises.length * 100)}%</p>`;
        $('finalConclusion').value = conclusion;
        saveState();
    }

    function sendResults() {
        const form = readForm();
        if (!form.studentName || !form.studentGrade || !form.studentClass || !form.finalConclusion) { alert('Preencha nome, série, turma e conclusão.'); return; }
        const payload = { timestamp: new Date().toLocaleString('pt-BR'), estudante: form.studentName, nome_aluno: form.studentName, série: form.studentGrade, turma: form.studentClass, email: form.studentEmail, to_email: teacherEmail, simulação: simulationName, acertos: `${score}/${exercises.length}`, acertos_erros: `${score}/${exercises.length - score}`, questoes_puladas: skipped, nota: `${Math.round(score / exercises.length * 100)}%`, conclusão: form.finalConclusion, críticas: form.criticismInput, sugestões: form.suggestionInput };
        const button = $('sendResults'); button.disabled = true; button.textContent = 'Enviando...'; $('sendStatus').textContent = 'Enviando dados para a planilha e para o e-mail...';
        fetch(sheetUrl, { method: 'POST', mode: 'no-cors', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }).then(() => fetch(emailUrl, { method: 'POST', mode: 'no-cors', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })).then(() => { $('sendStatus').textContent = form.studentEmail ? 'Dados enviados e cópia solicitada por e-mail.' : 'Dados enviados ao professor.'; button.textContent = 'Enviado'; }).catch(() => { $('sendStatus').textContent = 'Não foi possível confirmar o envio. Tente novamente.'; button.disabled = false; button.textContent = 'Enviar resultados'; });
    }

    function speak(text, button) {
        if (!window.speechSynthesis) return;
        speechSynthesis.cancel();
        speaking = true;
        if (button) { button.textContent = 'Parar áudio'; button.classList.add('playing'); }
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'pt-BR'; utterance.rate = 0.95;
        utterance.onend = () => { speaking = false; if (button) { button.textContent = 'Ouvir resolução'; button.classList.remove('playing'); } };
        speechSynthesis.speak(utterance);
    }

    function setupAudio() {
        const tracks = config.tracks || [
            `Olá. Esta é a simulação sobre ${simulationName}. Explore o PhET e observe as grandezas destacadas na página.`,
            `Depois da exploração, resolva os exercícios e justifique suas respostas usando as relações físicas apresentadas.`,
            `Você pode pausar e retornar à atividade: o progresso fica salvo neste dispositivo.`
        ];
        const bar = document.createElement('div'); bar.className = 'audio-bar'; bar.innerHTML = `<button type="button" id="audioButton">Ouvir apresentação</button><span id="audioCounter">Áudio inicial</span>`;
        document.querySelector('.container').appendChild(bar);
        $('audioButton').addEventListener('click', () => { if (speaking) { speechSynthesis.cancel(); speaking = false; $('audioButton').textContent = 'Ouvir apresentação'; return; } speak(tracks[speechIndex % tracks.length], $('audioButton')); speechIndex++; });
        document.querySelectorAll('.solved-exercise').forEach((item, index) => { const button = document.createElement('button'); button.type = 'button'; button.className = 'audio-solved'; button.textContent = 'Ouvir resolução'; button.addEventListener('click', () => speak(item.innerText, button)); item.appendChild(button); });
    }

    function setup() {
        $('exerciseButton').addEventListener('click', openExercises);
        $('closeExercise').addEventListener('click', () => { saveState(); $('exerciseModal').style.display = 'none'; });
        $('submitConclusion').addEventListener('click', showResults);
        $('sendResults').addEventListener('click', sendResults);
        $('solvedButton').addEventListener('click', () => $('solvedModal').style.display = 'flex');
        $('theoryButton').addEventListener('click', () => $('theoryModal').style.display = 'flex');
        document.querySelectorAll('.close-modal').forEach(button => button.addEventListener('click', () => { if (button.dataset.close) $(button.dataset.close).style.display = 'none'; }));
        document.querySelectorAll('#studentName, #studentGrade, #studentClass, #studentEmail, #criticismInput, #suggestionInput, #finalConclusion, #conclusionText').forEach(field => field.addEventListener('input', saveState));
        setupAudio();
        if (localStorage.getItem(stateKey)) { $('resumeNotice').textContent = 'Há um progresso salvo. O botão de exercícios continuará do ponto guardado.'; }
    }

    window.addEventListener('DOMContentLoaded', setup);
})();