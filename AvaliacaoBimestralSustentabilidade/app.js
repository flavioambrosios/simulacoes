const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbye5ZFZ95mUfkdUD_iZvFEvHUPww7-t_dKZQaDtvC72PqJhJtdPLs3FHeNFG6SfztXlVQ/exec';

const QUESTION_PAIRS = [
    {
        theme: 'Oceanos + clima',
        left: 'Os oceanos absorvem parte do calor e do dióxido de carbono da atmosfera, ajudando a regular o clima do planeta.',
        right: 'Os oceanos não têm papel relevante na regulação do clima do planeta.'
    },
    {
        theme: 'Oceanos + correntes marinhas',
        left: 'As correntes marinhas redistribuem calor e influenciam o clima de várias regiões do mundo.',
        right: 'As correntes marinhas não influenciam o clima das regiões costeiras nem do interior dos continentes.'
    },
    {
        theme: 'Oceanos + fitoplâncton',
        left: 'O fitoplâncton marinho participa das cadeias alimentares oceânicas e contribui para a produção de oxigênio.',
        right: 'O fitoplâncton não participa das cadeias alimentares oceânicas nem tem relação com a produção de oxigênio.'
    },
    {
        theme: 'Oceanos + acidificação',
        left: 'O excesso de dióxido de carbono dissolvido nos oceanos pode aumentar a acidificação da água e prejudicar corais e organismos com concha.',
        right: 'O excesso de dióxido de carbono dissolvido nos oceanos não altera a água nem afeta corais ou organismos com concha.'
    },
    {
        theme: 'Oceanos + manguezais',
        left: 'Manguezais ajudam a proteger o litoral, servem de berçário para muitas espécies e filtram parte dos sedimentos que chegam ao mar.',
        right: 'Manguezais não têm importância ecológica nem relação com a proteção do litoral e da vida marinha.'
    },
    {
        theme: 'Oceanos + poluição plástica',
        left: 'O descarte inadequado de plástico pode atingir os oceanos, afetar animais marinhos e entrar nas cadeias alimentares.',
        right: 'O descarte inadequado de plástico não chega aos oceanos e não afeta os seres vivos marinhos.'
    },
    {
        theme: 'Oceanos + pesca',
        left: 'A sobrepesca pode reduzir estoques pesqueiros e desequilibrar ecossistemas marinhos.',
        right: 'A sobrepesca não altera estoques pesqueiros nem o equilíbrio dos ecossistemas marinhos.'
    },
    {
        theme: 'Oceanos + aquecimento global',
        left: 'O aquecimento das águas pode favorecer o branqueamento de corais e alterar habitats marinhos.',
        right: 'O aquecimento das águas não altera habitats marinhos nem tem relação com o branqueamento de corais.'
    },
    {
        theme: 'Petróleo + origem',
        left: 'O petróleo é um combustível fóssil formado a partir de matéria orgânica acumulada e transformada ao longo de milhões de anos.',
        right: 'O petróleo é uma fonte renovável que se recompõe rapidamente em poucos anos.'
    },
    {
        theme: 'Petróleo + disponibilidade',
        left: 'Por ser um recurso não renovável na escala de tempo humana, o petróleo pode se tornar mais escasso com o uso contínuo.',
        right: 'Como o petróleo é inesgotável na escala humana, seu uso contínuo não afeta a disponibilidade futura.'
    },
    {
        theme: 'Petróleo + derivados',
        left: 'Do petróleo derivam produtos como gasolina, diesel, querosene, asfalto e parte dos plásticos.',
        right: 'O petróleo serve apenas para produzir gasolina e não origina outros materiais de uso cotidiano.'
    },
    {
        theme: 'Petróleo + derramamentos',
        left: 'Derramamentos de petróleo podem contaminar águas, praias e organismos vivos, gerando impactos econômicos e ambientais.',
        right: 'Derramamentos de petróleo não causam contaminação relevante porque o óleo desaparece sem efeitos ambientais.'
    },
    {
        theme: 'Petróleo + emissões',
        left: 'A queima de derivados do petróleo libera gases de efeito estufa e poluentes atmosféricos.',
        right: 'A queima de derivados do petróleo não libera gases de efeito estufa nem poluentes atmosféricos.'
    },
    {
        theme: 'Petróleo + pré-sal',
        left: 'No Brasil, parte importante da produção de petróleo está associada a áreas do pré-sal, localizadas em grandes profundidades.',
        right: 'O pré-sal brasileiro está em áreas rasas e superficiais, sem desafios tecnológicos relevantes.'
    },
    {
        theme: 'Petróleo + geopolítica',
        left: 'A dependência do petróleo pode aumentar vulnerabilidades econômicas e geopolíticas em países importadores.',
        right: 'A dependência do petróleo não tem relação com economia nem com disputas geopolíticas.'
    },
    {
        theme: 'Petróleo + transição energética',
        left: 'A transição energética busca reduzir a dependência de combustíveis fósseis sem ignorar os impactos sociais e econômicos dessa mudança.',
        right: 'A transição energética significa apenas trocar uma fonte por outra sem qualquer impacto social ou econômico.'
    },
    {
        theme: 'Produção de alimentos + Brasil',
        left: 'O Brasil se destaca na produção de alimentos e commodities agrícolas como soja, milho, café, carnes e cana-de-açúcar.',
        right: 'O Brasil não tem relevância na produção agrícola e não se destaca em alimentos ou commodities.'
    },
    {
        theme: 'Produção de alimentos + fome',
        left: 'A existência de alta produção de alimentos no mundo não elimina automaticamente a fome, porque acesso, renda e distribuição também importam.',
        right: 'Se o mundo produz muitos alimentos, a fome desaparece automaticamente sem depender de acesso, renda ou distribuição.'
    },
    {
        theme: 'Produção de alimentos + agricultura familiar',
        left: 'A agricultura familiar tem papel importante no abastecimento alimentar e na diversidade de produtos consumidos no Brasil.',
        right: 'A agricultura familiar não tem importância no abastecimento alimentar nem na diversidade de produtos consumidos no Brasil.'
    },
    {
        theme: 'Produção de alimentos + solo',
        left: 'Práticas agrícolas mesmo sem manejo adequado podem aumentar erosão, compactação e perda de fertilidade do solo.',
        right: 'Práticas agrícolas sem manejo adequado sempre melhoram a fertilidade do solo e reduzem erosão.'
    },
    {
        theme: 'Produção de alimentos + irrigação',
        left: 'A irrigação pode elevar a produtividade agrícola, mas exige planejamento para evitar desperdício de água e salinização do solo.',
        right: 'A irrigação nunca causa desperdício de água nem problemas no solo, por isso dispensa planejamento.'
    },
    {
        theme: 'Produção de alimentos + agroecologia',
        left: 'Práticas agroecológicas podem contribuir para conservar o solo, a água e a biodiversidade em sistemas de produção de alimentos.',
        right: 'Práticas agroecológicas não contribuem para conservar solo, água ou biodiversidade.'
    },
    {
        theme: 'Produção de alimentos + desperdício',
        left: 'Perdas e desperdícios ao longo da cadeia produtiva reduzem a eficiência do sistema alimentar e ampliam impactos ambientais.',
        right: 'Perdas e desperdícios de alimentos não interferem na eficiência do sistema alimentar nem nos impactos ambientais.'
    },
    {
        theme: 'Produção de alimentos + clima',
        left: 'Eventos climáticos extremos podem reduzir safras, encarecer alimentos e comprometer a segurança alimentar.',
        right: 'Eventos climáticos extremos não afetam safras, preços nem segurança alimentar.'
    },
    {
        theme: 'Recursos minerais + Brasil',
        left: 'O Brasil possui destaque em recursos como minério de ferro, bauxita, manganês e nióbio.',
        right: 'O Brasil não possui destaque relevante em recursos minerais como ferro, bauxita, manganês ou nióbio.'
    },
    {
        theme: 'Recursos minerais + indústria',
        left: 'Recursos minerais são matérias-primas importantes para a construção civil, a indústria e várias tecnologias.',
        right: 'Recursos minerais não são importantes para a indústria nem para tecnologias do cotidiano.'
    },
    {
        theme: 'Recursos minerais + distribuição mundial',
        left: 'A distribuição desigual de recursos minerais no mundo influencia comércio, dependência econômica e disputas estratégicas.',
        right: 'A distribuição de recursos minerais no mundo não interfere em comércio, dependência econômica ou disputas estratégicas.'
    },
    {
        theme: 'Recursos minerais + impactos ambientais',
        left: 'A mineração pode causar desmatamento, poeira, alteração da paisagem e riscos de contaminação, exigindo controle ambiental.',
        right: 'A mineração não gera impactos ambientais significativos e dispensa controle ambiental.'
    },
    {
        theme: 'Recursos minerais + garimpo ilegal',
        left: 'O garimpo ilegal pode provocar desmatamento, conflitos sociais e contaminação de rios por mercúrio.',
        right: 'O garimpo ilegal não causa desmatamento, conflitos sociais nem contaminação de rios.'
    },
    {
        theme: 'Recursos minerais + beneficiamento',
        left: 'Beneficiar e transformar minérios pode agregar valor econômico mesmo antes da exportação, gerando empregos qualificados e fortalecendo a balança comercial do país.',
        right: 'Beneficiar e transformar minérios não altera o valor econômico da produção mineral.'
    },
    {
        theme: 'Recursos minerais + finitude',
        left: 'As reservas minerais são finitas e não se renovam na escala de tempo humana.',
        right: 'As reservas minerais se renovam rapidamente, por isso podem ser exploradas sem preocupação com limites.'
    },
    {
        theme: 'Recursos minerais + transição energética',
        left: 'A transição energética tende a ampliar a demanda por minerais como cobre, lítio, níquel e terras raras.',
        right: 'A transição energética reduz a importância de minerais como cobre, lítio, níquel e terras raras.'
    },
    {
        theme: 'Água + disponibilidade',
        left: 'A maior parte da água do planeta é salgada, e apenas uma pequena fração da água doce está facilmente disponível para uso humano.',
        right: 'A maior parte da água do planeta é doce e está facilmente disponível para uso humano.'
    },
    {
        theme: 'Água + bacias hidrográficas',
        left: 'As bacias hidrográficas estruturam o escoamento da água sobre a superfície terrestre e orientam sua distribuição na paisagem.',
        right: 'As bacias hidrográficas não estruturam o escoamento da água sobre a superfície terrestre e nem orientam sua distribuição na paisagem.'
    },
    {
        theme: 'Água + mata ciliar',
        left: 'A vegetação nas margens dos rios ajuda a reduzir erosão, assoreamento e perda de qualidade da água.',
        right: 'A vegetação nas margens dos rios não interfere na erosão, no assoreamento nem na qualidade da água.'
    },
    {
        theme: 'Água + saneamento',
        left: 'O saneamento básico reduz doenças de veiculação hídrica e melhora a qualidade ambiental.',
        right: 'O saneamento básico não interfere em doenças de veiculação hídrica nem na qualidade ambiental.'
    },
    {
        theme: 'Água + aquíferos',
        left: 'Aquíferos subterrâneos podem ser contaminados por esgoto, resíduos e produtos químicos infiltrados no solo.',
        right: 'Aquíferos subterrâneos são imunes à contaminação por esgoto, resíduos e produtos químicos.'
    },
    {
        theme: 'Água + consumo consciente',
        left: 'Tratar a água não significa que ela seja infinita; uso consciente continua sendo necessário.',
        right: 'Se a água pode ser tratada, ela se torna infinita e dispensa consumo consciente.'
    },
    {
        theme: 'Água + reuso',
        left: 'Reuso de água e captação da chuva podem ajudar a reduzir pressão sobre mananciais em várias atividades.',
        right: 'Reuso de água e captação da chuva não ajudam a reduzir pressão sobre mananciais.'
    },
    {
        theme: 'Água + poluição',
        left: 'Esgoto sem tratamento, agrotóxicos e efluentes industriais podem comprometer a qualidade da água.',
        right: 'Esgoto sem tratamento, agrotóxicos e efluentes industriais não comprometem a qualidade da água.'
    },
    {
        theme: 'Amazônia + dimensão ecológica',
        left: 'A Amazônia abriga grande biodiversidade e tem papel importante no equilíbrio climático regional e global.',
        right: 'A Amazônia tem pouca biodiversidade e não interfere no equilíbrio climático regional ou global.'
    },
    {
        theme: 'Amazônia + biodiversidade',
        left: 'A diversidade de espécies da Amazônia inclui plantas, animais, fungos e micro-organismos ainda não totalmente conhecidos pela ciência.',
        right: 'A biodiversidade amazônica já é totalmente conhecida e se limita a poucas espécies de plantas e animais.'
    },
    {
        theme: 'Amazônia + rios voadores',
        left: 'A evapotranspiração da Amazônia contribui para a formação dos chamados rios voadores, que influenciam chuvas em outras regiões.',
        right: 'A evapotranspiração da Amazônia não interfere nas chuvas de outras regiões do Brasil ou da América do Sul.'
    },
    {
        theme: 'Amazônia + desmatamento',
        left: 'O desmatamento da Amazônia reduz habitats, libera carbono e afeta o ciclo da água.',
        right: 'O desmatamento da Amazônia não reduz habitats, não libera carbono e não afeta o ciclo da água.'
    },
    {
        theme: 'Amazônia + queimadas',
        left: 'Queimadas na Amazônia podem degradar o solo, afetar a fauna, emitir gases e agravar problemas respiratórios.',
        right: 'Queimadas na Amazônia não degradam o solo, não afetam a fauna e não pioram a qualidade do ar.'
    },
    {
        theme: 'Amazônia + povos indígenas',
        left: 'Povos indígenas e comunidades tradicionais têm papel importante na proteção de territórios e saberes associados à floresta.',
        right: 'Povos indígenas e comunidades tradicionais não têm relação com a proteção da floresta nem com saberes ambientais.'
    },
    {
        theme: 'Amazônia + garimpo e madeira ilegal',
        left: 'Garimpo ilegal e extração ilegal de madeira podem causar conflitos, contaminação e perda de biodiversidade na Amazônia.',
        right: 'Garimpo ilegal e extração ilegal de madeira não causam conflitos, contaminação ou perda de biodiversidade na Amazônia.'
    },
    {
        theme: 'Amazônia + bioeconomia',
        left: 'Atividades econômicas sustentáveis com a floresta em pé podem gerar renda e favorecer conservação em parte da Amazônia.',
        right: 'Só é possível gerar renda na Amazônia destruindo a floresta e substituindo-a completamente por outras atividades.'
    },
    {
        theme: 'Amazônia + população',
        left: 'A Amazônia não é um espaço vazio e homogêneo: nela vivem populações urbanas, rurais, ribeirinhas, indígenas e outros grupos sociais.',
        right: 'A Amazônia é um espaço vazio e homogêneo, sem diversidade de grupos sociais e modos de vida.'
    },
    {
        theme: 'Amazônia + impactos nacionais',
        left: 'Alterações ambientais na Amazônia podem afetar chuvas, agricultura e disponibilidade hídrica em outras regiões do Brasil.',
        right: 'Alterações ambientais na Amazônia ficam restritas à própria floresta e não afetam outras regiões do Brasil.'
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
    evaluationName: 'Avaliação Bimestral - Sustentabilidade',
    activityName: 'Avaliação Bimestral - Sustentabilidade',
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

function normalizeTermKey(termLabel) {
    const normalized = String(termLabel || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/bimestre/g, '')
        .trim();

    if (normalized.startsWith('1')) return '1o';
    if (normalized.startsWith('2')) return '2o';
    if (normalized.startsWith('3')) return '3o';
    if (normalized.startsWith('4')) return '4o';
    return normalized;
}

function getTermColumn(termLabel) {
    const termKey = normalizeTermKey(termLabel);
    const termColumns = {
        '1o': 'J',
        '2o': 'N',
        '3o': 'R',
        '4o': 'V'
    };

    return termColumns[termKey] || '';
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
        { text: state.profile.nome, className: 'name-pill' },
        { text: `Série: ${state.profile.serie}`, className: 'detail-pill' },
        { text: `Turma: ${state.profile.turma}`, className: 'detail-pill' },
        { text: `Bimestre: ${state.profile.bimestre}`, className: 'detail-pill' },
        { text: `Tipo: ${state.profile.isRecovery ? 'Recuperação' : 'Prova regular'}`, className: 'detail-pill' },
        { text: `Trilha: ${state.profile.trilha}`, className: 'detail-pill' }
    ];

    if (state.profile.sheetName) {
        items.push({ text: `Base: ${state.profile.sheetName}`, className: 'detail-pill' });
    }

    if (state.profile.email) {
        items.push({ text: `Email: ${state.profile.email}`, className: 'detail-pill' });
    }

    studentSummary.innerHTML = items
        .map((item) => `<span class="summary-pill ${item.className}">${escapeHtml(item.text)}</span>`)
        .join('');
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

    const targetColumn = getTermColumn(state.profile.bimestre);
    const payload = {
        avaliacao: APP_CONFIG.evaluationName,
        atividade: APP_CONFIG.activityName,
        categoria: APP_CONFIG.category,
        timestamp: state.result.timestamp,
        serie: state.profile.serie,
        turma: state.profile.turma,
        bimestre: state.profile.bimestre,
        coluna: targetColumn,
        colunaBimestre: targetColumn,
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
    showStatus(resultStatus, `Enviando resultado para a aba ${targetSheetLabel}, coluna ${targetColumn || state.profile.scoreHeader}...`, 'info');

    try {
        await postJsonNoCors(APPS_SCRIPT_URL, payload);
        showStatus(resultStatus, `Envio disparado para a aba ${targetSheetLabel}, coluna ${targetColumn || state.profile.scoreHeader}. ${state.profile.email ? 'Tambem foi solicitada a confirmação por email.' : 'Sem email de confirmação, porque nenhum email foi informado.'}`, 'success');
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