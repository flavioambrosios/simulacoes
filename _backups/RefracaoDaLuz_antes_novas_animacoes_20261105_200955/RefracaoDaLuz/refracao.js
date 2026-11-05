let exercises = RefractionExercises.createExercises();
let currentExercise = 0;
let exerciseResults = [];
let skippedQuestions = 0;
let currentExerciseAttempts = 0;

const tracks = [
    'Nesta atividade, vamos estudar a refração da luz com a simulação do PhET. Faça previsões, teste suas ideias e registre o que observou.',
    'A refração acontece quando a luz passa entre meios em que sua velocidade de propagação é diferente. A direção do raio pode mudar. Os ângulos são medidos em relação à normal, uma linha perpendicular à superfície.',
    'O índice de refração é dado por n igual a c dividido por v. Quanto maior o índice de um meio, menor a velocidade da luz nele.',
    'A Lei de Snell relaciona os índices e os senos dos ângulos. Em incidência oblíqua, o raio se aproxima da normal ao entrar em um meio de maior índice. Ao passar para um meio de menor índice, ele se afasta da normal, quando existe raio refratado.',
    'A frequência da luz permanece constante na passagem de um meio para outro. Como a velocidade é igual ao comprimento de onda multiplicado pela frequência, o comprimento de onda muda junto com a velocidade.',
    'A reflexão interna total pode ocorrer quando a luz vai de um meio de maior índice para outro de menor índice e o ângulo de incidência supera o ângulo crítico. É um princípio utilizado em fibras ópticas.',
    'No prisma, o índice pode depender do comprimento de onda. Assim, cores diferentes podem sofrer desvios diferentes. Depois de explorar o PhET, tente os dez exercícios e escreva sua conclusão.'
];

const exampleNarrations = {
    '1': 'No primeiro exemplo, usamos n igual a c dividido por v. Para um índice de um vírgula cinco, dividimos a velocidade da luz no vácuo por um vírgula cinco e encontramos dois vezes dez elevado a oito metros por segundo.',
    '2': 'No segundo exemplo, aplicamos a Lei de Snell à passagem do ar para o vidro. Com incidência de trinta graus, o ângulo de refração é aproximadamente dezenove vírgula cinco graus. O raio se aproxima da normal.',
    '3': 'No terceiro exemplo, a luz passa do vidro para o ar. Como a incidência de cinquenta graus supera o ângulo crítico de aproximadamente quarenta e um vírgula oito graus, ocorre reflexão interna total.'
};

const scenarios = {
    'air-water': {
        medium1: 'Ar — n ≈ 1,00',
        medium2: 'Água — n ≈ 1,33',
        incident: '30°',
        refracted: '≈ 22,1°',
        observation: 'Aproxima-se da normal',
        description: 'Do ar para a água, o índice aumenta e a luz diminui sua velocidade. Com incidência de 30°, o ângulo refratado é aproximadamente 22,1°.'
    },
    'water-air': {
        medium1: 'Água — n ≈ 1,33',
        medium2: 'Ar — n ≈ 1,00',
        incident: '30°',
        refracted: '≈ 41,7°',
        observation: 'Afasta-se da normal',
        description: 'Da água para o ar, o índice diminui e a luz aumenta sua velocidade. Para incidência de 30°, ainda há refração e o ângulo refratado é aproximadamente 41,7°.'
    },
    'total-reflection': {
        medium1: 'Vidro — n ≈ 1,50',
        medium2: 'Ar — n ≈ 1,00',
        incident: '50°',
        refracted: 'Não há raio refratado',
        observation: 'Reflexão interna total',
        description: 'Do vidro para o ar, o ângulo crítico é cerca de 41,8°. Como 50° supera esse valor, ocorre reflexão interna total.'
    },
    'normal-incidence': {
        medium1: 'Ar — n ≈ 1,00',
        medium2: 'Vidro — n ≈ 1,50',
        incident: '0°',
        refracted: '0°',
        observation: 'Sem desvio de direção',
        description: 'Na incidência normal, o raio transmitido segue na mesma direção. A velocidade e o comprimento de onda mudam, mas a frequência permanece constante.'
    }
};

function updateScenarioPanel() {
    const scenario = scenarios[document.getElementById('scenarioSelect').value];
    document.getElementById('scenarioDescription').textContent = scenario.description;
    document.getElementById('medium1Display').textContent = scenario.medium1;
    document.getElementById('medium2Display').textContent = scenario.medium2;
    document.getElementById('incidentDisplay').textContent = scenario.incident;
    document.getElementById('refractedDisplay').textContent = scenario.refracted;
    document.getElementById('observationDisplay').textContent = scenario.observation;
}

function generateExercises() {
    exercises = RefractionExercises.createExercises();
}

function openExercisesModal() {
    currentExercise = 0;
    exerciseResults = [];
    skippedQuestions = 0;
    currentExerciseAttempts = 0;
    generateExercises();
    document.getElementById('exercisesModal').style.display = 'flex';
    document.getElementById('exerciseContainer').style.display = 'block';
    document.getElementById('conclusionContainer').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'none';
    showCurrentExercise();
}

function closeExercisesModal() {
    document.getElementById('exercisesModal').style.display = 'none';
    document.getElementById('mainExerciseBtn').focus();
}

function resetExerciseState() {
    exercises = [];
    currentExercise = 0;
    exerciseResults = [];
    skippedQuestions = 0;
    currentExerciseAttempts = 0;
    [
        'conclusionText', 'finalConclusion', 'enhancerNotesInput', 'studentSheet',
        'studentName', 'studentNameSelect', 'studentNameManual', 'studentGrade',
        'studentClass', 'studentTrail', 'studentEmail', 'schoolTerm', 'criticismInput',
        'suggestionInput'
    ].forEach(function (id) {
        const field = document.getElementById(id);
        if (field) {
            field.value = '';
        }
    });
    const manualName = document.getElementById('studentNameManual');
    const manualNameRow = document.getElementById('studentNameManualRow');
    if (manualName) {
        manualName.required = false;
    }
    if (manualNameRow) {
        manualNameRow.classList.add('enhancer-hidden');
    }
    const nameSelect = document.getElementById('studentNameSelect');
    if (nameSelect) {
        nameSelect.dispatchEvent(new Event('change', { bubbles: true }));
    }
    document.getElementById('exerciseContainer').replaceChildren();
    document.getElementById('exerciseContainer').style.display = 'block';
    document.getElementById('conclusionContainer').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('resultsSummary').replaceChildren();
    const emailStatus = document.getElementById('emailStatus');
    if (emailStatus) {
        emailStatus.textContent = '';
        emailStatus.className = 'email-status';
        emailStatus.style.display = 'none';
    }
}

function createButton(id, text, handler) {
    const button = document.createElement('button');
    button.id = id;
    button.type = 'button';
    button.className = 'check-btn';
    button.textContent = text;
    button.addEventListener('click', handler);
    return button;
}

function showCurrentExercise() {
    const exercise = exercises[currentExercise];
    const container = document.getElementById('exerciseContainer');
    container.replaceChildren();

    const card = document.createElement('div');
    card.className = 'exercise';
    const title = document.createElement('h3');
    title.textContent = `Exercício ${currentExercise + 1} de ${exercises.length}`;
    const question = document.createElement('p');
    question.textContent = exercise.question;
    card.append(title, question);

    const options = document.createElement('div');
    options.className = 'options';
    exercise.options.forEach(function (optionText, index) {
        const option = document.createElement('button');
        const value = exercise.id + ':' + index;
        const selected = value === exercise.selectedValue;
        option.type = 'button';
        option.className = 'option';
        option.dataset.value = value;
        option.textContent = optionText;
        option.setAttribute('aria-pressed', String(selected));
        option.classList.toggle('selected', selected);
        option.disabled = exercise.status !== 'unanswered';

        if (exercise.status !== 'unanswered' && optionText === exercise.answer) {
            option.classList.add('correct');
        } else if (exercise.status === 'wrong' && selected) {
            option.classList.add('incorrect');
        }

        option.addEventListener('click', function () {
            exercise.selectedValue = value;
            options.querySelectorAll('.option').forEach(function (item) {
                const isSelected = item === option;
                item.classList.toggle('selected', isSelected);
                item.setAttribute('aria-pressed', String(isSelected));
            });
        });
        options.appendChild(option);
    });
    card.appendChild(options);

    const result = document.createElement('div');
    result.className = 'result';
    result.setAttribute('aria-live', 'polite');
    if (exercise.status === 'wrong' || exercise.status === 'correct') {
        const feedback = document.createElement('p');
        feedback.className = exercise.status === 'correct' ? 'success' : 'error';
        feedback.textContent = exercise.status === 'correct' ? 'Correto!' : 'Incorreto. Confira a resposta e tente novamente com dados diferentes.';
        const answer = document.createElement('p');
        answer.className = 'enhancer-correct-answer';
        answer.textContent = 'Resposta correta: ' + exercise.answer;
        const explanation = document.createElement('p');
        explanation.textContent = exercise.explanation;
        result.append(feedback, answer, explanation);
    }
    card.appendChild(result);

    const actions = document.createElement('div');
    actions.className = 'button-group';
    if (exercise.status === 'unanswered') {
        actions.appendChild(createButton('checkAnswerBtn', 'Verificar resposta', function () {
            checkAnswer();
        }));
    }
    if (exercise.status === 'wrong') {
        actions.appendChild(createButton('tryAgainBtn', 'Refazer com outros dados', function () {
            generateNewExerciseOfSameType();
            showCurrentExercise();
        }));
    }
    if (exercise.status !== 'correct') {
        actions.appendChild(createButton('skipExerciseBtn', 'Pular questão', function () {
            skipExercise();
        }));
    } else {
        actions.appendChild(createButton('nextExerciseBtn', currentExercise === exercises.length - 1 ? 'Ir para a conclusão' : 'Próxima questão', function () {
            nextExercise();
        }));
    }
    card.appendChild(actions);
    container.appendChild(card);
    updateProgressBar();
}

function checkAnswer() {
    const exercise = exercises[currentExercise];
    const selected = document.querySelector('#exerciseContainer .option.selected');
    if (!selected) {
        document.querySelector('#exerciseContainer .result').textContent = 'Selecione uma alternativa antes de verificar.';
        return;
    }

    exercise.selectedValue = selected.dataset.value;
    if (selected.textContent === exercise.answer) {
        exercise.status = 'correct';
        exerciseResults.push({
            exercise: currentExercise,
            correct: true,
            skipped: false,
            attempts: currentExerciseAttempts + 1
        });
    } else {
        exercise.status = 'wrong';
        currentExerciseAttempts++;
    }
    showCurrentExercise();
}

function generateNewExerciseOfSameType() {
    const previous = exercises[currentExercise];
    exercises[currentExercise] = RefractionExercises.createExercise(previous.type, previous.variantIndex);
}

function skipExercise() {
    if (!window.confirm('Deseja pular esta questão? Ela será registrada como não acertada.')) {
        return;
    }
    exerciseResults.push({
        exercise: currentExercise,
        correct: false,
        skipped: true,
        attempts: currentExerciseAttempts
    });
    skippedQuestions++;
    nextExercise();
}

function nextExercise() {
    currentExercise++;
    currentExerciseAttempts = 0;
    if (currentExercise < exercises.length) {
        showCurrentExercise();
    } else {
        showConclusion();
    }
}

function updateProgressBar() {
    for (let index = 0; index < exercises.length; index++) {
        const item = document.getElementById('progress' + (index + 1));
        const result = exerciseResults.find(entry => entry.exercise === index);
        item.classList.toggle('active', index === currentExercise);
        item.classList.toggle('completed', index < currentExercise);
        item.setAttribute('aria-label', `Questão ${index + 1}${result ? (result.skipped ? ': pulada' : ': correta') : ''}`);
        if (index === currentExercise) {
            item.setAttribute('aria-current', 'step');
        } else {
            item.removeAttribute('aria-current');
        }
    }
}

function showConclusion() {
    document.getElementById('exerciseContainer').style.display = 'none';
    document.getElementById('conclusionContainer').style.display = 'block';
    document.getElementById('resultsContainer').style.display = 'none';
    updateProgressBar();
}

function showResults(conclusion) {
    document.getElementById('exerciseContainer').style.display = 'none';
    document.getElementById('conclusionContainer').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'block';
    updateProgressBar();
    const correct = exerciseResults.filter(result => result.correct).length;
    const summary = document.getElementById('resultsSummary');
    summary.replaceChildren();
    [
        `Questões concluídas: ${exerciseResults.length} de ${exercises.length}`,
        `Questões acertadas: ${correct} (inclui acertos após refazer)`,
        `Questões puladas: ${skippedQuestions}`,
        `Aproveitamento nos exercícios: ${Math.round(correct / exercises.length * 100)}%`
    ].forEach(function (text) {
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        summary.appendChild(paragraph);
    });
    document.getElementById('finalConclusion').value = conclusion;
}

function openSolvedExercisesModal() {
    document.getElementById('solvedExercisesModal').style.display = 'flex';
}

function closeSolvedExercisesModal() {
    document.getElementById('solvedExercisesModal').style.display = 'none';
}

function openTheoryModal() {
    document.getElementById('theoryModal').style.display = 'flex';
}

function closeTheoryModal() {
    document.getElementById('theoryModal').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function () {
    updateScenarioPanel();
    document.getElementById('scenarioSelect').addEventListener('change', updateScenarioPanel);
    document.getElementById('helpBtn').addEventListener('click', function () {
        window.alert('No PhET, selecione a tela de introdução e ligue o laser. Escolha os meios, mova o raio e use o transferidor para medir os ângulos em relação à normal. Compare as previsões com o que aparece na simulação. Na tela de prismas, explore a dispersão da luz branca.');
    });
    document.getElementById('mainExerciseBtn').addEventListener('click', function () {
        openExercisesModal();
    });
    document.getElementById('solvedExercisesBtn').addEventListener('click', function () {
        openSolvedExercisesModal();
    });
    document.getElementById('theoryBtn').addEventListener('click', openTheoryModal);
    document.querySelector('#exercisesModal .close').addEventListener('click', function () {
        closeExercisesModal();
    });
    document.querySelector('#solvedExercisesModal .close').addEventListener('click', function () {
        closeSolvedExercisesModal();
    });
    document.querySelector('#theoryModal .close').addEventListener('click', closeTheoryModal);
    document.getElementById('closeSolvedExercises').addEventListener('click', function () {
        closeSolvedExercisesModal();
    });
    document.getElementById('closeTheory').addEventListener('click', closeTheoryModal);
    document.getElementById('submitConclusion').addEventListener('click', function () {
        const conclusion = document.getElementById('conclusionText').value.trim();
        if (!conclusion) {
            window.alert('Escreva sua conclusão antes de continuar.');
            return;
        }
        showResults(conclusion);
    });
    window.addEventListener('click', function (event) {
        if (event.target === document.getElementById('exercisesModal')) {
            closeExercisesModal();
        } else if (event.target === document.getElementById('solvedExercisesModal')) {
            closeSolvedExercisesModal();
        } else if (event.target === document.getElementById('theoryModal')) {
            closeTheoryModal();
        }
    });
    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') {
            return;
        }
        if (document.querySelector('.ai-tutor-panel:not([hidden])')) {
            return;
        }
        if (document.getElementById('exercisesModal').style.display === 'flex') {
            closeExercisesModal();
        } else if (document.getElementById('solvedExercisesModal').style.display === 'flex') {
            closeSolvedExercisesModal();
        } else if (document.getElementById('theoryModal').style.display === 'flex') {
            closeTheoryModal();
        }
    });
});
