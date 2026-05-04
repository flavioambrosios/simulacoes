const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbye5ZFZ95mUfkdUD_iZvFEvHUPww7-t_dKZQaDtvC72PqJhJtdPLs3FHeNFG6SfztXlVQ/exec';

const QUESTION_PAIRS = [
    {
        theme: 'Redes sociais + saúde mental',
        left: 'O uso exagerado de redes sociais pode aumentar ansiedade, atrapalhar o sono e comprometer a saúde mental de adolescentes.',
        right: 'O uso exagerado de redes sociais nunca afeta ansiedade, sono ou saúde mental de adolescentes.'
    },
    {
        theme: 'IA + redes sociais + estudo',
        left: 'Algoritmos de inteligência artificial podem manter o estudante preso por mais tempo nas plataformas e prejudicar a concentração para estudo e trabalho.',
        right: 'Algoritmos de inteligência artificial não interferem no tempo de uso nem na concentração para estudo e trabalho.'
    },
    {
        theme: 'IA + autonomia juvenil',
        left: 'Ferramentas de IA podem ajudar adolescentes a estudar e se organizar, desde que as respostas sejam conferidas com senso crítico.',
        right: 'Ferramentas de IA só atrapalham, por isso nunca podem contribuir com estudo ou organização do estudante.'
    },
    {
        theme: 'IA + saúde mental',
        left: 'Um chatbot pode oferecer acolhimento inicial, mas não substitui atendimento profissional quando a saúde mental exige cuidado especializado.',
        right: 'Um chatbot pode substituir totalmente psicólogos, médicos e a rede de apoio em qualquer situação emocional.'
    },
    {
        theme: 'Redes sociais + autoestima',
        left: 'Comparar a própria vida com perfis idealizados nas redes pode prejudicar autoestima e bem-estar emocional.',
        right: 'Comparar a própria vida com perfis idealizados fortalece sempre a autoestima e nunca causa desconforto emocional.'
    },
    {
        theme: 'Redes sociais + trabalho juvenil',
        left: 'A reputação digital construída nas redes pode influenciar oportunidades de estágio, trabalho e participação em projetos escolares.',
        right: 'O que um jovem publica nas redes não interfere em oportunidades de estágio, trabalho ou projetos escolares.'
    },
    {
        theme: 'IA + trabalho + golpes',
        left: 'Golpes de emprego podem usar textos, imagens e vozes gerados por IA para parecer confiáveis nas redes sociais.',
        right: 'Golpes de emprego não usam recursos digitais para parecer confiáveis, então basta ler rápido para identificar todos.'
    },
    {
        theme: 'Trabalho juvenil + saúde mental',
        left: 'Quando estudo, trabalho e descanso não ficam equilibrados, o adolescente pode apresentar estresse e queda no rendimento.',
        right: 'Mesmo sem equilíbrio entre estudo, trabalho e descanso, o adolescente não sofre estresse nem queda no rendimento.'
    },
    {
        theme: 'Sono + redes sociais',
        left: 'Levar notificações para a madrugada pode atrapalhar o sono e afetar humor, memória e aprendizagem.',
        right: 'Receber livremente notificações na madrugada não altera sono, humor, memória nem aprendizagem.'
    },
    {
        theme: 'Redes sociais + proteção',
        left: 'Denunciar cyberbullying e buscar ajuda de adultos responsáveis protege a saúde mental e a convivência digital.',
        right: 'Cyberbullying deve ser ignorado sempre, porque denunciar ou pedir ajuda só piora a saúde mental.'
    },
    {
        theme: 'IA + mercado de trabalho',
        left: 'Sistemas de IA usados em seleção podem reproduzir preconceitos quando são treinados com dados injustos.',
        right: 'Sistemas de IA usados em seleção são sempre neutros e nunca reproduzem preconceitos dos dados.'
    },
    {
        theme: 'Trabalho juvenil + direitos',
        left: 'Entrar cedo no mundo do trabalho sem orientação e sem direitos garantidos pode expor o jovem a exploração e sofrimento psíquico.',
        right: 'Entrar cedo no mundo do trabalho mesmo sem orientação e sem direitos garantidos nunca expõe o jovem a exploração ou sofrimento psíquico.'
    },
    {
        theme: 'Redes sociais + identidade',
        left: 'Curtidas e seguidores não definem o valor pessoal nem a competência de alguém para estudar ou trabalhar.',
        right: 'Curtidas e seguidores, sem dúvida, definem com precisão o valor pessoal e a competência de alguém para estudar ou trabalhar.'
    },
    {
        theme: 'Informação + saúde mental',
        left: 'Checar a fonte antes de compartilhar conteúdos sobre saúde mental, trabalho e IA reduz desinformação e riscos.',
        right: 'Não é preciso checar fonte ao compartilhar conteúdos sobre saúde mental, trabalho e IA nas redes.'
    },
    {
        theme: 'IA + autonomia de estudo',
        left: 'A IA pode sugerir rotinas de estudo, mas não deve decidir sozinha o que o estudante pensa ou entrega como produção.',
        right: 'A IA deve decidir sozinha o que o estudante faz e entrega, porque senso crítico não é necessário.'
    },
    {
        theme: 'Produtividade + saúde mental',
        left: 'A pressão para parecer sempre produtivo nas redes pode gerar culpa, cansaço e comparação prejudicial.',
        right: 'A pressão para parecer sempre produtivo nas redes trazem sempre motivação e nunca gera culpa ou cansaço.'
    },
    {
        theme: 'Privacidade + trabalho',
        left: 'Expor dados pessoais demais nas redes pode favorecer golpes, assédio e prejuízos emocionais e profissionais.',
        right: 'Expor dados pessoais nas redes é sempre seguro e nunca favorece golpes, assédio ou prejuízos.'
    },
    {
        theme: 'Bem-estar digital',
        left: 'Fazer pausas nas telas ajuda o cérebro a recuperar atenção e favorece o equilíbrio emocional.',
        right: 'Fazer pausas nas telas não traz nenhum benefício para atenção nem para o equilíbrio emocional.'
    },
    {
        theme: 'Educação digital + uso consciente',
        left: 'Passar muitas horas conectado não significa, por si só, desenvolver educação digital crítica e responsável.',
        right: 'Quanto mais horas conectado, maior é automaticamente a educação digital crítica e responsável.'
    },
    {
        theme: 'Proteção + desafios online',
        left: 'Se um desafio online ameaça saúde, estudo ou dignidade, o adolescente deve parar e buscar apoio confiável.',
        right: 'Se um desafio online ameaça saúde, estudo ou dignidade, o adolescente deve continuar para ganhar visibilidade.'
    },
    {
        theme: 'IA + imagem corporal',
        left: 'Imagens geradas ou editadas por IA podem criar padrões irreais de aparência e aumentar insatisfação corporal.',
        right: 'Imagens geradas ou editadas por IA mostram a realidade exatamente como ela é e não influenciam insatisfação corporal.'
    },
    {
        theme: 'Trabalho + convivência',
        left: 'Mesmo com avanço tecnológico, empatia, cooperação e responsabilidade continuam importantes no trabalho e na escola.',
        right: 'Com o avanço tecnológico, empatia, cooperação e responsabilidade deixaram de ser importantes no trabalho e na escola.'
    },
    {
        theme: 'Trabalho infantil/adolescente',
        left: 'Quando o trabalho dificulta ou impede frequência escolar, descanso e desenvolvimento, a juventude fica prejudicda.',
        right: 'Quando o trabalho dificulta ou impede frequência escolar, descanso e desenvolvimento, automaticamente a juventude fica foratelcida.'
    },
    {
        theme: 'Redes sociais + cidadania',
        left: 'As redes sociais podem mobilizar apoio, informação e campanhas solidárias, mas também espalham boatos com rapidez.',
        right: 'As redes sociais só servem para mobilizar apoio verdadeiro e nunca espalham boatos com rapidez.'
    },
    {
        theme: 'Uso de telas + contexto',
        left: 'Idade, contexto, tempo de uso e qualidade das interações importam quando se fala em bem-estar digital.',
        right: 'Idade, contexto, tempo de uso e qualidade das interações não importam para o bem-estar digital.'
    },
    {
        theme: 'IA + fake news',
        left: 'Ferramentas de IA podem ajudar a analisar padrões suspeitos, mas a decisão final sobre uma notícia exige julgamento humano.',
        right: 'Se uma ferramenta de IA disser que a notícia é confiável, não há mais necessidade de julgamento humano.'
    },
    {
        theme: 'Violência digital + saúde mental',
        left: 'Humilhações em memes, prints e comentários podem causar sofrimento real e afetar a saúde mental.',
        right: 'Humilhações em memes, prints e comentários nunca causam sofrimento real nem afetam a saúde mental.'
    },
    {
        theme: 'Privacidade + algoritmos',
        left: 'Aceitar termos sem ler pode permitir uso amplo dos dados por plataformas e sistemas algorítmicos.',
        right: 'Aceitar termos sem ler impede qualquer uso dos dados pelas plataformas e pelos sistemas algorítmicos.'
    },
    {
        theme: 'Rotina saudável',
        left: 'Uma rotina saudável inclui sono, estudo, lazer, convivência offline e uso equilibrado das tecnologias.',
        right: 'Uma rotina saudável dispensa sono, lazer e convivência offline quando há muito conteúdo digital disponível.'
    },
    {
        theme: 'Trabalho juvenil + redes sociais',
        left: 'Conselhos virais que circulam frequentemente nas redes sociais sobre produtividade podem ignorar limites físicos e emocionais de adolescentes que estudam e trabalham.',
        right: 'Conselhos virais que circulam frequentemente nas redes sociais sobre produtividade sempre respeitam limites físicos e emocionais de adolescentes.'
    },
    {
        theme: 'IA + ética escolar',
        left: 'Usar IA na escola com transparência e autoria clara é diferente de copiar respostas como se fossem próprias.',
        right: 'Usar IA na escola é sempre igual a copiar respostas, mesmo quando há transparência e autoria clara.'
    },
    {
        theme: 'Comparação social + ansiedade',
        left: 'Comparar corpo, carreira e estilo de vida com o que aparece nas redes pode aumentar ansiedade e frustração.',
        right: 'Comparar corpo, carreira e estilo de vida com o que aparece nas redes ajuda a reduzir a ansiedade e a frustração.'
    },
    {
        theme: 'Reputação digital + oportunidades',
        left: 'Posturas respeitosas no ambiente digital ajudam a construir reputação positiva para a vida acadêmica e profissional.',
        right: 'Posturas respeitosas no ambiente digital não têm relação com reputação acadêmica ou profissional.'
    },
    {
        theme: 'Direitos do trabalho',
        left: 'Conhecer direitos trabalhistas ajuda o jovem a identificar propostas abusivas divulgadas na internet.',
        right: 'Conhecer direitos trabalhistas não ajuda em nada a identificar propostas abusivas divulgadas na internet.'
    },
    {
        theme: 'Limites digitais + cuidado',
        left: 'Cuidar da saúde mental inclui pedir ajuda, estabelecer limites com telas e reconhecer sinais de sobrecarga.',
        right: 'Cuidar da saúde mental significa apenas continuar usando telas sem limites e ignorar sinais de sobrecarga.'
    },
    {
        theme: 'Algoritmos + bolhas',
        left: 'Sistemas de recomendação de machine learning não são neutros: eles selecionam o que aparece e podem reforçar bolhas de opinião.',
        right: 'Sistemas de recomendação de machine learning mostram tudo de forma neutra e nunca reforçam bolhas de opinião.'
    },
    {
        theme: 'Desafios online + segurança',
        left: 'Nem todo conteúdo viral é seguro; popularidade não substitui análise de risco e responsabilidade.',
        right: 'Se um conteúdo é viral, ele já é seguro e dispensa análise de risco e responsabilidade.'
    },
    {
        theme: 'IA + aprendizagem',
        left: 'Usar IA para plagiar compromete a aprendizagem, a autoria e a confiança no próprio processo de estudo.',
        right: 'Usar IA para plagiar até fortalece a aprendizagem, pois a autoria e a confiança no próprio processo de estudo são menos importantes.'
    },
    {
        theme: 'Autoproteção nas redes',
        left: 'Bloquear ofensores, moderar comentários e ajustar privacidade são medidas legítimas de proteção digital.',
        right: 'Bloquear ofensores, moderar comentários e ajustar privacidade são medidas inúteis de proteção digital.'
    },
    {
        theme: 'Descanso + desempenho',
        left: 'Adolescentes precisam também de descanso; excesso de trabalho e hiperconexão podem reduzir atenção e rendimento.',
        right: 'Adolescentes não precisam de descanso, porque excesso de trabalho e hiperconexão melhoram atenção e rendimento.'
    },
    {
        theme: 'Redes sociais + apoio',
        left: 'Quando usadas com equilíbrio, as redes podem fortalecer grupos de estudo, apoio entre colegas e projetos coletivos.',
        right: 'Mesmo com equilíbrio, as redes nunca fortalecem grupos de estudo, apoio entre colegas ou projetos coletivos.'
    },
    {
        theme: 'Imagem pública + seleção',
        left: 'Recrutadores, projetos e instituições podem observar postagens públicas antes de oferecer oportunidades.',
        right: 'Recrutadores, projetos e instituições jamais observam postagens públicas antes de oferecer oportunidades.'
    },
    {
        theme: 'Violência digital + dignidade',
        left: 'Zombarias online sobre trabalho, aparência ou desempenho escolar também podem ser formas de violência.',
        right: 'Zombarias online sobre trabalho, aparência ou desempenho escolar não podem ser consideradas violência.'
    },
    {
        theme: 'IA + verificação',
        left: 'Resumos gerados por IA podem economizar tempo, mas precisam ser conferidos antes de virar fonte de estudo.',
        right: 'Resumos gerados por IA são sempre corretos, então não precisam ser conferidos antes do estudo.'
    },
    {
        theme: 'Produtividade + autocuidado',
        left: 'Aplicativos de organização pessoal e profissional ajudam mais quando servem ao planejamento, e não à vigilância obsessiva de si mesmo.',
        right: 'Aplicativos de organização pessoal e profissional só funcionam quando o jovem se torna um vigilante obsessivo de si mesmo.'
    },
    {
        theme: 'Saúde mental + informação',
        left: 'Compartilhar conselhos sobre saúde emocional sem fonte confiável pode espalhar erros e causar danos.',
        right: 'Compartilhar conselhos sobre saúde emocional sem fonte confiável é sempre seguro e não pode causar danos.'
    },
    {
        theme: 'Educação digital + ética',
        left: 'Uma atividade de educação digital deve valorizar técnica, ética, cidadania e cuidado com o bem-estar.',
        right: 'Uma atividade de educação digital pode ignorar ética, cidadania e bem-estar, pois o que importa é a técnica.'
    },
    {
        theme: 'Segurança digital + oportunidades',
        left: 'Senhas fortes e configurações de privacidade ajudam a proteger a imagem, os dados e futuras oportunidades.',
        right: 'Senhas fortes e configurações de privacidade não fazem diferença na proteção de imagem, dados ou oportunidades.'
    },
    {
        theme: 'Saúde mental + rede de apoio',
        left: 'Se um conteúdo digital faz o estudante se sentir pressionado ou mal, fazer uma pausa e conversar com alguém de confiança pode ajudar.',
        right: 'Se um conteúdo digital faz o estudante se sentir pressionado ou mal, a melhor decisão é resolver tudo sozinho e continuar exposto.'
    },
    {
        theme: 'IA + carreira',
        left: 'A inteligência artificial muda profissões, mas continua exigindo responsabilidade, estudo permanente e decisões humanas.',
        right: 'A inteligência artificial elimina a necessidade de responsabilidade, estudo permanente e decisões humanas no trabalho.'
    }
].map((pair, index) => ({
    pairIndex: index + 1,
    questions: [
        {
            number: index * 2 + 1,
            text: pair.left,
            correct: true
        },
        {
            number: index * 2 + 2,
            text: pair.right,
            correct: false
        }
    ],
    theme: pair.theme
}));

const APP_CONFIG = {
    evaluationName: 'Avaliação Bimestral - Educação Digital',
    activityName: 'Avaliação Bimestral - Educação Digital',
    category: 'avaliacao',
    questionPairLimit: QUESTION_PAIRS.length,
    scoreHeader: '',
    ...(window.AVALIACAO_CONFIG || {})
};

const ACTIVE_PAIR_LIMIT = Math.max(1, Math.min(
    QUESTION_PAIRS.length,
    Number(APP_CONFIG.questionPairLimit) || QUESTION_PAIRS.length
));
const ACTIVE_QUESTION_PAIRS = QUESTION_PAIRS.slice(0, ACTIVE_PAIR_LIMIT);
const TOTAL_PAIRS = ACTIVE_QUESTION_PAIRS.length;
const TOTAL_QUESTIONS = ACTIVE_QUESTION_PAIRS.reduce((total, pair) => total + pair.questions.length, 0);

const DEFAULT_DATABASE = {
    bySheet: {},
    bySerieTurma: {},
    byTrilha: {}
};

const STUDENT_SOURCE = typeof STUDENT_DATABASE !== 'undefined' ? STUDENT_DATABASE : DEFAULT_DATABASE;

const state = {
    profile: null,
    result: null,
    examQuestions: [],
    questionPairs: []
};

const introScreen = document.getElementById('intro-screen');
const examScreen = document.getElementById('exam-screen');
const resultScreen = document.getElementById('result-screen');
const introForm = document.getElementById('intro-form');
const examForm = document.getElementById('exam-form');
const questionList = document.getElementById('question-list');
const studentSelect = document.getElementById('student-select');
const manualNameField = document.getElementById('manual-name-field');
const manualNameInput = document.getElementById('manual-name');
const introStatus = document.getElementById('intro-status');
const examStatus = document.getElementById('exam-status');
const resultStatus = document.getElementById('result-status');
const progressFill = document.getElementById('progress-fill');
const progressLabel = document.getElementById('progress-label');
const studentSummary = document.getElementById('student-summary');
const backButton = document.getElementById('back-button');
const restartButton = document.getElementById('restart-button');

applyStaticCounters();
resetExamOrder();
renderQuestionCards();
attachEvents();
populateStudentOptions();

function applyStaticCounters() {
    progressLabel.textContent = `0 de ${TOTAL_QUESTIONS} respondidas`;
    document.getElementById('result-pairs').textContent = `0/${TOTAL_PAIRS}`;
    document.getElementById('result-individual').textContent = `0/${TOTAL_QUESTIONS}`;
}

function attachEvents() {
    introForm.addEventListener('submit', handleIntroSubmit);
    examForm.addEventListener('change', updateProgress);
    examForm.addEventListener('submit', handleExamSubmit);
    backButton.addEventListener('click', () => showScreen('intro'));
    restartButton.addEventListener('click', restartApplication);

    ['serie', 'turma', 'trilha'].forEach((fieldId) => {
        document.getElementById(fieldId).addEventListener('change', populateStudentOptions);
    });

    studentSelect.addEventListener('change', handleStudentSelectionChange);
}

function resetExamOrder() {
    state.questionPairs = ACTIVE_QUESTION_PAIRS.map((pair) => ({
        pairIndex: pair.pairIndex,
        theme: pair.theme,
        questions: pair.questions.map((question, questionIndex) => ({
            id: `pair-${pair.pairIndex}-q-${questionIndex + 1}`,
            pairIndex: pair.pairIndex,
            originalNumber: question.number,
            theme: pair.theme,
            text: question.text,
            correct: question.correct
        }))
    }));

    state.examQuestions = shuffleQuestions(state.questionPairs.flatMap((pair) => pair.questions));
}

function renderQuestionCards() {
    questionList.innerHTML = state.examQuestions.map((question, index) => `
        <article class="question-card pending" data-question-card="${question.id}">
            <div class="pair-head">
                <span class="question-number">Questão ${index + 1}</span>
                <span class="pair-tag">${escapeHtml(question.theme)}</span>
            </div>
            <p>${question.text}</p>
            <div class="options">
                <label class="option">
                    <input type="radio" name="q-${question.id}" value="C" required>
                    <span>Certo</span>
                </label>
                <label class="option">
                    <input type="radio" name="q-${question.id}" value="E" required>
                    <span>Errado</span>
                </label>
            </div>
        </article>
    `).join('');
}

function populateStudentOptions() {
    const serie = document.getElementById('serie').value;
    const turma = document.getElementById('turma').value;
    const trilha = document.getElementById('trilha').value;
    const names = getStudentNames({ serie, turma, trilha });

    const placeholder = names.length > 0
        ? '<option value="">Selecione o nome</option>'
        : '<option value="">Nenhum nome encontrado para este recorte</option>';

    const options = names.map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join('');
    studentSelect.innerHTML = `${placeholder}${options}<option value="__OTHER__">Meu nome não está na lista</option>`;
    studentSelect.value = '';
    manualNameInput.value = '';
    manualNameField.classList.add('hidden');
}

function getStudentNames({ serie, turma, trilha }) {
    const names = new Set();
    const preferredSheet = resolveSheetName({ serie, turma, trilha });

    if (preferredSheet && STUDENT_SOURCE.bySheet[preferredSheet]) {
        STUDENT_SOURCE.bySheet[preferredSheet].forEach((name) => names.add(name));
    }

    const serieTurmaKey = `${serie}|${turma}`;
    if (STUDENT_SOURCE.bySerieTurma[serieTurmaKey]) {
        STUDENT_SOURCE.bySerieTurma[serieTurmaKey].forEach((name) => names.add(name));
    }

    if (trilha && STUDENT_SOURCE.byTrilha[trilha]) {
        STUDENT_SOURCE.byTrilha[trilha].forEach((name) => names.add(name));
    }

    return Array.from(names).sort((first, second) => first.localeCompare(second, 'pt-BR'));
}

function resolveSheetName({ serie, turma, trilha }) {
    if (trilha && !['Outra', 'Nenhuma'].includes(trilha) && STUDENT_SOURCE.bySheet[trilha]) {
        return trilha;
    }

    const normalizedSerie = normalizeSerieForSheet(serie);
    const serieTurmaName = normalizedSerie && turma ? `${normalizedSerie} ${turma}` : '';
    if (serieTurmaName && STUDENT_SOURCE.bySheet[serieTurmaName]) {
        return serieTurmaName;
    }

    return '';
}

function normalizeSerieForSheet(serie) {
    return String(serie || '')
        .replace('º', 'o')
        .trim();
}

function postJsonNoCors(url, payload) {
    return fetch(url, {
        method: 'POST',
        mode: 'no-cors',
        headers: {
            'Content-Type': 'text/plain;charset=utf-8'
        },
        body: JSON.stringify(payload)
    });
}

function addStudentToRuntimeSource(profile) {
    const studentName = String(profile.manualName || '').trim();
    if (!studentName) {
        return;
    }

    const sheetName = resolveSheetName({ serie: profile.serie, turma: profile.turma, trilha: profile.trilha })
        || profile.trilha
        || `${normalizeSerieForSheet(profile.serie)} ${profile.turma}`;
    const serieTurmaKey = `${profile.serie}|${profile.turma}`;

    STUDENT_SOURCE.bySheet[sheetName] = STUDENT_SOURCE.bySheet[sheetName] || [];
    STUDENT_SOURCE.bySerieTurma[serieTurmaKey] = STUDENT_SOURCE.bySerieTurma[serieTurmaKey] || [];
    if (profile.trilha) {
        STUDENT_SOURCE.byTrilha[profile.trilha] = STUDENT_SOURCE.byTrilha[profile.trilha] || [];
    }

    if (!STUDENT_SOURCE.bySheet[sheetName].includes(studentName)) {
        STUDENT_SOURCE.bySheet[sheetName].push(studentName);
    }

    if (!STUDENT_SOURCE.bySerieTurma[serieTurmaKey].includes(studentName)) {
        STUDENT_SOURCE.bySerieTurma[serieTurmaKey].push(studentName);
    }

    if (profile.trilha && !STUDENT_SOURCE.byTrilha[profile.trilha].includes(studentName)) {
        STUDENT_SOURCE.byTrilha[profile.trilha].push(studentName);
    }
}

function handleStudentSelectionChange() {
    const manualMode = studentSelect.value === '__OTHER__';
    manualNameField.classList.toggle('hidden', !manualMode);
    manualNameInput.required = manualMode;
    if (!manualMode) {
        manualNameInput.value = '';
    }
}

function handleIntroSubmit(event) {
    event.preventDefault();
    clearStatus(introStatus);

    const formData = new FormData(introForm);
    const profile = {
        serie: formData.get('serie'),
        turma: formData.get('turma'),
        bimestre: formData.get('bimestre'),
        assessmentMode: formData.get('assessmentMode'),
        trilha: formData.get('trilha'),
        selectedName: formData.get('studentSelect'),
        manualName: String(formData.get('manualName') || '').trim(),
        studentEmail: String(formData.get('studentEmail') || '').trim()
    };

    if (!profile.serie || !profile.turma || !profile.bimestre || !profile.trilha) {
        showStatus(introStatus, 'Preencha série, turma, bimestre e trilha antes de continuar.', 'warning');
        return;
    }

    if (!profile.selectedName) {
        showStatus(introStatus, 'Selecione um nome na lista ou escolha a opção para digitar manualmente.', 'warning');
        return;
    }

    if (profile.selectedName === '__OTHER__' && !profile.manualName) {
        showStatus(introStatus, 'Digite o nome completo quando ele não estiver na lista.', 'warning');
        manualNameInput.focus();
        return;
    }

    if (profile.selectedName === '__OTHER__') {
        addStudentToRuntimeSource(profile);
    }

    const configuredScoreHeader = String(APP_CONFIG.scoreHeader || '').trim();

    state.profile = {
        serie: profile.serie,
        turma: profile.turma,
        bimestre: profile.bimestre,
        assessmentMode: profile.assessmentMode,
        isRecovery: profile.assessmentMode === 'recuperacao',
        trilha: profile.trilha,
        nome: profile.selectedName === '__OTHER__' ? profile.manualName : profile.selectedName,
        nomeManual: profile.selectedName === '__OTHER__' ? profile.manualName : '',
        email: profile.studentEmail,
        sheetName: resolveSheetName({ serie: profile.serie, turma: profile.turma, trilha: profile.trilha }),
        scoreHeader: configuredScoreHeader || (profile.assessmentMode === 'recuperacao' ? 'recuperacao' : 'prova')
    };

    updateStudentSummary();
    updateProgress();
    showScreen('exam');
}

function updateStudentSummary() {
    if (!state.profile) {
        studentSummary.innerHTML = '';
        return;
    }

    const items = [
        `Estudante: ${state.profile.nome}`,
        `Série: ${state.profile.serie}`,
        `Turma: ${state.profile.turma}`,
        `Bimestre: ${state.profile.bimestre}`,
        `Tipo: ${state.profile.isRecovery ? 'Recuperação' : 'Prova regular'}`,
        `Trilha: ${state.profile.trilha}`
    ];

    if (state.profile.sheetName) {
        items.push(`Base: ${state.profile.sheetName}`);
    }

    if (state.profile.email) {
        items.push(`Email: ${state.profile.email}`);
    }

    studentSummary.innerHTML = items.map((item) => `<span class="summary-pill">${escapeHtml(item)}</span>`).join('');
}

function updateProgress() {
    const answered = state.examQuestions.reduce((count, question) => {
        return count + (getAnswer(question.id) ? 1 : 0);
    }, 0);

    progressLabel.textContent = `${answered} de ${TOTAL_QUESTIONS} respondidas`;
    progressFill.style.width = `${(answered / TOTAL_QUESTIONS) * 100}%`;

    state.examQuestions.forEach((question) => {
        const questionElement = document.querySelector(`[data-question-card="${question.id}"]`);
        questionElement.classList.toggle('pending', !Boolean(getAnswer(question.id)));
    });
}

function getAnswer(questionId) {
    const selected = examForm.querySelector(`input[name="q-${questionId}"]:checked`);
    return selected ? selected.value : '';
}

async function handleExamSubmit(event) {
    event.preventDefault();
    clearStatus(examStatus);

    const unansweredQuestion = state.examQuestions.find((question) => !getAnswer(question.id));
    if (unansweredQuestion) {
        const questionPosition = state.examQuestions.findIndex((question) => question.id === unansweredQuestion.id) + 1;
        showStatus(examStatus, `A questão ${questionPosition} ainda não foi respondida.`, 'warning');
        document.querySelector(`[data-question-card="${unansweredQuestion.id}"]`).scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }

    const answers = state.examQuestions.map((question, index) => {
        const answer = getAnswer(question.id);
        return {
            numeroExibido: index + 1,
            numeroOriginal: question.originalNumber,
            par: question.pairIndex,
            respostaMarcada: answer,
            respostaCorreta: question.correct ? 'C' : 'E',
            acertou: answer === (question.correct ? 'C' : 'E'),
            tema: question.theme,
            enunciado: question.text
        };
    });

    const correctIndividuals = answers.filter((answer) => answer.acertou).length;
    const correctPairs = state.questionPairs.filter((pair) => {
        return pair.questions.every((question) => getAnswer(question.id) === (question.correct ? 'C' : 'E'));
    }).length;

    const score = Number(((correctPairs / TOTAL_PAIRS) * 10).toFixed(1));

    state.result = {
        score,
        correctPairs,
        correctIndividuals,
        answers,
        timestamp: new Date().toISOString()
    };

    fillResultScreen();
    showScreen('result');
    await sendResultToSheet();
}

function fillResultScreen() {
    document.getElementById('result-student').textContent = `${state.profile.nome} · ${state.profile.serie} ${state.profile.turma} · ${state.profile.bimestre} · ${state.profile.isRecovery ? 'Recuperação' : 'Prova regular'} · ${state.profile.trilha}`;
    document.getElementById('result-score').textContent = state.result.score.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    document.getElementById('result-pairs').textContent = `${state.result.correctPairs}/${TOTAL_PAIRS}`;
    document.getElementById('result-individual').textContent = `${state.result.correctIndividuals}/${TOTAL_QUESTIONS}`;
    clearStatus(resultStatus);
}

async function sendResultToSheet() {
    if (!APPS_SCRIPT_URL) {
        showStatus(resultStatus, 'A prova foi calculada localmente. Para gravar na planilha, informe a URL do Apps Script no arquivo app.js.', 'warning');
        return;
    }

    const payload = {
        avaliacao: APP_CONFIG.evaluationName,
        atividade: APP_CONFIG.activityName,
        categoria: APP_CONFIG.category,
        timestamp: state.result.timestamp,
        serie: state.profile.serie,
        turma: state.profile.turma,
        bimestre: state.profile.bimestre,
        recuperacao: state.profile.isRecovery,
        trilha: state.profile.trilha,
        estudante: state.profile.nome,
        estudanteDigitado: state.profile.nomeManual,
        email: state.profile.email,
        sheetName: state.profile.sheetName,
        scoreHeader: state.profile.scoreHeader,
        totalQuestoes: TOTAL_QUESTIONS,
        totalPares: TOTAL_PAIRS,
        acertosIndividuais: state.result.correctIndividuals,
        paresCorretos: state.result.correctPairs,
        nota: state.result.score,
        respostas: state.result.answers
    };

    const targetSheetLabel = state.profile.sheetName || `${normalizeSerieForSheet(state.profile.serie)} ${state.profile.turma}`;
    showStatus(resultStatus, `Enviando resultado para a aba ${targetSheetLabel}, coluna ${state.profile.scoreHeader}...`, 'info');

    try {
        await postJsonNoCors(APPS_SCRIPT_URL, payload);
        showStatus(resultStatus, `Envio disparado para a aba ${targetSheetLabel}, coluna ${state.profile.scoreHeader}. ${state.profile.email ? 'Tambem foi solicitada a confirmação por email.' : 'Sem email de confirmação, porque nenhum email foi informado.'}`, 'success');
    } catch (error) {
        showStatus(resultStatus, `A nota foi calculada, mas o envio falhou: ${error.message}`, 'error');
    }
}

function restartApplication() {
    introForm.reset();
    examForm.reset();
    state.profile = null;
    state.result = null;
    resetExamOrder();
    renderQuestionCards();
    populateStudentOptions();
    updateProgress();
    clearStatus(introStatus);
    clearStatus(examStatus);
    clearStatus(resultStatus);
    studentSummary.innerHTML = '';
    manualNameField.classList.add('hidden');
    showScreen('intro');
}

function showScreen(screenName) {
    introScreen.classList.toggle('active', screenName === 'intro');
    examScreen.classList.toggle('active', screenName === 'exam');
    resultScreen.classList.toggle('active', screenName === 'result');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status show ${type}`;
}

function clearStatus(element) {
    element.textContent = '';
    element.className = 'status';
}

function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function shuffleQuestions(items) {
    let shuffled = [...items];

    for (let attempt = 0; attempt < 40; attempt += 1) {
        shuffled = shuffleArray(shuffled);
        if (!hasAdjacentPair(shuffled)) {
            return shuffled;
        }
    }

    for (let index = 1; index < shuffled.length; index += 1) {
        if (shuffled[index].pairIndex === shuffled[index - 1].pairIndex) {
            const swapIndex = shuffled.findIndex((candidate, candidateIndex) => {
                if (candidateIndex <= index) {
                    return false;
                }

                const previousPair = shuffled[index - 1].pairIndex;
                const nextPair = shuffled[candidateIndex + 1] ? shuffled[candidateIndex + 1].pairIndex : null;
                return candidate.pairIndex !== previousPair && candidate.pairIndex !== nextPair;
            });

            if (swapIndex > -1) {
                [shuffled[index], shuffled[swapIndex]] = [shuffled[swapIndex], shuffled[index]];
            }
        }
    }

    return shuffled;
}

function hasAdjacentPair(items) {
    for (let index = 1; index < items.length; index += 1) {
        if (items[index].pairIndex === items[index - 1].pairIndex) {
            return true;
        }
    }

    return false;
}

function shuffleArray(items) {
    const shuffled = [...items];

    for (let currentIndex = shuffled.length - 1; currentIndex > 0; currentIndex -= 1) {
        const randomIndex = Math.floor(Math.random() * (currentIndex + 1));
        [shuffled[currentIndex], shuffled[randomIndex]] = [shuffled[randomIndex], shuffled[currentIndex]];
    }

    return shuffled;
}