(function () {
    'use strict';

    if (window.__simulationEnhancerLoaded) {
        return;
    }
    window.__simulationEnhancerLoaded = true;

    const PRIMARY_GRADEBOOK_URL = 'https://script.google.com/macros/s/AKfycbye5ZFZ95mUfkdUD_iZvFEvHUPww7-t_dKZQaDtvC72PqJhJtdPLs3FHeNFG6SfztXlVQ/exec';
    const LEGACY_BACKUP_URL = 'https://script.google.com/macros/s/AKfycbxX6bygZyd5PwiPXZtLz4GfpqatnFT_ZRGSPPcQYSxrc2cWqD8YyX-ic4oOTG1QvRzX/exec';
    const TERM_GRADEBOOK_URL = 'https://script.google.com/macros/s/AKfycbye5ZFZ95mUfkdUD_iZvFEvHUPww7-t_dKZQaDtvC72PqJhJtdPLs3FHeNFG6SfztXlVQ/exec';
    const EMAIL_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbyVQeiZ9lxSy86Lp-85VlJWRXamY2uc_-s9dCo472uLkeg_ezHeGdQPjl4HAH7Uonfi/exec';
    const TEACHER_EMAIL = 'flavio.ambrosio@edu.se.df.gov.br';
    const TERM_COLUMN_MAP = {
        '1o': 'J',
        '2o': 'N',
        '3o': 'R',
        '4o': 'V',
        '1o bimestre': 'J',
        '2o bimestre': 'N',
        '3o bimestre': 'R',
        '4o bimestre': 'V'
    };
    const TRAIL_OPTIONS = [
        'PCA - Educa��o Digital 3o ano A',
        'PCA - Educa��o Digital 3o ano B',
        'Sustentabilidade 2o ano C',
        'Outra',
        'Nenhuma (Turma de Fisica)'
    ];
    const DEFAULT_DATABASE = {
        bySheet: {},
        bySerieTurma: {},
        byTrilha: {},
        accessControl: {}
    };
    const DEFAULT_STUDENT_ACCESS_CONFIG = {
        enabled: true,
        salt: 'EDU-DIGITAL-2026',
        passwordHash: '0e71f1560760cf5cc90d84c76c5028354b4d2366d8841144d34b1fa4b6dacb60',
        acceptedPasswordHashes: [
            '0e71f1560760cf5cc90d84c76c5028354b4d2366d8841144d34b1fa4b6dacb60',
            'f267aa257c7116e591f638a9bb704f8c11940f3798b59f7a8f1f6a55d0877be1'
        ],
        apiAccessToken: 'f267aa257c7116e591f638a9bb704f8c11940f3798b59f7a8f1f6a55d0877be1',
        rememberStudentAccess: false,
        hint: 'Solicite ao professor a senha de acesso do estudante.',
        rosterApiUrl: 'https://script.google.com/macros/s/AKfycbye5ZFZ95mUfkdUD_iZvFEvHUPww7-t_dKZQaDtvC72PqJhJtdPLs3FHeNFG6SfztXlVQ/exec',
        apiTimeoutMs: 20000,
        rosterCacheTtlMs: 15000
    };
    const STUDENT_ACCESS_SESSION_KEY = 'simulationEnhancer:student-access-auth';
    const STUDENT_ACCESS_TOKEN_SESSION_KEY = 'simulationEnhancer:student-access-token';
    const SCORE_WEIGHTS = {
        exercises: 0.5,
        conclusion: 0.5
    };
    const STOPWORDS = new Set([
        'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'ate', 'com', 'como',
        'da', 'das', 'de', 'dela', 'dele', 'deles', 'demais', 'depois', 'do', 'dos', 'e', 'ela', 'elas',
        'ele', 'eles', 'em', 'entre', 'era', 'eram', 'essa', 'essas', 'esse', 'esses', 'esta', 'estao',
        'estas', 'estava', 'este', 'estes', 'eu', 'foi', 'foram', 'ha', 'isso', 'isto', 'ja', 'la', 'lhe',
        'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu', 'minha', 'muito', 'na', 'nao', 'nas', 'nem', 'no',
        'nos', 'nossa', 'nosso', 'num', 'numa', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos',
        'por', 'porque', 'quando', 'que', 'quem', 'se', 'sem', 'ser', 'seu', 'sua', 'suas', 'tambem', 'tem',
        'ter', 'teu', 'tua', 'um', 'uma', 'voces'
    ]);
    const LEARNING_SIGNAL_TERMS = [
        'aprendi', 'observei', 'percebi', 'conclui', 'compreendi', 'entendi', 'relacionei', 'comparei',
        'analisei', 'investiguei', 'calculei', 'identifiquei', 'verifiquei', 'expliquei'
    ];
    const CONNECTOR_TERMS = [
        'porque', 'portanto', 'assim', 'logo', 'entao', 'dessa forma', 'por isso', 'alem disso', 'ou seja'
    ];

    const config = Object.assign({
        simulationName: '',
        storageKey: '',
        termOptions: ['1o', '2o', '3o', '4o']
    }, window.SIMULATION_ENHANCER_CONFIG || {});

    const simulationName = config.simulationName || getSimulationName();
    const normalizedSimulationKey = slugify(config.storageKey || simulationName || document.title || 'simulacao');
    const EXERCISE_STORAGE_KEY = 'simulationEnhancer:' + normalizedSimulationKey + ':exercise-state';
    const AUDIO_STORAGE_KEY = 'simulationEnhancer:' + normalizedSimulationKey + ':voice';
    const AI_STORAGE_KEY = 'simulationEnhancer:' + normalizedSimulationKey + ':ai-analysis';

    let narrationTracks = [];
    let narrationIndex = 0;
    let speaking = false;
    let audioPaused = false;
    let activeAudioMode = null;
    let activeExampleButton = null;
    let selectedVoice = null;
    let activeUtterance = null;
    let speechRequestToken = 0;
    let lastAiAnalysis = null;
    let studentDatabaseLoadPromise = null;
    let studentAccessConfigLoadPromise = null;
    let studentOptionsRequestToken = 0;
    let rosterApiCache = {};
    let rosterSheetsCache = null;
    let saveIndicatorHideTimer = null;
    let lastSaveIndicatorAt = 0;

    injectStyles();
    ensureSaveIndicator();
    ensureEnhancedFormFields();
    ensureExerciseHeaderTools();
    setupAudioControls();
    setupSolvedExerciseAudio();
    setupAudioLifecycleGuards();
    setupExercisePersistence();
    setupConclusionPreview();
    setupDelegatedSendHandler();

    function getSimulationName() {
        const heading = document.querySelector('h1');
        return heading ? heading.textContent.trim() : document.title.trim();
    }

    function slugify(text) {
        return String(text || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '') || 'simulacao';
    }

    function normalizeText(text) {
        return String(text || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    }

    function clamp(value, min, max) {
        return Math.min(max, Math.max(min, value));
    }

    function readGlobalBinding(name) {
        try {
            return window.eval(name);
        } catch (error) {
            return undefined;
        }
    }

    function writeGlobalBinding(name, value) {
        try {
            window.__simulationEnhancerTempValue = value;
            window.eval(name + ' = window.__simulationEnhancerTempValue');
        } catch (error) {
            return;
        } finally {
            try {
                delete window.__simulationEnhancerTempValue;
            } catch (cleanupError) {
                window.__simulationEnhancerTempValue = undefined;
            }
        }
    }

    function injectStyles() {
        if (document.getElementById('simulation-enhancer-styles')) {
            return;
        }

        const style = document.createElement('style');
        style.id = 'simulation-enhancer-styles';
        style.textContent = [
            '.enhancer-audio-controls { position: static !important; top: auto !important; right: auto !important; bottom: auto !important; left: auto !important; z-index: auto !important; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: center; margin-top: 18px; padding: 14px; border-radius: 10px; background: rgba(0, 0, 0, 0.45); border: 1px solid rgba(255, 204, 0, 0.25); }',
            '.enhancer-audio-controls button, .enhancer-audio-controls select { width: auto; margin: 0; }',
            '.enhancer-track-counter { color: #ffdd88; font-size: 0.95rem; font-weight: 700; }',
            '.enhancer-voice-group { display: flex; align-items: center; gap: 8px; color: #fff; }',
            '.enhancer-voice-group label { margin: 0; white-space: nowrap; }',
            '.enhancer-voice-group select { min-width: 210px; }',
            '.enhancer-ai-card { margin-top: 14px; padding: 14px; border-radius: 10px; background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 204, 0, 0.25); }',
            '.enhancer-ai-card h4 { margin: 0 0 8px; color: #ffcc00; text-align: center; }',
            '.enhancer-ai-score { display: grid; gap: 6px; margin-top: 8px; font-size: 0.94rem; }',
            '.enhancer-inline-note { margin-top: 8px; color: #ffdd88; font-size: 0.92rem; text-align: center; }',
            '.enhancer-badge { display: none; padding: 6px 10px; border-radius: 999px; background: rgba(0, 255, 170, 0.16); border: 1px solid rgba(0, 255, 170, 0.4); color: #a8ffe1; font-size: 0.82rem; }',
            '.enhancer-example-audio-btn { margin-top: 10px; padding: 10px 14px; border: none; border-radius: 10px; background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); color: #fff; font-size: 0.95rem; font-weight: 700; cursor: pointer; transition: transform 0.18s ease, box-shadow 0.18s ease; }',
            '.enhancer-example-audio-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(245, 124, 0, 0.28); }',
            '.enhancer-example-audio-btn.is-playing { background: linear-gradient(135deg, #ef6c00 0%, #e65100 100%); }',
            '.enhancer-correct-answer { margin-top: 10px; padding: 10px 12px; border-radius: 10px; background: rgba(36, 94, 52, 0.28); border: 1px solid rgba(144, 238, 144, 0.35); color: #e8ffe8; font-weight: 700; }',
            '.enhancer-modal-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }',
            '.enhancer-restart-btn { width: auto; margin: 0; padding: 8px 12px; background: #1a2a6c; color: #fff; }',
            '.enhancer-restart-btn:hover { background: #273b93; }',
            '.enhancer-save-indicator { position: fixed; right: 18px; bottom: 18px; z-index: 3000; max-width: 260px; padding: 10px 14px; border-radius: 12px; background: rgba(12, 22, 32, 0.92); border: 1px solid rgba(120, 255, 190, 0.5); color: #d9ffee; font-size: 0.92rem; font-weight: 700; box-shadow: 0 10px 24px rgba(0, 0, 0, 0.28); opacity: 0; transform: translateY(10px); pointer-events: none; transition: opacity 0.18s ease, transform 0.18s ease; }',
            '.enhancer-save-indicator.is-visible { opacity: 1; transform: translateY(0); }',
            '.enhancer-save-indicator strong { color: #7fffc0; }',
            '.enhancer-visitor-checkbox { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; padding: 10px; border-radius: 8px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 204, 0, 0.15); cursor: pointer; }',
            '.enhancer-student-auth { margin-bottom: 10px; padding: 10px; border-radius: 8px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(100, 181, 246, 0.25); }',
            '.enhancer-student-auth-btn { width: auto; margin: 0 0 8px; background: #1976d2; color: #fff; }',
            '.enhancer-student-auth-panel { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }',
            '.enhancer-student-auth-panel input { margin: 0; }',
            '.enhancer-student-auth-status { margin-top: 6px; }',
            '.email-status.warning-status { background: rgba(255, 193, 7, 0.15); border-left: 4px solid #ffc107; color: #fff3cd; }',
                        '.enhancer-visitor-checkbox input { width: auto; margin: 0; cursor: pointer; }',
                        '.enhancer-visitor-checkbox label { margin: 0; cursor: pointer; font-size: 0.95rem; color: #ffdd88; }',
                        '.enhancer-visitor-fields { display: block; }',
                        '.enhancer-visitor-fields.enhancer-hidden { display: none !important; }',
                        '.enhancer-hidden { display: none !important; }',
                        '.enhancer-hidden-legacy-audio { display: none !important; }',
            '@media (max-width: 768px) { .enhancer-audio-controls { flex-direction: column; align-items: stretch; } .enhancer-audio-controls button, .enhancer-audio-controls select { width: 100%; } .enhancer-voice-group { width: 100%; flex-direction: column; align-items: stretch; } .enhancer-save-indicator { left: 12px; right: 12px; bottom: 12px; max-width: none; } }'
        ].join('');
        document.head.appendChild(style);
    }

    function ensureSaveIndicator() {
        if (document.getElementById('enhancerSaveIndicator')) {
            return;
        }

        const indicator = document.createElement('div');
        indicator.id = 'enhancerSaveIndicator';
        indicator.className = 'enhancer-save-indicator';
        indicator.setAttribute('aria-live', 'polite');
        indicator.innerHTML = '<strong>Progresso salvo</strong><div>O ponto atual dos exercicios foi guardado.</div>';
        document.body.appendChild(indicator);
    }

    function flashSaveIndicator() {
        const indicator = document.getElementById('enhancerSaveIndicator');
        const now = Date.now();
        if (!indicator) {
            return;
        }

        if (now - lastSaveIndicatorAt < 900 && indicator.classList.contains('is-visible')) {
            window.clearTimeout(saveIndicatorHideTimer);
            saveIndicatorHideTimer = window.setTimeout(function () {
                indicator.classList.remove('is-visible');
            }, 1400);
            return;
        }

        lastSaveIndicatorAt = now;
        indicator.classList.add('is-visible');
        window.clearTimeout(saveIndicatorHideTimer);
        saveIndicatorHideTimer = window.setTimeout(function () {
            indicator.classList.remove('is-visible');
        }, 1400);
    }

    function ensureEnhancedFormFields() {
        const emailForm = document.querySelector('#resultsContainer .email-form');
        if (!emailForm) {
            return;
        }

        const currentValues = {
            studentSheet: getFieldValue('studentSheet'),
            studentTrail: getFieldValue('studentTrail'),
            studentGrade: getFieldValue('studentGrade'),
            studentClass: getFieldValue('studentClass'),
            studentName: getFieldValue('studentName'),
            studentNameSelect: getFieldValue('studentNameSelect'),
            studentNameManual: getFieldValue('studentNameManual') || getFieldValue('studentName'),
            studentEmail: getFieldValue('studentEmail'),
            visitorName: getFieldValue('visitorName'),
            visitorEmail: getFieldValue('visitorEmail'),
            visitorMode: getCheckboxValue('visitorMode'),
            schoolTerm: getFieldValue('schoolTerm'),
            criticismInput: getFieldValue('criticismInput'),
            suggestionInput: getFieldValue('suggestionInput'),
            finalConclusion: getFieldValue('finalConclusion')
        };

        emailForm.innerHTML = [
                    '<div class="form-row enhancer-visitor-checkbox">',
                                '<div class="form-row enhancer-student-auth">',
                                '<button type="button" id="unlockStudentModeBtn" class="enhancer-student-auth-btn">Sou estudante (liberar por senha)</button>',
                                '<div id="studentAccessPanel" class="enhancer-student-auth-panel enhancer-hidden">',
                                '<input type="password" id="studentAccessPassword" placeholder="Digite a senha do estudante">',
                                '<button type="button" id="confirmStudentAccessBtn" class="check-btn">Liberar acesso</button>',
                                '</div>',
                                '<div id="enhancerStudentAccessStatus" class="enhancer-inline-note enhancer-student-auth-status">Modo visitante ativo por padrão.</div>',
                                '</div>',
                    '<div class="form-row enhancer-visitor-checkbox">',
                                '<input type="checkbox" id="visitorMode">',
                                '<label for="visitorMode">Sou visitante (não tenho série, turma ou trilha definida)</label>',
                                '</div>',
                                '<div id="studentFieldsArea" class="enhancer-visitor-fields">',
                    '<div class="form-row">',
                    '<label for="studentSheet" class="required">Turma / Aba da planilha:</label>',
                    '<select id="studentSheet" required>',
                    '<option value="">Selecione sua turma</option>',
                    '</select>',
                    '<input type="hidden" id="studentTrail">',
                    '<input type="hidden" id="studentGrade">',
                    '<input type="hidden" id="studentClass">',
                    '</div>',
                    '<div class="form-row">',
                    '<label for="studentNameSelect" class="required">Nome Completo:</label>',
                    '<select id="studentNameSelect" required><option value="">Selecione primeiro a turma</option></select>',
                    '<input type="hidden" id="studentName">',
                    '</div>',
                    '<div class="form-row enhancer-hidden" id="studentNameManualRow">',
                    '<label for="studentNameManual" class="required">Caso o nome não esteja na lista, escreva o nome completo:</label>',
                    '<input type="text" id="studentNameManual">',
                    '</div>',
                    '<div class="form-row">',
                    '<label for="studentEmail">E-mail para cópia:</label>',
                    '<input type="email" id="studentEmail" placeholder="seu@email.com">',
                    '</div>',
                    '<div class="form-row">',
                    '<label for="schoolTerm" class="required">Bimestre:</label>',
                    '<select id="schoolTerm" required>',
                    '<option value="">Selecione o bimestre</option>',
                    config.termOptions.map(function (term) {
                        return '<option value="' + escapeHtml(term) + '">' + escapeHtml(term.replace('o', 'º bimestre')) + '</option>';
                    }).join(''),
                    '</select>',
                    '</div>',
                    '</div>',
                    '<div id="visitorFieldsArea" class="enhancer-visitor-fields enhancer-hidden">',
                    '<div class="form-row">',
                    '<label for="visitorName" class="required">Nome do visitante:</label>',
                    '<input type="text" id="visitorName" placeholder="Digite seu nome completo">',
                    '</div>',
                    '<div class="form-row">',
                    '<label for="visitorEmail">E-mail do visitante (opcional):</label>',
                    '<input type="email" id="visitorEmail" placeholder="seu@email.com">',
                    '</div>',
                    '</div>',
                    '<div class="form-row">',
                    '<label for="criticismInput">Críticas:</label>',
                    '<textarea id="criticismInput" rows="3" placeholder="O que poderia ser melhorado na simulação e nos exercícios?"></textarea>',
                    '</div>',
                    '<div class="form-row">',
                    '<label for="suggestionInput">Sugestões:</label>',
                    '<textarea id="suggestionInput" rows="3" placeholder="Tem alguma sugestão para melhorar a experiência de aprendizado?"></textarea>',
                    '</div>',
                    '<div class="form-row">',
                    '<label for="finalConclusion" class="required">Conclusão sobre o exercício:</label>',
                    '<textarea id="finalConclusion" rows="4" required placeholder="Escreva aqui sua conclusão sobre a simulação e os exercícios..."></textarea>',
                    '</div>',
                    '<div id="emailStatus" class="email-status"></div>',
                    '<button id="sendResults" class="check-btn">Enviar Resultados</button>'
                ].join('');

        restoreFormState(currentValues);
        syncSelectedSheetMetadata();
        setupStudentFieldInteractions();
        setupVisitorModeToggle();
        bindFormPersistence();

        loadStudentDatabase()
            .then(function () {
                return loadStudentAccessConfigScript();
            })
            .finally(function () {
                setupStudentAccessGate();
                populateSimulationSheetOptions(currentValues.studentSheet || '');
                populateSimulationStudentOptions(currentValues.studentNameSelect || '');
            });
    }

    function setupVisitorModeToggle() {
            const visitorCheckbox = document.getElementById('visitorMode');
            const studentFieldsArea = document.getElementById('studentFieldsArea');
            const visitorFieldsArea = document.getElementById('visitorFieldsArea');
            const visitorName = document.getElementById('visitorName');
            if (!visitorCheckbox || !studentFieldsArea || !visitorFieldsArea) {
                return;
            }

            function toggleVisitorMode() {
                if (!visitorCheckbox.checked && !isStudentAccessAuthenticated()) {
                    visitorCheckbox.checked = true;
                    updateStudentAccessStatus('Para usar o modo estudante, informe a senha.', 'error');
                }
                const isVisitor = visitorCheckbox.checked;
                studentFieldsArea.classList.toggle('enhancer-hidden', isVisitor);
                visitorFieldsArea.classList.toggle('enhancer-hidden', !isVisitor);

                const requiredFields = studentFieldsArea.querySelectorAll('[required]');
                requiredFields.forEach(function (field) {
                    field.required = !isVisitor;
                    if (isVisitor) {
                        field.value = '';
                    }
                });

                if (visitorName) {
                    visitorName.required = isVisitor;
                }
                saveExerciseState();
            }

            visitorCheckbox.addEventListener('change', toggleVisitorMode);
            visitorCheckbox.dataset.enhancerBound = 'true';

            visitorCheckbox.checked = !isStudentAccessAuthenticated();
            toggleVisitorMode();
        }

    function getStudentAccessConfig() {
        const externalConfig = window.SIMULATION_ENHANCER_STUDENT_ACCESS
            || readGlobalBinding('SIMULATION_ENHANCER_STUDENT_ACCESS')
            || (getStudentSource() && getStudentSource().accessControl)
            || {};

        return Object.assign({}, DEFAULT_STUDENT_ACCESS_CONFIG, externalConfig || {});
    }

    function loadStudentAccessConfigScript() {
        const existingConfig = window.SIMULATION_ENHANCER_STUDENT_ACCESS || readGlobalBinding('SIMULATION_ENHANCER_STUDENT_ACCESS');
        if (existingConfig) {
            return Promise.resolve(existingConfig);
        }

        if (studentAccessConfigLoadPromise) {
            return studentAccessConfigLoadPromise;
        }

        const cacheBust = 'v=' + Date.now();
        const candidates = [
            new URL('../_shared/student-access-config.js?' + cacheBust, document.baseURI).toString(),
            new URL('../../_shared/student-access-config.js?' + cacheBust, document.baseURI).toString(),
            new URL('./student-access-config.js?' + cacheBust, new URL('../_shared/', document.baseURI)).toString()
        ];

        studentAccessConfigLoadPromise = new Promise(function (resolve) {
            let index = 0;

            function tryNext() {
                const loadedConfig = window.SIMULATION_ENHANCER_STUDENT_ACCESS || readGlobalBinding('SIMULATION_ENHANCER_STUDENT_ACCESS');
                if (loadedConfig) {
                    resolve(loadedConfig);
                    return;
                }

                if (index >= candidates.length) {
                    resolve(null);
                    return;
                }

                const script = document.createElement('script');
                script.src = candidates[index++];
                script.async = true;
                script.onload = function () {
                    resolve(window.SIMULATION_ENHANCER_STUDENT_ACCESS || readGlobalBinding('SIMULATION_ENHANCER_STUDENT_ACCESS') || null);
                };
                script.onerror = tryNext;
                document.head.appendChild(script);
            }

            tryNext();
        });

        return studentAccessConfigLoadPromise;
    }

    function getAcceptedStudentAccessHashes(config) {
        const values = [];
        const primaryHash = String((config && config.passwordHash) || '').trim().toLowerCase();
        if (primaryHash) {
            values.push(primaryHash);
        }

        const extraHashes = config && Array.isArray(config.acceptedPasswordHashes)
            ? config.acceptedPasswordHashes
            : [];

        extraHashes.forEach(function (hashValue) {
            const normalized = String(hashValue || '').trim().toLowerCase();
            if (normalized) {
                values.push(normalized);
            }
        });

        return Array.from(new Set(values));
    }

    function resolveRosterApiToken(config, digest) {
        const configuredToken = String((config && config.apiAccessToken) || '').trim().toLowerCase();
        if (configuredToken) {
            return configuredToken;
        }
        return String(digest || '').trim().toLowerCase();
    }

    function isStudentAccessAuthenticated() {
        try {
            if (window.sessionStorage.getItem(STUDENT_ACCESS_SESSION_KEY) !== '1') {
                return false;
            }

            const config = getStudentAccessConfig();
            const acceptedHashes = getAcceptedStudentAccessHashes(config);
            const currentToken = getStudentAccessToken().trim().toLowerCase();

            if (acceptedHashes.length && acceptedHashes.indexOf(currentToken) === -1) {
                window.sessionStorage.removeItem(STUDENT_ACCESS_SESSION_KEY);
                window.sessionStorage.removeItem(STUDENT_ACCESS_TOKEN_SESSION_KEY);
                clearRosterApiCache();
                return false;
            }

            return true;
        } catch (error) {
            return false;
        }
    }

    function setStudentAccessAuthenticated(value) {
        try {
            if (value) {
                window.sessionStorage.setItem(STUDENT_ACCESS_SESSION_KEY, '1');
            } else {
                window.sessionStorage.removeItem(STUDENT_ACCESS_SESSION_KEY);
                window.sessionStorage.removeItem(STUDENT_ACCESS_TOKEN_SESSION_KEY);
            }
            clearRosterApiCache();
        } catch (error) {
            return;
        }
    }

    function getStudentAccessToken() {
        try {
            return window.sessionStorage.getItem(STUDENT_ACCESS_TOKEN_SESSION_KEY) || '';
        } catch (error) {
            return '';
        }
    }

    function setStudentAccessToken(token) {
        try {
            if (token) {
                window.sessionStorage.setItem(STUDENT_ACCESS_TOKEN_SESSION_KEY, String(token));
            } else {
                window.sessionStorage.removeItem(STUDENT_ACCESS_TOKEN_SESSION_KEY);
            }
            clearRosterApiCache();
        } catch (error) {
            return;
        }
    }

    function updateStudentAccessStatus(message, type) {
        const status = document.getElementById('enhancerStudentAccessStatus');
        if (!status) {
            return;
        }

        status.textContent = message;
        if (type === 'success') {
            status.style.color = '#7fffc0';
            return;
        }
        if (type === 'error') {
            status.style.color = '#ff9f9f';
            return;
        }
        status.style.color = '#ffdd88';
    }

    function hashStudentAccessInput(rawText) {
        if (!window.crypto || !window.crypto.subtle || !window.TextEncoder) {
            return Promise.resolve('');
        }

        const bytes = new TextEncoder().encode(String(rawText || ''));
        return window.crypto.subtle.digest('SHA-256', bytes).then(function (buffer) {
            return Array.from(new Uint8Array(buffer)).map(function (value) {
                return value.toString(16).padStart(2, '0');
            }).join('');
        }).catch(function () {
            return '';
        });
    }

    function setupStudentAccessGate() {
        const visitorCheckbox = document.getElementById('visitorMode');
        const unlockButton = document.getElementById('unlockStudentModeBtn');
        const accessPanel = document.getElementById('studentAccessPanel');
        const passwordInput = document.getElementById('studentAccessPassword');
        const confirmButton = document.getElementById('confirmStudentAccessBtn');
        const config = getStudentAccessConfig();

        if (!visitorCheckbox || !unlockButton || !accessPanel || !passwordInput || !confirmButton) {
            return;
        }

        if (!config.rememberStudentAccess) {
            setStudentAccessAuthenticated(false);
            setStudentAccessToken('');
            visitorCheckbox.checked = true;
            visitorCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
        }

        if (!config.enabled) {
            unlockButton.classList.add('enhancer-hidden');
            updateStudentAccessStatus('Modo estudante sem senha (controle desativado).', 'info');
            setStudentAccessAuthenticated(true);
            return;
        }

        updateStudentAccessStatus(config.hint || 'Para sair do modo visitante, informe a senha.', 'info');

        if (isStudentAccessAuthenticated()) {
            visitorCheckbox.checked = false;
            visitorCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
            updateStudentAccessStatus('Acesso de estudante liberado nesta sessão.', 'success');
            populateSimulationSheetOptions(getFieldValue('studentSheet'));
        }

        if (unlockButton.dataset.enhancerBound !== 'true') {
            unlockButton.addEventListener('click', function () {
                accessPanel.classList.toggle('enhancer-hidden');
                if (!accessPanel.classList.contains('enhancer-hidden')) {
                    passwordInput.focus();
                }
            });
            unlockButton.dataset.enhancerBound = 'true';
        }

        if (confirmButton.dataset.enhancerBound !== 'true') {
            confirmButton.addEventListener('click', function () {
                const plainPassword = (passwordInput.value || '').trim();
                if (!plainPassword) {
                    updateStudentAccessStatus('Digite a senha antes de liberar o modo estudante.', 'error');
                    return;
                }

                const seed = String(config.salt || '') + plainPassword;
                hashStudentAccessInput(seed).then(function (digest) {
                    const acceptedHashes = getAcceptedStudentAccessHashes(config);
                    if (!digest || (acceptedHashes.length && acceptedHashes.indexOf(String(digest).toLowerCase()) === -1)) {
                        updateStudentAccessStatus('Senha inválida. Permanecendo no modo visitante.', 'error');
                        setStudentAccessAuthenticated(false);
                        setStudentAccessToken('');
                        visitorCheckbox.checked = true;
                        visitorCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
                        return;
                    }

                    setStudentAccessAuthenticated(true);
                    setStudentAccessToken(resolveRosterApiToken(config, digest));
                    updateStudentAccessStatus('Acesso de estudante liberado com sucesso.', 'success');
                    visitorCheckbox.checked = false;
                    visitorCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
                    populateSimulationSheetOptions(getFieldValue('studentSheet'));
                    passwordInput.value = '';
                    accessPanel.classList.add('enhancer-hidden');
                });
            });
            confirmButton.dataset.enhancerBound = 'true';
        }
    }

        function setupStudentFieldInteractions() {
            ['studentSheet'].forEach(function (fieldId) {
            const field = document.getElementById(fieldId);
            if (!field || field.dataset.enhancerRosterBound === 'true') {
                return;
            }

            field.addEventListener('change', function () {
                syncSelectedSheetMetadata();
                populateSimulationStudentOptions();
                syncResolvedStudentName();
                saveExerciseState();
            });
            field.dataset.enhancerRosterBound = 'true';
        });

        const studentNameSelect = document.getElementById('studentNameSelect');
        if (studentNameSelect && studentNameSelect.dataset.enhancerRosterBound !== 'true') {
            studentNameSelect.addEventListener('change', function () {
                const manualMode = studentNameSelect.value === '__OTHER__';
                const manualRow = document.getElementById('studentNameManualRow');
                const manualInput = document.getElementById('studentNameManual');
                if (manualRow) {
                    manualRow.classList.toggle('enhancer-hidden', !manualMode);
                }
                if (manualInput) {
                    manualInput.required = manualMode;
                    if (!manualMode) {
                        manualInput.value = '';
                    }
                }
                syncResolvedStudentName();
                saveExerciseState();
            });
            studentNameSelect.dataset.enhancerRosterBound = 'true';
        }

        const studentNameManual = document.getElementById('studentNameManual');
        if (studentNameManual && studentNameManual.dataset.enhancerRosterBound !== 'true') {
            studentNameManual.addEventListener('input', function () {
                syncResolvedStudentName();
                saveExerciseState();
            });
            studentNameManual.dataset.enhancerRosterBound = 'true';
        }
    }

    function loadStudentDatabase() {
        if (isGoogleOnlyRosterMode()) {
            return Promise.resolve(DEFAULT_DATABASE);
        }

        const loadedDatabase = readGlobalBinding('STUDENT_DATABASE') || window.STUDENT_DATABASE;
        if (loadedDatabase) {
            return Promise.resolve(loadedDatabase);
        }

        if (studentDatabaseLoadPromise) {
            return studentDatabaseLoadPromise;
        }

        const candidates = [
            new URL('../AvaliacaoBimestralEducacaoDigital/alunos.js', document.baseURI).toString(),
            new URL('../../AvaliacaoBimestralEducacaoDigital/alunos.js', document.baseURI).toString()
        ];

        studentDatabaseLoadPromise = new Promise(function (resolve) {
            let index = 0;

            function tryNext() {
                const studentDatabase = readGlobalBinding('STUDENT_DATABASE') || window.STUDENT_DATABASE;
                if (studentDatabase) {
                    resolve(studentDatabase);
                    return;
                }
                if (index >= candidates.length) {
                    resolve(DEFAULT_DATABASE);
                    return;
                }

                const script = document.createElement('script');
                script.src = candidates[index++];
                script.async = true;
                script.onload = function () {
                    resolve(readGlobalBinding('STUDENT_DATABASE') || window.STUDENT_DATABASE || DEFAULT_DATABASE);
                };
                script.onerror = tryNext;
                document.head.appendChild(script);
            }

            tryNext();
        });

        return studentDatabaseLoadPromise;
    }

    function getStudentSource() {
        return readGlobalBinding('STUDENT_DATABASE') || window.STUDENT_DATABASE || DEFAULT_DATABASE;
    }

    function getRosterSourceMode() {
        const externalMode = window.SIMULATION_ENHANCER_ROSTER_MODE
            || readGlobalBinding('SIMULATION_ENHANCER_ROSTER_MODE')
            || config.rosterSourceMode
            || '';

        const normalized = String(externalMode || '').trim().toLowerCase();
        if (normalized === 'merge' || normalized === 'local-only' || normalized === 'google-only') {
            return normalized;
        }
        return 'merge';
    }

    function isGoogleOnlyRosterMode() {
        return getRosterSourceMode() === 'google-only';
    }

    function getLocalAvailableSheets() {
        return Object.keys(getStudentSource().bySheet || {}).sort(function (first, second) {
            return first.localeCompare(second, 'pt-BR');
        });
    }

    function getSheetMetadata(sheetName) {
        const normalizedSheetName = String(sheetName || '').trim();
        if (!normalizedSheetName) {
            return {
                sheetName: '',
                serie: '',
                turma: '',
                trilha: ''
            };
        }

        const exactSerieTurmaMatch = normalizedSheetName.match(/^([123]o ano)\s+([A-Z])$/i);
        if (exactSerieTurmaMatch) {
            return {
                sheetName: normalizedSheetName,
                serie: exactSerieTurmaMatch[1].replace(/\s+/g, ' ').trim(),
                turma: exactSerieTurmaMatch[2].trim().toUpperCase(),
                trilha: ''
            };
        }

        const embeddedSerieTurmaMatch = normalizedSheetName.match(/([123]o ano)\s+([A-Z])/i);
        return {
            sheetName: normalizedSheetName,
            serie: embeddedSerieTurmaMatch ? embeddedSerieTurmaMatch[1].replace(/\s+/g, ' ').trim() : '',
            turma: embeddedSerieTurmaMatch ? embeddedSerieTurmaMatch[2].trim().toUpperCase() : '',
            trilha: normalizedSheetName
        };
    }

    function syncSelectedSheetMetadata() {
        const metadata = getSheetMetadata(getFieldValue('studentSheet'));
        const studentGrade = document.getElementById('studentGrade');
        const studentClass = document.getElementById('studentClass');
        const studentTrail = document.getElementById('studentTrail');

        if (studentGrade) {
            studentGrade.value = metadata.serie;
        }
        if (studentClass) {
            studentClass.value = metadata.turma;
        }
        if (studentTrail) {
            studentTrail.value = metadata.trilha;
        }
    }

    function getLocalStudentNames(filters) {
        const studentSource = getStudentSource();
        const names = new Set();
        const preferredSheet = String(filters.sheetName || '').trim() || resolveSimulationSheetName(filters.serie, filters.turma, filters.trilha);
        const serieTurmaKey = filters.serie + '|' + filters.turma;

        if (preferredSheet && studentSource.bySheet[preferredSheet]) {
            studentSource.bySheet[preferredSheet].forEach(function (name) { names.add(name); });
        }

        if (studentSource.bySerieTurma[serieTurmaKey]) {
            studentSource.bySerieTurma[serieTurmaKey].forEach(function (name) { names.add(name); });
        }

        if (filters.trilha && studentSource.byTrilha[filters.trilha]) {
            studentSource.byTrilha[filters.trilha].forEach(function (name) { names.add(name); });
        }

        return Array.from(names).sort(function (first, second) {
            return first.localeCompare(second, 'pt-BR');
        });
    }

    function shouldUseProtectedRosterApi() {
        const config = getStudentAccessConfig();
        const apiUrl = String(config.rosterApiUrl || '').trim();
        if (!apiUrl) {
            return false;
        }
        return isStudentAccessAuthenticated() && !!getStudentAccessToken();
    }

    function buildRosterCacheKey(filters) {
        return [filters.sheetName || '', filters.serie || '', filters.turma || '', filters.trilha || ''].join('|');
    }

    function clearRosterApiCache() {
        rosterApiCache = {};
        rosterSheetsCache = null;
    }

    function fetchProtectedAvailableSheets() {
        const config = getStudentAccessConfig();
        const apiUrl = String(config.rosterApiUrl || '').trim();
        const token = getStudentAccessToken();
        if (!apiUrl || !token) {
            return Promise.reject(new Error('API protegida não configurada para lista de turmas.'));
        }

        if (rosterSheetsCache && rosterSheetsCache.expiresAt > Date.now()) {
            return Promise.resolve(rosterSheetsCache.sheets);
        }

        rosterSheetsCache = null;

        const cacheTtlMs = Math.max(1000, Number(config.rosterCacheTtlMs || 15000));
        const timeoutMs = Math.max(6000, Number(config.apiTimeoutMs || 20000));
        const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const timeoutId = controller
            ? window.setTimeout(function () { controller.abort(); }, timeoutMs)
            : null;

        return fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'text/plain;charset=utf-8' },
            body: JSON.stringify({
                action: 'getAvailableSheets',
                accessToken: token
            }),
            signal: controller ? controller.signal : undefined
        })
            .catch(function (error) {
                if (error && error.name === 'AbortError') {
                    return fetch(apiUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                        body: JSON.stringify({
                            action: 'getAvailableSheets',
                            accessToken: token
                        })
                    });
                }
                throw error;
            })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('Resposta inválida da API protegida: HTTP ' + response.status);
                }
                return response.json();
            })
            .then(function (payload) {
                const payloadStatus = String((payload && payload.status) || '').trim().toLowerCase();
                if (payloadStatus === 'error') {
                    throw new Error((payload && payload.message) || 'Falha na API protegida de turmas.');
                }

                const rawSheets = Array.isArray(payload)
                    ? payload
                    : (Array.isArray(payload.sheets) ? payload.sheets : []);

                const normalized = rawSheets
                    .map(function (name) { return String(name || '').trim(); })
                    .filter(function (name) { return !!name; })
                    .sort(function (first, second) { return first.localeCompare(second, 'pt-BR'); });

                rosterSheetsCache = {
                    sheets: normalized,
                    expiresAt: Date.now() + cacheTtlMs
                };
                return normalized;
            })
            .finally(function () {
                if (timeoutId) {
                    window.clearTimeout(timeoutId);
                }
            });
    }

    function getAvailableSheetsHybrid() {
        const localSheets = getLocalAvailableSheets();

        if (isGoogleOnlyRosterMode()) {
            if (!shouldUseProtectedRosterApi()) {
                return Promise.resolve([]);
            }
            return fetchProtectedAvailableSheets().catch(function (error) {
                console.warn('[simulation-enhancer] Falha na API protegida de turmas em modo Google-only.', error);
                return [];
            });
        }

        if (!shouldUseProtectedRosterApi()) {
            return Promise.resolve(localSheets);
        }

        return fetchProtectedAvailableSheets()
            .catch(function (error) {
                console.warn('[simulation-enhancer] Falha na API protegida de turmas. Usando fallback local.', error);
                return localSheets;
            });
    }

    function populateSimulationSheetOptions(preservedValue) {
        const studentSheetSelect = document.getElementById('studentSheet');
        if (!studentSheetSelect) {
            return;
        }

        if (!isStudentAccessAuthenticated()) {
            studentSheetSelect.innerHTML = '<option value="">Libere o modo estudante para carregar turmas</option>';
            studentSheetSelect.value = '';
            return;
        }

        studentSheetSelect.innerHTML = '<option value="">Carregando turmas...</option>';

        getAvailableSheetsHybrid().then(function (sheetNames) {
            studentSheetSelect.innerHTML = (sheetNames.length
                ? '<option value="">Selecione sua turma</option>'
                : '<option value="">Nenhuma turma encontrada</option>')
                + sheetNames.map(function (sheetName) {
                    return '<option value="' + escapeHtml(sheetName) + '">' + escapeHtml(sheetName) + '</option>';
                }).join('');

            if (preservedValue && sheetNames.indexOf(preservedValue) !== -1) {
                studentSheetSelect.value = preservedValue;
            } else {
                studentSheetSelect.value = '';
            }

            syncSelectedSheetMetadata();
            populateSimulationStudentOptions(getFieldValue('studentNameSelect'));
        });
    }

    function fetchProtectedStudentNames(filters) {
        const config = getStudentAccessConfig();
        const apiUrl = String(config.rosterApiUrl || '').trim();
        const token = getStudentAccessToken();
        if (!apiUrl || !token) {
            return Promise.reject(new Error('API protegida não configurada para lista de alunos.'));
        }

        const cacheKey = buildRosterCacheKey(filters);
        const cachedEntry = rosterApiCache[cacheKey];
        if (cachedEntry && cachedEntry.expiresAt > Date.now()) {
            return Promise.resolve(cachedEntry.names);
        }

        delete rosterApiCache[cacheKey];

        const cacheTtlMs = Math.max(1000, Number(config.rosterCacheTtlMs || 15000));

        const timeoutMs = Math.max(6000, Number(config.apiTimeoutMs || 20000));
        const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const timeoutId = controller
            ? window.setTimeout(function () { controller.abort(); }, timeoutMs)
            : null;

        return fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'text/plain;charset=utf-8' },
            body: JSON.stringify({
                action: 'getStudentNames',
                sheetName: filters.sheetName || '',
                serie: filters.serie || '',
                turma: filters.turma || '',
                trilha: filters.trilha || '',
                accessToken: token
            }),
            signal: controller ? controller.signal : undefined
        })
            .catch(function (error) {
                if (error && error.name === 'AbortError') {
                    return fetch(apiUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                        body: JSON.stringify({
                            action: 'getStudentNames',
                            sheetName: filters.sheetName || '',
                            serie: filters.serie || '',
                            turma: filters.turma || '',
                            trilha: filters.trilha || '',
                            accessToken: token
                        })
                    });
                }
                throw error;
            })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('Resposta inválida da API protegida: HTTP ' + response.status);
                }
                return response.json();
            })
            .then(function (payload) {
                const payloadStatus = String((payload && payload.status) || '').trim().toLowerCase();
                if (payloadStatus === 'error') {
                    throw new Error((payload && payload.message) || 'Falha na API protegida de alunos.');
                }

                const rawNames = Array.isArray(payload)
                    ? payload
                    : (Array.isArray(payload.names) ? payload.names : []);

                const normalized = rawNames
                    .map(function (name) { return String(name || '').trim(); })
                    .filter(function (name) { return !!name; })
                    .sort(function (first, second) { return first.localeCompare(second, 'pt-BR'); });

                rosterApiCache[cacheKey] = {
                    names: normalized,
                    expiresAt: Date.now() + cacheTtlMs
                };
                return normalized;
            })
            .finally(function () {
                if (timeoutId) {
                    window.clearTimeout(timeoutId);
                }
            });
    }

    function getStudentNamesHybrid(filters) {
        const localNames = getLocalStudentNames(filters);

        if (isGoogleOnlyRosterMode()) {
            if (!shouldUseProtectedRosterApi()) {
                return Promise.resolve([]);
            }
            return fetchProtectedStudentNames(filters).catch(function (error) {
                console.warn('[simulation-enhancer] Falha na API protegida de alunos em modo Google-only.', error);
                return [];
            });
        }

        if (!shouldUseProtectedRosterApi()) {
            return Promise.resolve(localNames);
        }

        return fetchProtectedStudentNames(filters)
            .catch(function (error) {
                console.warn('[simulation-enhancer] Falha na API protegida de alunos. Usando fallback local.', error);
                return localNames;
            });
    }

    function populateSimulationStudentOptions(preservedValue) {
        const studentNameSelect = document.getElementById('studentNameSelect');
        if (!studentNameSelect) {
            return;
        }

        const sheetName = getFieldValue('studentSheet');
        const serie = getFieldValue('studentGrade');
        const turma = getFieldValue('studentClass');
        const trilha = getFieldValue('studentTrail');
        const requestToken = ++studentOptionsRequestToken;

        if (!sheetName) {
            studentNameSelect.innerHTML = '<option value="">Selecione primeiro a turma</option><option value="__OTHER__">Meu nome não está na lista</option>';
            return;
        }

        studentNameSelect.innerHTML = '<option value="">Carregando nomes...</option><option value="__OTHER__">Meu nome não está na lista</option>';

        getStudentNamesHybrid({ sheetName: sheetName, serie: serie, turma: turma, trilha: trilha }).then(function (names) {
            if (requestToken !== studentOptionsRequestToken) {
                return;
            }

            const emptyMessage = shouldUseProtectedRosterApi()
                ? 'Nenhum nome encontrado para este recorte'
                : 'Libere o modo estudante para carregar os nomes da turma';

            studentNameSelect.innerHTML = (names.length
                ? '<option value="">Selecione o nome</option>'
                : '<option value="">' + escapeHtml(emptyMessage) + '</option>')
                + names.map(function (name) {
                    return '<option value="' + escapeHtml(name) + '">' + escapeHtml(name) + '</option>';
                }).join('')
                + '<option value="__OTHER__">Meu nome não está na lista</option>';

            if (preservedValue && (preservedValue === '__OTHER__' || names.indexOf(preservedValue) !== -1)) {
                studentNameSelect.value = preservedValue;
            } else {
                studentNameSelect.value = '';
            }

            const manualMode = studentNameSelect.value === '__OTHER__';
            const manualRow = document.getElementById('studentNameManualRow');
            const manualInput = document.getElementById('studentNameManual');
            if (manualRow) {
                manualRow.classList.toggle('enhancer-hidden', !manualMode);
            }
            if (manualInput) {
                manualInput.required = manualMode;
            }
            syncResolvedStudentName();
        });
    }

    function syncResolvedStudentName() {
        const hiddenName = document.getElementById('studentName');
        if (hiddenName) {
            hiddenName.value = getResolvedStudentName();
        }
    }

    function getResolvedStudentName() {
        const studentNameSelect = document.getElementById('studentNameSelect');
        const studentNameManual = document.getElementById('studentNameManual');
        if (!studentNameSelect) {
            return getFieldValue('studentName');
        }
        if (studentNameSelect.value === '__OTHER__') {
            return studentNameManual ? studentNameManual.value.trim() : '';
        }
        return studentNameSelect.value.trim();
    }

    function ensureExerciseHeaderTools() {
        const modalHeader = document.querySelector('#exercisesModal .modal-header');
        if (!modalHeader || modalHeader.querySelector('.enhancer-modal-actions')) {
            updateExerciseLauncherState();
            updateResumeBadge();
            return;
        }

        const legacyRestart = document.getElementById('restartExercisesBtn');
        if (legacyRestart) {
            legacyRestart.classList.add('enhancer-hidden-legacy-audio');
        }

        const actions = document.createElement('div');
        actions.className = 'enhancer-modal-actions';
        actions.innerHTML = [
            '<span id="enhancerResumeBadge" class="enhancer-badge">Progresso salvo</span>',
            '<button id="enhancerRestartExercisesBtn" type="button" class="enhancer-restart-btn">Reiniciar</button>'
        ].join('');
        modalHeader.appendChild(actions);

        const restartButton = document.getElementById('enhancerRestartExercisesBtn');
        restartButton.addEventListener('click', restartExercisesFromEnhancer);

        updateExerciseLauncherState();
        updateResumeBadge();
    }

    function restartExercisesFromEnhancer() {
        const confirmed = window.confirm('Deseja reiniciar todos os exercícios? Seu progresso atual será perdido.');
        if (!confirmed) {
            return;
        }

        if (typeof window.resetAndRestartExercises === 'function') {
            window.resetAndRestartExercises();
            clearExerciseState();
            return;
        }

        resetLegacyExerciseState();

        if (typeof window.generateExercises === 'function') {
            window.generateExercises();
        }

        const modal = document.getElementById('exercisesModal');
        const exerciseContainer = document.getElementById('exerciseContainer');
        const conclusionContainer = document.getElementById('conclusionContainer');
        const resultsContainer = document.getElementById('resultsContainer');
        if (modal) {
            modal.style.display = 'flex';
        }
        if (exerciseContainer) {
            exerciseContainer.style.display = 'block';
        }
        if (conclusionContainer) {
            conclusionContainer.style.display = 'none';
        }
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }

        if (typeof window.showCurrentExercise === 'function') {
            window.showCurrentExercise();
        }

        clearExerciseState();
    }

    function resetLegacyExerciseState() {
        writeGlobalBinding('currentExercise', 0);
        writeGlobalBinding('exerciseResults', []);
        writeGlobalBinding('skippedQuestions', 0);
        writeGlobalBinding('currentExerciseAttempts', 0);
        writeGlobalBinding('conclusionTextSaved', '');

        const conclusionText = document.getElementById('conclusionText');
        const finalConclusion = document.getElementById('finalConclusion');
        const resultsSummary = document.getElementById('resultsSummary');
        const emailStatus = document.getElementById('emailStatus');
        const studentName = document.getElementById('studentName');
        const studentNameSelect = document.getElementById('studentNameSelect');
        const studentNameManual = document.getElementById('studentNameManual');

        if (conclusionText) {
            conclusionText.value = '';
        }
        if (finalConclusion) {
            finalConclusion.value = '';
        }
        if (resultsSummary) {
            resultsSummary.innerHTML = '';
        }
        if (emailStatus) {
            emailStatus.textContent = '';
            emailStatus.className = 'email-status';
            emailStatus.style.display = 'none';
        }
        if (studentName) {
            studentName.value = '';
        }
        if (studentNameSelect) {
            studentNameSelect.value = '';
        }
        if (studentNameManual) {
            studentNameManual.value = '';
        }

        const aiPreview = document.getElementById('enhancerAiPreview');
        if (aiPreview) {
            aiPreview.innerHTML = '<h4>Avaliacao local da conclusao</h4><p class="enhancer-inline-note">Escreva a conclusao para ver a leitura automatizada.</p>';
        }
        lastAiAnalysis = null;
    }

    function updateExerciseLauncherState() {
        const mainExerciseBtn = document.getElementById('mainExerciseBtn');
        if (!mainExerciseBtn) {
            return;
        }

        if (!mainExerciseBtn.dataset.defaultLabel) {
            mainExerciseBtn.dataset.defaultLabel = mainExerciseBtn.textContent.trim() || 'Iniciar Exercicios';
        }

        const hasSavedState = hasResumableExerciseState(getSavedExerciseState());
        mainExerciseBtn.textContent = hasSavedState ? 'Continuar Exercicios' : mainExerciseBtn.dataset.defaultLabel;
        mainExerciseBtn.classList.toggle('pulse', !hasSavedState);
    }

    function updateResumeBadge(forceVisible) {
        const badge = document.getElementById('enhancerResumeBadge');
        if (!badge) {
            return;
        }

        const shouldShow = typeof forceVisible === 'boolean' ? forceVisible : hasResumableExerciseState(getSavedExerciseState());
        badge.style.display = shouldShow ? 'inline-flex' : 'none';
    }

    function setupAudioControls() {
        const legacyAudio = document.getElementById('audioControls');
        if (legacyAudio) {
            legacyAudio.classList.add('enhancer-hidden-legacy-audio');
        }

        if (document.getElementById('enhancerAudioControls')) {
            return;
        }

        narrationTracks = buildNarrationTracks();

        const audioBar = document.createElement('div');
        audioBar.id = 'enhancerAudioControls';
        audioBar.className = 'audio-controls enhancer-audio-controls';
        audioBar.innerHTML = [
            '<button id="enhancerPrevTrackBtn" type="button">◀◀</button>',
            '<button id="enhancerPlayPauseBtn" type="button">▶️ Iniciar</button>',
            '<button id="enhancerNextTrackBtn" type="button">▶▶</button>',
            '<span id="enhancerTrackCounter" class="enhancer-track-counter">Trecho 0/' + narrationTracks.length + '</span>',
            '<div class="enhancer-voice-group">',
            '<label for="enhancerVoiceSelect">Voz:</label>',
            '<select id="enhancerVoiceSelect" aria-label="Selecionar voz da narracao"><option value="">Carregando vozes...</option></select>',
            '</div>'
        ].join('');

        const container = document.querySelector('.container') || document.body;
        container.appendChild(audioBar);

        document.getElementById('enhancerPrevTrackBtn').addEventListener('click', playPreviousTrack);
        document.getElementById('enhancerPlayPauseBtn').addEventListener('click', toggleAudioPlayback);
        document.getElementById('enhancerNextTrackBtn').addEventListener('click', playNextTrack);
        setupVoiceSelector();
        updateAudioUi();
    }

    function setupSolvedExerciseAudio() {
        ensureSolvedExerciseAudioButtons();

        wrapFunction('openSolvedExercisesModal', function () {
            ensureSolvedExerciseAudioButtons();
        });

        wrapFunction('closeSolvedExercisesModal', function () {
            stopAudioPlayback();
        });
    }

    function ensureSolvedExerciseAudioButtons() {
        const solvedModal = document.getElementById('solvedExercisesModal');
        if (!solvedModal || solvedModal.querySelector('.audio-example-btn')) {
            return;
        }

        const exercises = solvedModal.querySelectorAll('.solved-exercise');
        exercises.forEach(function (exercise, index) {
            let button = exercise.querySelector('.enhancer-example-audio-btn');
            if (!button) {
                button = document.createElement('button');
                button.type = 'button';
                button.className = 'enhancer-example-audio-btn';
                button.textContent = '🔊 Ouvir resolução';
                button.dataset.exampleIndex = String(index);
                exercise.appendChild(button);
            }

            if (button.dataset.enhancerBound === 'true') {
                return;
            }

            button.addEventListener('click', function () {
                toggleSolvedExerciseAudio(button, exercise);
            });
            button.dataset.enhancerBound = 'true';
        });
    }

    function toggleSolvedExerciseAudio(button, exercise) {
        if (!window.speechSynthesis) {
            return;
        }

        const exampleIndex = getSolvedExerciseNarrationIndex(button);
        const narrationText = buildSolvedExerciseNarration(exercise, exampleIndex);
        if (!narrationText) {
            return;
        }

        if (activeAudioMode === 'example' && activeExampleButton === button && speaking) {
            if (audioPaused && activeUtterance) {
                window.speechSynthesis.resume();
                audioPaused = false;
                updateSolvedExerciseButtonState(button, 'playing');
            } else {
                window.speechSynthesis.pause();
                audioPaused = true;
                updateSolvedExerciseButtonState(button, 'paused');
            }
            updateAudioUi();
            return;
        }

        stopAudioPlayback();

        activeAudioMode = 'example';
        activeExampleButton = button;
        updateSolvedExerciseButtonState(button, 'playing');
        updateAudioUi();

        activeUtterance = new SpeechSynthesisUtterance(narrationText);
        activeUtterance.lang = selectedVoice ? selectedVoice.lang : 'pt-BR';
        activeUtterance.rate = 1;
        activeUtterance.pitch = 1;
        if (selectedVoice) {
            activeUtterance.voice = selectedVoice;
        }

        speaking = true;
        audioPaused = false;

        activeUtterance.onend = function () {
            stopAudioPlayback();
        };

        activeUtterance.onerror = function () {
            stopAudioPlayback();
        };

        startUtterance(activeUtterance);
    }

    function getSolvedExerciseNarrationIndex(button) {
        if (!button) {
            return 0;
        }

        if (button.dataset.example) {
            return Number(button.dataset.example) || 0;
        }

        if (button.dataset.exampleIndex) {
            return (Number(button.dataset.exampleIndex) || 0) + 1;
        }

        return 0;
    }

    function getLocalExampleNarration(exampleIndex) {
        const localNarrations = readGlobalBinding('exampleNarrations');
        if (!localNarrations || !exampleIndex) {
            return '';
        }

        const rawNarration = localNarrations[String(exampleIndex)] || localNarrations[exampleIndex];
        if (typeof rawNarration === 'function') {
            try {
                return String(rawNarration(exampleIndex) || '').trim();
            } catch (error) {
                return '';
            }
        }

        return String(rawNarration || '').trim();
    }

    function buildSolvedExerciseNarration(exercise, exampleIndex) {
        if (!exercise) {
            return '';
        }

        const localNarration = getLocalExampleNarration(exampleIndex);
        if (localNarration) {
            return localNarration;
        }

        return Array.from(exercise.querySelectorAll('h4, p, .solution-step, li'))
            .map(function (node) {
                return node.textContent.replace(/\s+/g, ' ').trim();
            })
            .filter(Boolean)
            .join('. ');
    }

    function updateSolvedExerciseButtonState(button, state) {
        if (!button) {
            return;
        }

        if (state === 'playing') {
            button.textContent = '⏸ Pausar resolução';
            button.classList.add('is-playing');
            return;
        }

        if (state === 'paused') {
            button.textContent = '▶ Retomar resolução';
            button.classList.add('is-playing');
            return;
        }

        button.textContent = '🔊 Ouvir resolução';
        button.classList.remove('is-playing');
    }

    function resetSolvedExerciseAudioButtons() {
        document.querySelectorAll('.enhancer-example-audio-btn').forEach(function (button) {
            updateSolvedExerciseButtonState(button, 'idle');
        });
        activeExampleButton = null;
    }

    function normalizeLocalNarrationTrack(track) {
        if (typeof track === 'function') {
            return track;
        }

        const normalizedTrack = String(track || '').trim();
        return normalizedTrack ? normalizedTrack : null;
    }

    function getLocalNarrationTracks() {
        const localTracks = readGlobalBinding('tracks');
        if (!Array.isArray(localTracks) || !localTracks.length) {
            return null;
        }

        const normalizedTracks = localTracks.map(function (track) {
            return normalizeLocalNarrationTrack(track);
        }).filter(Boolean);

        return normalizedTracks.length ? normalizedTracks : null;
    }

    function resolveNarrationTrackText(track, index) {
        if (typeof track === 'function') {
            try {
                return String(track(index) || '').trim();
            } catch (error) {
                return '';
            }
        }

        return String(track || '').trim();
    }

    function buildNarrationTracks() {
        const localTracks = getLocalNarrationTracks();
        if (localTracks) {
            return localTracks;
        }

        const title = simulationName;
        const description = Array.from(document.querySelectorAll('header p, .panel-title, .formula-box, .status-indicator, .measurement-label, .theory-section h3, .theory-content p'))
            .map(function (node) {
                return node.textContent.replace(/\s+/g, ' ').trim();
            })
            .filter(Boolean);

        const controlLabels = Array.from(document.querySelectorAll('.controls-panel label')).map(function (label) {
            return label.textContent.replace(/\s+/g, ' ').trim();
        }).filter(Boolean);

        const theoryHighlights = Array.from(document.querySelectorAll('.theory-content li')).slice(0, 8).map(function (item) {
            return item.textContent.replace(/\s+/g, ' ').trim();
        }).filter(Boolean);

        const introTrack = [
            title + '.',
            description.slice(0, 4).join(' ')
        ].join(' ').trim();

        const controlsTrack = controlLabels.length
            ? 'Controles disponiveis: ' + controlLabels.join('. ') + '.'
            : '';

        const theoryTrack = theoryHighlights.length
            ? 'Pontos centrais da teoria: ' + theoryHighlights.join(' ')
            : description.slice(4, 10).join(' ');

        return [introTrack, controlsTrack, theoryTrack].filter(Boolean);
    }

    function getPreferredVoices(voices) {
        const preferred = voices.filter(function (voice) {
            return /^pt(-|_)/i.test(voice.lang || '');
        });
        return preferred.length ? preferred : voices;
    }

    function getVoiceKey(voice) {
        return [voice.name || '', voice.lang || '', voice.voiceURI || ''].join('::');
    }

    function populateVoiceSelector(voices) {
        const voiceSelect = document.getElementById('enhancerVoiceSelect');
        if (!voiceSelect) {
            return;
        }

        const preferredVoices = getPreferredVoices(voices || []);
        voiceSelect.innerHTML = '';

        if (!preferredVoices.length) {
            voiceSelect.innerHTML = '<option value="">Sem vozes disponiveis</option>';
            voiceSelect.disabled = true;
            selectedVoice = null;
            return;
        }

        preferredVoices.forEach(function (voice) {
            const option = document.createElement('option');
            option.value = getVoiceKey(voice);
            option.textContent = voice.name + ' (' + voice.lang + ')';
            voiceSelect.appendChild(option);
        });

        const savedVoiceKey = localStorage.getItem(AUDIO_STORAGE_KEY);
        selectedVoice = preferredVoices.find(function (voice) {
            return getVoiceKey(voice) === savedVoiceKey;
        }) || preferredVoices[0];

        voiceSelect.disabled = false;
        voiceSelect.value = getVoiceKey(selectedVoice);
    }

    function setupVoiceSelector() {
        const voiceSelect = document.getElementById('enhancerVoiceSelect');
        if (!voiceSelect || !window.speechSynthesis) {
            return;
        }

        function loadVoices() {
            populateVoiceSelector(window.speechSynthesis.getVoices());
        }

        voiceSelect.addEventListener('change', function () {
            const voices = getPreferredVoices(window.speechSynthesis.getVoices());
            selectedVoice = voices.find(function (voice) {
                return getVoiceKey(voice) === voiceSelect.value;
            }) || null;
            if (selectedVoice) {
                localStorage.setItem(AUDIO_STORAGE_KEY, getVoiceKey(selectedVoice));
            }
        });

        loadVoices();
        if (!window.speechSynthesis.getVoices().length) {
            window.speechSynthesis.onvoiceschanged = loadVoices;
        }
    }

    function updateAudioUi() {
        const playPauseBtn = document.getElementById('enhancerPlayPauseBtn');
        const trackCounter = document.getElementById('enhancerTrackCounter');
        if (!playPauseBtn || !trackCounter) {
            return;
        }

        if (activeAudioMode === 'track' && speaking && !audioPaused) {
            playPauseBtn.textContent = '⏸ Pausar';
            trackCounter.textContent = 'Trecho ' + (narrationIndex + 1) + '/' + narrationTracks.length;
        } else if (activeAudioMode === 'track' && speaking && audioPaused) {
            playPauseBtn.textContent = '▶ Retomar';
            trackCounter.textContent = 'Trecho ' + (narrationIndex + 1) + '/' + narrationTracks.length;
        } else {
            playPauseBtn.textContent = '▶️ Iniciar';
            trackCounter.textContent = 'Trecho 0/' + narrationTracks.length;
        }
    }

    function playNextTrack() {
        if (!narrationTracks.length) {
            return;
        }
        narrationIndex = narrationIndex >= narrationTracks.length - 1 ? narrationTracks.length - 1 : narrationIndex + 1;
        speakTrack(narrationIndex);
    }

    function playPreviousTrack() {
        if (!narrationTracks.length) {
            return;
        }
        narrationIndex = Math.max(0, narrationIndex - 1);
        speakTrack(narrationIndex);
    }

    function speakTrack(index) {
        if (!window.speechSynthesis || !narrationTracks.length) {
            return;
        }

        const text = resolveNarrationTrackText(narrationTracks[index], index);
        if (!text) {
            stopAudioPlayback();
            return;
        }

        if (window.speechSynthesis.speaking || window.speechSynthesis.pending || window.speechSynthesis.paused) {
            stopAudioPlayback();
        }

        activeUtterance = new SpeechSynthesisUtterance(text);
        activeUtterance.lang = selectedVoice ? selectedVoice.lang : 'pt-BR';
        activeUtterance.rate = 1;
        activeUtterance.pitch = 1;
        if (selectedVoice) {
            activeUtterance.voice = selectedVoice;
        }

        activeAudioMode = 'track';
        speaking = true;
        audioPaused = false;
        narrationIndex = index;
        updateAudioUi();

        activeUtterance.onend = function () {
            if (audioPaused) {
                return;
            }
            if (narrationIndex < narrationTracks.length - 1) {
                speakTrack(narrationIndex + 1);
                return;
            }
            stopAudioPlayback();
        };

        activeUtterance.onerror = function () {
            stopAudioPlayback();
        };

        startUtterance(activeUtterance);
    }

    function toggleAudioPlayback() {
        if (!window.speechSynthesis || !narrationTracks.length) {
            return;
        }

        if (speaking && !audioPaused) {
            window.speechSynthesis.pause();
            audioPaused = true;
            updateAudioUi();
            return;
        }

        if (speaking && audioPaused && activeUtterance) {
            window.speechSynthesis.resume();
            audioPaused = false;
            updateAudioUi();
            return;
        }

        speakTrack(0);
    }

    function stopAudioPlayback() {
        speechRequestToken += 1;
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        resetSolvedExerciseAudioButtons();
        speaking = false;
        audioPaused = false;
        activeAudioMode = null;
        narrationIndex = 0;
        activeUtterance = null;
        updateAudioUi();
    }

    function startUtterance(utterance) {
        if (!window.speechSynthesis || !utterance) {
            return;
        }

        const requestToken = ++speechRequestToken;
        if (window.speechSynthesis.speaking || window.speechSynthesis.pending || window.speechSynthesis.paused) {
            window.speechSynthesis.cancel();
        }

        window.setTimeout(function () {
            if (requestToken !== speechRequestToken || !activeUtterance) {
                return;
            }

            try {
                window.speechSynthesis.speak(utterance);
            } catch (error) {
                stopAudioPlayback();
            }
        }, 30);
    }

    function setupAudioLifecycleGuards() {
        document.addEventListener('visibilitychange', function () {
            if (document.hidden) {
                stopAudioPlayback();
            }
        });

        window.addEventListener('pagehide', function () {
            stopAudioPlayback();
        });
    }

    function setupExercisePersistence() {
        wrapFunction('showCurrentExercise', function () {
            const state = getSavedExerciseState();
            const container = document.getElementById('exerciseContainer');
            const currentExercise = readGlobalBinding('currentExercise');
            if (container && state && state.selectedOption && state.currentExercise === currentExercise) {
                const option = Array.from(container.querySelectorAll('.option')).find(function (item) {
                    return item.dataset.value === state.selectedOption;
                });
                if (option) {
                    option.classList.add('selected');
                }
            }

            bindExerciseOptionPersistence();
            saveExerciseState();
        });

        wrapFunction('checkAnswer', function () {
            window.setTimeout(appendCorrectAnswerFeedback, 0);
            window.setTimeout(saveExerciseState, 1650);
        });

        wrapFunction('skipExercise', function () {
            window.setTimeout(saveExerciseState, 80);
        });

        wrapFunction('showConclusion', function () {
            const field = document.getElementById('conclusionText');
            const state = getSavedExerciseState();
            if (field && state && state.conclusionTextSaved && !field.value) {
                field.value = state.conclusionTextSaved;
            }
            bindFormPersistence();
            saveExerciseState();
        });

        wrapFunction('showResults', function () {
            const finalConclusion = document.getElementById('finalConclusion');
            if (finalConclusion) {
                renderAiPreview(finalConclusion.value);
            }
            bindFormPersistence();
            saveExerciseState();
        });

        const originalClose = window.closeExercisesModal;
        if (typeof originalClose === 'function' && !originalClose.__enhancerWrapped) {
            window.closeExercisesModal = function () {
                persistExerciseStateSnapshot();
                const result = originalClose.apply(this, arguments);
                updateExerciseLauncherState();
                updateResumeBadge();
                return result;
            };
            window.closeExercisesModal.__enhancerWrapped = true;
        }

        wrapFunction('openExercisesModal', function () {
            restoreExerciseState();
            bindFormPersistence();
            updateExerciseLauncherState();
            updateResumeBadge();
        });

        const originalResetExerciseState = window.resetExerciseState;
        if (typeof originalResetExerciseState === 'function' && !originalResetExerciseState.__enhancerWrapped) {
            window.resetExerciseState = function () {
                const result = originalResetExerciseState.apply(this, arguments);
                clearExerciseState();
                return result;
            };
            window.resetExerciseState.__enhancerWrapped = true;
        }

        const originalResetAndRestart = window.resetAndRestartExercises;
        if (typeof originalResetAndRestart === 'function' && !originalResetAndRestart.__enhancerWrapped) {
            window.resetAndRestartExercises = function () {
                const result = originalResetAndRestart.apply(this, arguments);
                window.setTimeout(clearExerciseState, 40);
                return result;
            };
            window.resetAndRestartExercises.__enhancerWrapped = true;
        }

        const originalRegenerateExercise = window.generateNewExerciseOfSameType;
        if (typeof originalRegenerateExercise === 'function' && !originalRegenerateExercise.__enhancerWrapped) {
            window.generateNewExerciseOfSameType = function () {
                const currentExercise = typeof readGlobalBinding('currentExercise') === 'number' ? readGlobalBinding('currentExercise') : 0;
                const exercisesBefore = Array.isArray(readGlobalBinding('exercises')) ? readGlobalBinding('exercises') : [];
                const previousSignature = buildExerciseSignature(exercisesBefore[currentExercise]);
                let attempts = 0;
                let result;

                do {
                    result = originalRegenerateExercise.apply(this, arguments);
                    attempts += 1;
                } while (attempts < 8 && previousSignature && previousSignature === buildExerciseSignature((Array.isArray(readGlobalBinding('exercises')) ? readGlobalBinding('exercises') : [])[currentExercise]));

                return result;
            };
            window.generateNewExerciseOfSameType.__enhancerWrapped = true;
        }

        const originalOpen = window.openExercisesModal;
        if (typeof originalOpen === 'function' && !originalOpen.__enhancerPatchedOpen) {
            window.openExercisesModal = function () {
                const savedState = getSavedExerciseState();
                if (!hasResumableExerciseState(savedState)) {
                    return originalOpen.apply(this, arguments);
                }

                const exercises = readGlobalBinding('exercises');
                if (!Array.isArray(exercises) || !exercises.length) {
                    if (typeof window.generateExercises === 'function') {
                        window.resetExerciseState && window.resetExerciseState();
                        window.generateExercises();
                    }
                }

                const modal = document.getElementById('exercisesModal');
                if (modal) {
                    modal.style.display = 'flex';
                }
                restoreExerciseState();
                return undefined;
            };
            window.openExercisesModal.__enhancerPatchedOpen = true;
        }

        const originalSendResults = window.sendResultsToSheet;
        if (typeof originalSendResults === 'function' && !originalSendResults.__enhancerWrapped) {
            window.sendResultsToSheet = enhancedSendResultsToSheet;
            window.sendResultsToSheet.__enhancerWrapped = true;
        }

        bindFormPersistence();
        updateExerciseLauncherState();
        updateResumeBadge();
    }

    function wrapFunction(name, afterCall) {
        const originalFn = window[name];
        if (typeof originalFn !== 'function' || originalFn.__enhancerWrapped) {
            return;
        }

        window[name] = function () {
            const result = originalFn.apply(this, arguments);
            afterCall();
            return result;
        };
        window[name].__enhancerWrapped = true;
    }

    function bindExerciseOptionPersistence() {
        const container = document.getElementById('exerciseContainer');
        if (!container || container.dataset.enhancerBound === 'true') {
            return;
        }

        container.addEventListener('click', function (event) {
            const option = event.target.closest('.option');
            if (!option) {
                return;
            }

            window.setTimeout(saveExerciseState, 0);
        });
        container.dataset.enhancerBound = 'true';
    }

    function buildExerciseSignature(exercise) {
        if (!exercise) {
            return '';
        }

        return JSON.stringify({
            type: exercise.type || '',
            question: exercise.question || '',
            answer: exercise.answer || '',
            options: Array.isArray(exercise.options) ? exercise.options.map(function (option) {
                if (option && typeof option === 'object') {
                    return {
                        value: option.value,
                        display: option.display
                    };
                }
                return option;
            }) : []
        });
    }

    function appendCorrectAnswerFeedback() {
        const resultDiv = document.querySelector('#exerciseContainer .result');
        const currentExercise = typeof readGlobalBinding('currentExercise') === 'number' ? readGlobalBinding('currentExercise') : 0;
        const exercises = Array.isArray(readGlobalBinding('exercises')) ? readGlobalBinding('exercises') : [];
        const exercise = exercises[currentExercise];

        if (!resultDiv || !exercise) {
            return;
        }

        const hasErrorState = resultDiv.querySelector('.error') || /incorreto/i.test(resultDiv.textContent || '');
        if (!hasErrorState || resultDiv.querySelector('.enhancer-correct-answer')) {
            return;
        }

        const answerText = resolveExerciseAnswerText(exercise);
        if (!answerText) {
            return;
        }

        const answerNote = document.createElement('div');
        answerNote.className = 'enhancer-correct-answer';
        answerNote.textContent = 'Resposta correta: ' + answerText;
        resultDiv.appendChild(answerNote);
    }

    function resolveExerciseAnswerText(exercise) {
        if (!exercise) {
            return '';
        }

        const options = Array.isArray(exercise.options) ? exercise.options : [];
        const answer = exercise.answer;

        for (let index = 0; index < options.length; index += 1) {
            const option = options[index];
            if (option && typeof option === 'object') {
                if (areEquivalentAnswers(option.value, answer) || areEquivalentAnswers(option.display, answer)) {
                    return String(option.display || option.value || '').trim();
                }
                continue;
            }

            if (areEquivalentAnswers(option, answer)) {
                return String(option || '').trim();
            }
        }

        return String(answer || '').trim();
    }

    function areEquivalentAnswers(firstValue, secondValue) {
        if (typeof firstValue === 'number' && typeof secondValue === 'number') {
            return Math.abs(firstValue - secondValue) < 1e-9;
        }

        if (typeof firstValue === 'string' && typeof secondValue === 'string') {
            return firstValue.trim() === secondValue.trim();
        }

        const firstNumeric = parseComparableNumber(firstValue);
        const secondNumeric = parseComparableNumber(secondValue);
        if (firstNumeric !== null && secondNumeric !== null) {
            return Math.abs(firstNumeric - secondNumeric) < 1e-9;
        }

        return String(firstValue || '').trim() === String(secondValue || '').trim();
    }

    function parseComparableNumber(value) {
        if (typeof value === 'number' && Number.isFinite(value)) {
            return value;
        }

        if (typeof value !== 'string') {
            return null;
        }

        const match = value.replace(',', '.').match(/-?\d+(?:\.\d+)?/);
        if (!match) {
            return null;
        }

        const parsed = Number(match[0]);
        return Number.isFinite(parsed) ? parsed : null;
    }

    function bindFormPersistence() {
        [
            'conclusionText', 'studentSheet', 'studentTrail', 'studentName', 'studentNameSelect', 'studentNameManual', 'studentGrade', 'studentClass', 'schoolTerm', 'studentEmail',
            'visitorName', 'visitorEmail', 'visitorMode',
            'criticismInput', 'suggestionInput', 'finalConclusion'
        ].forEach(function (fieldId) {
            const field = document.getElementById(fieldId);
            if (!field || field.dataset.enhancerBound === 'true') {
                return;
            }

            field.addEventListener('input', saveExerciseState);
            field.addEventListener('change', saveExerciseState);
            field.dataset.enhancerBound = 'true';
        });
    }

    function getCurrentView() {
        const results = document.getElementById('resultsContainer');
        const conclusion = document.getElementById('conclusionContainer');
        if (results && results.style.display === 'block') {
            return 'results';
        }
        if (conclusion && conclusion.style.display === 'block') {
            return 'conclusion';
        }
        return 'exercise';
    }

    function buildExerciseState() {
        const selectedOption = document.querySelector('#exerciseContainer .option.selected');
        const conclusionText = document.getElementById('conclusionText');
        const finalConclusion = document.getElementById('finalConclusion');

        return {
            exercises: Array.isArray(readGlobalBinding('exercises')) ? readGlobalBinding('exercises') : [],
            currentExercise: typeof readGlobalBinding('currentExercise') === 'number' ? readGlobalBinding('currentExercise') : 0,
            exerciseResults: Array.isArray(readGlobalBinding('exerciseResults')) ? readGlobalBinding('exerciseResults') : [],
            skippedQuestions: typeof readGlobalBinding('skippedQuestions') === 'number' ? readGlobalBinding('skippedQuestions') : 0,
            currentExerciseAttempts: typeof readGlobalBinding('currentExerciseAttempts') === 'number' ? readGlobalBinding('currentExerciseAttempts') : 0,
            conclusionTextSaved: conclusionText ? conclusionText.value : (readGlobalBinding('conclusionTextSaved') || ''),
            selectedOption: selectedOption ? selectedOption.dataset.value : '',
            view: getCurrentView(),
            formState: {
                            studentSheet: getFieldValue('studentSheet'),
                            studentTrail: getFieldValue('studentTrail'),
                            studentName: getFieldValue('studentName'),
                            studentNameSelect: getFieldValue('studentNameSelect'),
                            studentNameManual: getFieldValue('studentNameManual'),
                            studentGrade: getFieldValue('studentGrade'),
                            studentClass: getFieldValue('studentClass'),
                            schoolTerm: getFieldValue('schoolTerm'),
                            studentEmail: getFieldValue('studentEmail'),
                            visitorName: getFieldValue('visitorName'),
                            visitorEmail: getFieldValue('visitorEmail'),
                            criticismInput: getFieldValue('criticismInput'),
                            suggestionInput: getFieldValue('suggestionInput'),
                            finalConclusion: finalConclusion ? finalConclusion.value : '',
                            visitorMode: getCheckboxValue('visitorMode')
                        },
            aiAnalysis: lastAiAnalysis
        };
    }

    function getSavedExerciseState() {
        try {
            const raw = localStorage.getItem(EXERCISE_STORAGE_KEY);
            if (!raw) {
                return null;
            }
            const parsed = JSON.parse(raw);
            if (!parsed || !Array.isArray(parsed.exercises) || !parsed.exercises.length) {
                return null;
            }
            return parsed;
        } catch (error) {
            return null;
        }
    }

    function saveExerciseState() {
        const exercises = readGlobalBinding('exercises');
        if (!Array.isArray(exercises) || !exercises.length) {
            clearExerciseState();
            return;
        }

        const state = buildExerciseState();
        if (!hasMeaningfulProgress(state)) {
            clearExerciseState();
            return;
        }

        persistBuiltExerciseState(state);
    }

    function persistExerciseStateSnapshot() {
        const exercises = readGlobalBinding('exercises');
        if (!Array.isArray(exercises) || !exercises.length) {
            return;
        }

        const state = buildExerciseState();
        if (!hasMeaningfulProgress(state)) {
            return;
        }

        persistBuiltExerciseState(state);
    }

    function persistBuiltExerciseState(state) {
        if (!state) {
            return;
        }

        try {
            localStorage.setItem(EXERCISE_STORAGE_KEY, JSON.stringify(state));
            if (state.aiAnalysis) {
                localStorage.setItem(AI_STORAGE_KEY, JSON.stringify(state.aiAnalysis));
            }
        } catch (error) {
            return;
        }

        updateExerciseLauncherState();
        updateResumeBadge(true);
        flashSaveIndicator();
    }

    function hasMeaningfulProgress(state) {
        if (!state) {
            return false;
        }

        const hasCurrentExercise = Number(state.currentExercise || 0) > 0;
        const hasResults = Array.isArray(state.exerciseResults) && state.exerciseResults.length > 0;
        const hasSkipped = Number(state.skippedQuestions || 0) > 0;
        const hasAttempts = Number(state.currentExerciseAttempts || 0) > 0;
        const hasSelection = Boolean(state.selectedOption);
        const hasConclusion = Boolean(String(state.conclusionTextSaved || '').trim());
        const hasCompletedView = state.view === 'conclusion' || state.view === 'results';

        return hasCurrentExercise || hasResults || hasSkipped || hasAttempts || hasSelection || hasConclusion || hasCompletedView;
    }

    function hasResumableExerciseState(state) {
        if (!state || !Array.isArray(state.exercises) || !state.exercises.length) {
            return false;
        }

        const hasCurrentExercise = Number(state.currentExercise || 0) > 0;
        const hasResults = Array.isArray(state.exerciseResults) && state.exerciseResults.length > 0;
        const hasSkipped = Number(state.skippedQuestions || 0) > 0;
        const hasAttempts = Number(state.currentExerciseAttempts || 0) > 0;
        const hasSelection = Boolean(state.selectedOption);
        const hasConclusion = Boolean(String(
            state.conclusionTextSaved || (state.formState && state.formState.finalConclusion) || ''
        ).trim());
        const hasCompletedView = state.view === 'conclusion' || state.view === 'results';

        return hasCurrentExercise || hasResults || hasSkipped || hasAttempts || hasSelection || hasConclusion || hasCompletedView;
    }

    function clearExerciseState() {
        localStorage.removeItem(EXERCISE_STORAGE_KEY);
        localStorage.removeItem(AI_STORAGE_KEY);
        lastAiAnalysis = null;
        updateExerciseLauncherState();
        updateResumeBadge(false);
    }

    function restoreExerciseState() {
        const savedState = getSavedExerciseState();
        if (!savedState) {
            return;
        }

        writeGlobalBinding('exercises', Array.isArray(savedState.exercises) ? savedState.exercises : []);
        writeGlobalBinding('currentExercise', typeof savedState.currentExercise === 'number' ? savedState.currentExercise : 0);
        writeGlobalBinding('exerciseResults', Array.isArray(savedState.exerciseResults) ? savedState.exerciseResults : []);
        writeGlobalBinding('skippedQuestions', typeof savedState.skippedQuestions === 'number' ? savedState.skippedQuestions : 0);
        writeGlobalBinding('currentExerciseAttempts', typeof savedState.currentExerciseAttempts === 'number' ? savedState.currentExerciseAttempts : 0);
        writeGlobalBinding('conclusionTextSaved', savedState.conclusionTextSaved || '');
        lastAiAnalysis = savedState.aiAnalysis || restoreAiAnalysis();

        const exerciseContainer = document.getElementById('exerciseContainer');
        const conclusionContainer = document.getElementById('conclusionContainer');
        const resultsContainer = document.getElementById('resultsContainer');
        if (savedState.view === 'results') {
            if (exerciseContainer) exerciseContainer.style.display = 'none';
            if (conclusionContainer) conclusionContainer.style.display = 'none';
            if (resultsContainer) resultsContainer.style.display = 'none';
            if (typeof window.showResults === 'function') {
                window.showResults(savedState.formState.finalConclusion || savedState.conclusionTextSaved || '');
            }
        } else if (savedState.view === 'conclusion') {
            if (exerciseContainer) exerciseContainer.style.display = 'none';
            if (conclusionContainer) conclusionContainer.style.display = 'none';
            if (resultsContainer) resultsContainer.style.display = 'none';
            if (typeof window.showConclusion === 'function') {
                window.showConclusion();
            }
        } else if (typeof window.showCurrentExercise === 'function') {
            if (exerciseContainer) exerciseContainer.style.display = 'block';
            if (conclusionContainer) conclusionContainer.style.display = 'none';
            if (resultsContainer) resultsContainer.style.display = 'none';
            window.showCurrentExercise();
        }

        restoreFormState(savedState.formState || {});
        renderAiPreview(getFieldValue('finalConclusion') || savedState.conclusionTextSaved || '');
        updateExerciseLauncherState();
        updateResumeBadge(true);
    }

    function restoreAiAnalysis() {
        try {
            const raw = localStorage.getItem(AI_STORAGE_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch (error) {
            return null;
        }
    }

    function restoreFormState(formState) {
        Object.keys(formState || {}).forEach(function (fieldId) {
            const field = document.getElementById(fieldId);
            if (!field) {
                return;
            }
            if (field.type === 'checkbox') {
                field.checked = Boolean(formState[fieldId]);
                return;
            }
            field.value = formState[fieldId] || '';
        });
        syncSelectedSheetMetadata();
        const visitorCheckbox = document.getElementById('visitorMode');
        if (visitorCheckbox) {
            visitorCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
        }
        loadStudentDatabase().then(function () {
            populateSimulationSheetOptions(getFieldValue('studentSheet'));
            populateSimulationStudentOptions(getFieldValue('studentNameSelect'));
            syncResolvedStudentName();
        });
    }

    function getFieldValue(fieldId) {
        const field = document.getElementById(fieldId);
        return field ? field.value.trim() : '';
    }

    function getCheckboxValue(fieldId) {
        const field = document.getElementById(fieldId);
        return !!(field && field.checked);
    }

    function setupConclusionPreview() {
        const finalConclusion = document.getElementById('finalConclusion');
        if (!finalConclusion) {
            return;
        }

        finalConclusion.addEventListener('input', function () {
            renderAiPreview(finalConclusion.value);
            saveExerciseState();
        });
    }

    function getTopicReferenceTerms() {
        const rawTexts = Array.from(document.querySelectorAll('h1, h2, h3, .formula-box, .theory-content p, .theory-content li, .measurement-label, .controls-panel label'))
            .map(function (node) {
                return normalizeText(node.textContent);
            });

        const counts = Object.create(null);
        rawTexts.forEach(function (text) {
            text.split(/[^a-z0-9]+/).forEach(function (word) {
                if (!word || word.length < 4 || STOPWORDS.has(word)) {
                    return;
                }
                counts[word] = (counts[word] || 0) + 1;
            });
        });

        return Object.keys(counts)
            .sort(function (first, second) {
                return counts[second] - counts[first];
            })
            .slice(0, 18);
    }

    function analyzeConclusionWithLocalAi(text) {
        const trimmedText = String(text || '').trim();
        const normalized = normalizeText(trimmedText);
        const words = normalized.match(/[a-z0-9]+(?:\/[a-z0-9]+)?/g) || [];
        const uniqueWords = new Set(words);
        const sentences = trimmedText.split(/[.!?]+/).map(function (sentence) {
            return sentence.trim();
        }).filter(Boolean);
        const topicTerms = getTopicReferenceTerms();
        const topicHits = topicTerms.filter(function (term) {
            return normalized.includes(term);
        }).length;
        const learningHits = LEARNING_SIGNAL_TERMS.filter(function (term) {
            return normalized.includes(term);
        }).length;
        const connectorHits = CONNECTOR_TERMS.filter(function (term) {
            return normalized.includes(term);
        }).length;
        const lengthScore = clamp((words.length / 60) * 10, 0, 10);
        const semanticsScore = clamp((topicHits / 6) * 10 + Math.min(connectorHits, 3), 0, 10);
        const learningScore = clamp((learningHits / 4) * 10 + (sentences.length >= 3 ? 1 : 0), 0, 10);
        const finalScore = Number(((lengthScore * 0.2) + (semanticsScore * 0.4) + (learningScore * 0.4)).toFixed(1));

        return {
            wordCount: words.length,
            sentenceCount: sentences.length,
            lengthScore: Number(lengthScore.toFixed(1)),
            semanticsScore: Number(semanticsScore.toFixed(1)),
            learningScore: Number(learningScore.toFixed(1)),
            finalScore: finalScore,
            feedback: [
                'Palavras: ' + words.length,
                'Extensao: ' + lengthScore.toFixed(1) + '/10',
                'Coerencia tematica: ' + semanticsScore.toFixed(1) + '/10',
                'Aprendizagem evidenciada: ' + learningScore.toFixed(1) + '/10'
            ].join(' | ')
        };
    }

    function calculateCompositeSimulationScore(exerciseScorePercentage, aiConclusionScore) {
        const exerciseScore = clamp(exerciseScorePercentage / 10, 0, 10);
        return Number(((exerciseScore * SCORE_WEIGHTS.exercises) + (aiConclusionScore * SCORE_WEIGHTS.conclusion)).toFixed(1));
    }

    function renderAiPreview(conclusionText) {
        const resultsSummary = document.getElementById('resultsSummary');
        if (!resultsSummary) {
            return null;
        }

        const trimmedText = String(conclusionText || '').trim();
        let previewCard = document.getElementById('enhancerAiPreview');
        if (!previewCard) {
            previewCard = document.createElement('div');
            previewCard.id = 'enhancerAiPreview';
            previewCard.className = 'enhancer-ai-card';
            resultsSummary.insertAdjacentElement('afterend', previewCard);
        }

        if (!trimmedText) {
            previewCard.innerHTML = '<h4>Avaliacao local da conclusao</h4><p class="enhancer-inline-note">Escreva a conclusao para ver a leitura automatizada.</p>';
            return null;
        }

        lastAiAnalysis = analyzeConclusionWithLocalAi(trimmedText);
        localStorage.setItem(AI_STORAGE_KEY, JSON.stringify(lastAiAnalysis));
        const exercises = Array.isArray(readGlobalBinding('exercises')) ? readGlobalBinding('exercises') : [];
        const exerciseResults = Array.isArray(readGlobalBinding('exerciseResults')) ? readGlobalBinding('exerciseResults') : [];
        const total = exercises.length;
        const correct = exerciseResults.filter(function (result) { return result.correct; }).length;
        const exercisePercentage = total ? Math.round((correct / total) * 100) : 0;
        const finalScore = calculateCompositeSimulationScore(exercisePercentage, lastAiAnalysis.finalScore);

        previewCard.innerHTML = [
            '<h4>Avaliacao local da conclusao</h4>',
            '<div class="enhancer-ai-score">',
            '<span>Conclusao: ' + lastAiAnalysis.finalScore.toFixed(1) + '/10</span>',
            '<span>Extensao: ' + lastAiAnalysis.lengthScore.toFixed(1) + '/10</span>',
            '<span>Coerencia tematica: ' + lastAiAnalysis.semanticsScore.toFixed(1) + '/10</span>',
            '<span>Aprendizagem evidenciada: ' + lastAiAnalysis.learningScore.toFixed(1) + '/10</span>',
            '<span>Nota final combinada: ' + finalScore.toFixed(1) + '</span>',
            '</div>',
            '<p class="enhancer-inline-note">' + escapeHtml(lastAiAnalysis.feedback) + '</p>'
        ].join('');

        saveExerciseState();
        return lastAiAnalysis;
    }

    function normalizeSerieForSheet(serie) {
        return String(serie || '').replace('º', 'o').trim();
    }

    function getTermGradeColumn(schoolTerm) {
        return TERM_COLUMN_MAP[String(schoolTerm || '').trim()] || '';
    }

    function resolveSimulationSheetName(studentGrade, studentClass, studentTrail) {
        const studentSource = getStudentSource();
        const explicitSheetName = resolveSelectedSheetName();
        if (explicitSheetName) {
            return explicitSheetName;
        }

        if (studentTrail && !['Outra', 'Nenhuma (Turma de Fisica)'].includes(studentTrail) && studentSource.bySheet[studentTrail]) {
            return studentTrail;
        }

        const serie = normalizeSerieForSheet(studentGrade);
        const turma = String(studentClass || '').trim();
        if (serie && turma && studentSource.bySheet[serie + ' ' + turma]) {
            return serie + ' ' + turma;
        }

        return '';
    }

    function getManualStudentName() {
        const studentNameSelect = document.getElementById('studentNameSelect');
        const studentNameManual = document.getElementById('studentNameManual');
        if (!studentNameSelect || studentNameSelect.value !== '__OTHER__' || !studentNameManual) {
            return '';
        }

        return studentNameManual.value.trim();
    }

    function buildUnifiedSimulationPayload(formData, scoreData, aiAnalysis, finalScore) {
        const resolvedSheetName = formData.studentSheet
            || (formData.visitorMode ? 'VISITANTE' : resolveSimulationSheetName(formData.studentGrade, formData.studentClass, formData.studentTrail));

        return {
            timestamp: new Date().toISOString(),
            visitorMode: !!formData.visitorMode,
            serie: formData.studentGrade,
            turma: formData.studentClass,
            trilha: formData.studentTrail,
            coluna: getTermGradeColumn(formData.schoolTerm),
            bimestre: formData.schoolTerm,
            colunaBimestre: getTermGradeColumn(formData.schoolTerm),
            estudante: formData.studentName,
            estudanteDigitado: getManualStudentName(),
            sheetName: resolvedSheetName,
            avaliacao: 'Simulacao - ' + simulationName,
            categoria: 'simulacao',
            atividade: simulationName,
            simulacao: simulationName,
            scoreHeader: simulationName,
            nota: finalScore,
            notaExercicios: Number((scoreData.scorePercentage / 10).toFixed(1)),
            notaConclusaoIa: aiAnalysis.finalScore,
            notaPercentual: scoreData.scorePercentage + '%',
            acertosIndividuais: scoreData.correctAnswers,
            totalQuestoes: scoreData.totalExercises,
            questoes_puladas: scoreData.skippedQuestions,
            conclusao: formData.finalConclusion,
            analiseIa: aiAnalysis.feedback,
            palavrasConclusao: aiAnalysis.wordCount,
            extensaoTexto: aiAnalysis.lengthScore,
            coerenciaSemantica: aiAnalysis.semanticsScore,
            significanciaAprendizagem: aiAnalysis.learningScore,
            criticas: formData.criticism,
            sugestoes: formData.suggestion,
            email: formData.studentEmail || ''
        };
    }

    function buildLegacyBackupPayload(formData, scoreData, aiAnalysis, finalScore) {
        return {
            timestamp: new Date().toLocaleString('pt-BR'),
            visitorMode: !!formData.visitorMode,
            serie: formData.studentGrade,
            turma: formData.studentClass,
            coluna: getTermGradeColumn(formData.schoolTerm),
            bimestre: formData.schoolTerm,
            colunaBimestre: getTermGradeColumn(formData.schoolTerm),
            estudante: formData.studentName,
            simulacao: simulationName,
            questoes_puladas: scoreData.skippedQuestions,
            acertos_erros: scoreData.correctAnswers + '/' + (scoreData.totalExercises - scoreData.correctAnswers),
            nota: scoreData.scorePercentage + '%',
            nota_final: finalScore,
            nota_conclusao_ia: aiAnalysis.finalScore,
            conclusao: formData.finalConclusion,
            analise_ia: aiAnalysis.feedback,
            criticas: formData.criticism,
            sugestoes: formData.suggestion,
            email: formData.studentEmail || '',
            to_email: TEACHER_EMAIL,
            nome_aluno: formData.studentName,
            acertos: scoreData.correctAnswers + '/' + scoreData.totalExercises,
            data_envio: new Date().toLocaleString('pt-BR')
        };
    }

    function buildTermGradePayload(formData, scoreData, aiAnalysis, finalScore) {
        const resolvedSheetName = formData.studentSheet
            || (formData.visitorMode ? 'VISITANTE' : resolveSimulationSheetName(formData.studentGrade, formData.studentClass, formData.studentTrail));

        return {
            timestamp: new Date().toISOString(),
            visitorMode: !!formData.visitorMode,
            serie: formData.studentGrade,
            turma: formData.studentClass,
            trilha: formData.studentTrail,
            coluna: getTermGradeColumn(formData.schoolTerm),
            bimestre: formData.schoolTerm,
            colunaBimestre: getTermGradeColumn(formData.schoolTerm),
            acao: 'acumular_nota_bimestral',
            tipoLancamento: 'somar',
            valorLancamento: finalScore,
            estudante: formData.studentName,
            estudanteDigitado: getManualStudentName(),
            sheetName: resolvedSheetName,
            avaliacao: 'Nota Bimestral - ' + simulationName,
            categoria: 'nota-bimestral',
            atividade: simulationName,
            simulacao: simulationName,
            totalSimulacoesAcumuladas: 1,
            nota: finalScore,
            notaExercicios: Number((scoreData.scorePercentage / 10).toFixed(1)),
            notaConclusaoIa: aiAnalysis.finalScore,
            notaPercentual: scoreData.scorePercentage + '%',
            acertos: scoreData.correctAnswers,
            totalQuestoes: scoreData.totalExercises,
            conclusao: formData.finalConclusion,
            palavrasConclusao: aiAnalysis.wordCount,
            extensaoTexto: aiAnalysis.lengthScore,
            coerenciaSemantica: aiAnalysis.semanticsScore,
            significanciaAprendizagem: aiAnalysis.learningScore,
            analiseIa: aiAnalysis.feedback,
            email: formData.studentEmail || ''
        };
    }

    function buildProfessorEmailPayload(formData, scoreData, aiAnalysis, finalScore) {
        return {
            to_email: TEACHER_EMAIL,
            visitorMode: !!formData.visitorMode,
            nome_aluno: formData.studentName,
            serie: formData.studentGrade,
            turma: formData.studentClass,
            simulacao: simulationName,
            nota: scoreData.scorePercentage + '%',
            nota_final: finalScore,
            nota_conclusao_ia: aiAnalysis.finalScore,
            acertos: scoreData.correctAnswers + '/' + scoreData.totalExercises,
            conclusao: formData.finalConclusion,
            analise_ia: aiAnalysis.feedback,
            criticas: formData.criticism,
            sugestoes: formData.suggestion,
            email: formData.studentEmail || '',
            data_envio: new Date().toLocaleString('pt-BR')
        };
    }

    function buildStudentCopyEmailPayload(formData, scoreData, aiAnalysis, finalScore) {
        return {
            to_email: formData.studentEmail,
            visitorMode: !!formData.visitorMode,
            nome_aluno: formData.studentName,
            serie: formData.studentGrade,
            turma: formData.studentClass,
            simulacao: simulationName,
            nota: scoreData.scorePercentage + '%',
            nota_final: finalScore,
            nota_conclusao_ia: aiAnalysis.finalScore,
            acertos: scoreData.correctAnswers + '/' + scoreData.totalExercises,
            conclusao: formData.finalConclusion,
            mensagem: 'Confirmacao de envio - ' + simulationName + '\nNota final: ' + finalScore.toFixed(1) + '\nAcertos: ' + scoreData.correctAnswers + '/' + scoreData.totalExercises
        };
    }

    function postJsonNoCors(url, data) {
        return fetch(url, {
            method: 'POST',
            mode: 'no-cors',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }

    function postJsonWithResponse(url, data) {
        return fetch(url, {
            method: 'POST',
            mode: 'cors',
            headers: { 'Content-Type': 'text/plain;charset=utf-8' },
            body: JSON.stringify(data)
        }).then(function (response) {
            return response.text().then(function (text) {
                let parsed = null;

                try {
                    parsed = text ? JSON.parse(text) : null;
                } catch (error) {
                    parsed = null;
                }

                if (!response.ok) {
                    throw new Error((parsed && parsed.message) || ('HTTP ' + response.status));
                }

                if (parsed && parsed.status === 'error') {
                    throw new Error(parsed.message || 'Erro ao processar o envio na planilha CEAN.');
                }

                return parsed || { status: 'success' };
            });
        });
    }

    function waitMs(durationMs) {
        return new Promise(function (resolve) {
            window.setTimeout(resolve, Math.max(0, Number(durationMs) || 0));
        });
    }

    function randomInt(minValue, maxValue) {
        const min = Math.floor(Number(minValue) || 0);
        const max = Math.floor(Number(maxValue) || 0);
        if (max <= min) {
            return min;
        }
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function getErrorMessage(error) {
        if (!error) {
            return '';
        }
        if (error && error.message) {
            return String(error.message);
        }
        return String(error);
    }

    function isLikelyCorsOrOpaqueRestriction(error) {
        const message = getErrorMessage(error).toLowerCase();
        return message.includes('failed to fetch')
            || message.includes('networkerror')
            || message.includes('load failed')
            || message.includes('cors')
            || message.includes('typeerror');
    }

    function isRetryableEmailError(error) {
        const message = getErrorMessage(error).toLowerCase();
        return message.includes('429')
            || message.includes('quota')
            || message.includes('limit')
            || message.includes('exceeded')
            || message.includes('temporar')
            || message.includes('timeout')
            || message.includes('failed to fetch')
            || message.includes('networkerror')
            || message.includes('load failed')
            || message.includes('503')
            || message.includes('502');
    }

    function postEmailWithFallback(url, data) {
        return postJsonWithResponse(url, data).catch(function (error) {
            if (!isLikelyCorsOrOpaqueRestriction(error)) {
                throw error;
            }
            return postJsonNoCors(url, data).then(function () {
                return { status: 'accepted-opaque' };
            });
        });
    }

    function postEmailWithRetry(url, data, options) {
        const normalizedOptions = options || {};
        const maxAttempts = Math.max(1, Number(normalizedOptions.maxAttempts || 3));
        const baseDelayMs = Math.max(200, Number(normalizedOptions.baseDelayMs || 900));
        const jitterMs = Math.max(0, Number(normalizedOptions.jitterMs || 600));
        const initialJitterMs = Math.max(0, Number(normalizedOptions.initialJitterMs || 0));
        let attempt = 0;

        function tryOnce() {
            attempt += 1;

            return postEmailWithFallback(url, data).catch(function (error) {
                if (attempt >= maxAttempts || !isRetryableEmailError(error)) {
                    throw error;
                }

                const retryDelay = (baseDelayMs * attempt) + randomInt(0, jitterMs);
                return waitMs(retryDelay).then(tryOnce);
            });
        }

        if (initialJitterMs > 0) {
            return waitMs(randomInt(0, initialJitterMs)).then(tryOnce);
        }

        return tryOnce();
    }

    function buildSendJobs(unifiedPayload, legacyPayload, termPayload, professorEmailPayload, studentEmailPayload, options) {
        const normalizedOptions = options || {};
        const isVisitor = !!normalizedOptions.isVisitor;
        const jobs = [];

        jobs.push({
            key: 'cean',
            promise: postJsonWithResponse(PRIMARY_GRADEBOOK_URL, unifiedPayload)
        });

        if (!isVisitor && TERM_GRADEBOOK_URL && TERM_GRADEBOOK_URL !== PRIMARY_GRADEBOOK_URL) {
            jobs.push({
                key: 'term',
                promise: postJsonWithResponse(TERM_GRADEBOOK_URL, termPayload)
            });
        }

        jobs.push({
            key: 'backup',
            promise: postJsonNoCors(LEGACY_BACKUP_URL, legacyPayload)
        });

        const professorEmailPromise = postEmailWithRetry(EMAIL_SCRIPT_URL, professorEmailPayload, {
            maxAttempts: 3,
            baseDelayMs: 1200,
            jitterMs: 800,
            initialJitterMs: 900
        });

        jobs.push({
            key: 'professor-email',
            promise: professorEmailPromise
        });

        if (studentEmailPayload) {
            const studentEmailPromise = professorEmailPromise
                .catch(function () {
                    return null;
                })
                .then(function () {
                    return waitMs(randomInt(350, 1200));
                })
                .then(function () {
                    return postEmailWithRetry(EMAIL_SCRIPT_URL, studentEmailPayload, {
                        maxAttempts: 3,
                        baseDelayMs: 1200,
                        jitterMs: 800,
                        initialJitterMs: 600
                    });
                });

            jobs.push({
                key: 'student-email',
                promise: studentEmailPromise
            });
        }

        return jobs;
    }

    function finalizeSuccessfulSubmissionReset() {
        window.setTimeout(function () {
            if (typeof window.closeExercisesModal === 'function') {
                window.closeExercisesModal();
            } else {
                const exercisesModal = document.getElementById('exercisesModal');
                if (exercisesModal) {
                    exercisesModal.style.display = 'none';
                }
            }

            if (typeof window.resetExerciseState === 'function') {
                window.resetExerciseState();
            } else {
                clearExerciseState();
            }

            updateExerciseLauncherState();
            updateResumeBadge(false);
        }, 2200);
    }

    function enhancedSendResultsToSheet() {
        const resolvedStudentName = getResolvedStudentName();
        const formData = {
            studentName: resolvedStudentName,
            studentSheet: getFieldValue('studentSheet'),
            studentGrade: getFieldValue('studentGrade'),
            studentClass: getFieldValue('studentClass'),
            studentTrail: getFieldValue('studentTrail') || '',
            studentEmail: getFieldValue('studentEmail'),
            visitorName: getFieldValue('visitorName'),
            visitorEmail: getFieldValue('visitorEmail'),
            visitorMode: document.getElementById('visitorMode') ? document.getElementById('visitorMode').checked : false,
            schoolTerm: getFieldValue('schoolTerm'),
            criticism: getFieldValue('criticismInput'),
            suggestion: getFieldValue('suggestionInput'),
            finalConclusion: getFieldValue('finalConclusion')
        };

        const isVisitor = document.getElementById('visitorMode') ? document.getElementById('visitorMode').checked : false;

                if (isVisitor) {
                    if (!formData.visitorName || !formData.finalConclusion) {
                        alert('Preencha o nome e a conclusão antes de enviar.');
                        return;
                    }
                    // Para visitantes, usar valores padrão
                    formData.studentName = formData.visitorName;
                    formData.studentEmail = formData.visitorEmail;
                    formData.studentGrade = 'Visitante';
                    formData.studentClass = 'Visitante';
                    formData.schoolTerm = 'Visitante';
                    formData.studentTrail = 'Visitante';
                    formData.studentSheet = 'VISITANTE';
                } else {
                    if (!isStudentAccessAuthenticated()) {
                        alert('Para enviar como estudante, libere o acesso por senha.');
                        return;
                    }
                    if (!formData.studentName || !formData.studentSheet || !formData.schoolTerm || !formData.finalConclusion) {
                        alert('Preencha nome, turma, bimestre e conclusão antes de enviar.');
                        return;
                    }
                }

        const exercises = Array.isArray(readGlobalBinding('exercises')) ? readGlobalBinding('exercises') : [];
        const exerciseResults = Array.isArray(readGlobalBinding('exerciseResults')) ? readGlobalBinding('exerciseResults') : [];
        const totalExercises = exercises.length;
        const correctAnswers = exerciseResults.filter(function (result) { return result.correct; }).length;
        const skippedQuestions = typeof readGlobalBinding('skippedQuestions') === 'number' ? readGlobalBinding('skippedQuestions') : 0;
        const scorePercentage = totalExercises ? Math.round((correctAnswers / totalExercises) * 100) : 0;
        const aiAnalysis = renderAiPreview(formData.finalConclusion) || analyzeConclusionWithLocalAi(formData.finalConclusion);
        const finalScore = calculateCompositeSimulationScore(scorePercentage, aiAnalysis.finalScore);
        const scoreData = {
            totalExercises: totalExercises,
            correctAnswers: correctAnswers,
            skippedQuestions: skippedQuestions,
            scorePercentage: scorePercentage
        };

        const unifiedPayload = buildUnifiedSimulationPayload(formData, scoreData, aiAnalysis, finalScore);
        const legacyPayload = buildLegacyBackupPayload(formData, scoreData, aiAnalysis, finalScore);
        const termPayload = buildTermGradePayload(formData, scoreData, aiAnalysis, finalScore);
        const professorEmailPayload = buildProfessorEmailPayload(formData, scoreData, aiAnalysis, finalScore);
        const studentEmailPayload = formData.studentEmail ? buildStudentCopyEmailPayload(formData, scoreData, aiAnalysis, finalScore) : null;

        const emailStatus = document.getElementById('emailStatus');
        const sendButton = document.getElementById('sendResults');
        if (emailStatus) {
            emailStatus.style.display = 'block';
            emailStatus.textContent = 'Enviando dados para as planilhas...';
            emailStatus.className = 'email-status sending';
        }
        if (sendButton) {
            sendButton.disabled = true;
            sendButton.textContent = 'Enviando...';
        }

        const sendJobs = buildSendJobs(
            unifiedPayload,
            legacyPayload,
            termPayload,
            professorEmailPayload,
            studentEmailPayload,
            { isVisitor: isVisitor }
        );

        Promise.allSettled(sendJobs.map(function (job) {
            return job.promise;
        }))
            .then(function (results) {
                const successfulTargets = [];
                const successfulResultsByKey = {};
                const rejectedResultsByKey = {};
                const warningMessages = [];

                function getFailureMessage(reason, fallbackMessage) {
                    if (reason && reason.message) {
                        return reason.message;
                    }

                    if (typeof reason === 'string' && reason.trim()) {
                        return reason;
                    }

                    return fallbackMessage;
                }

                results.forEach(function (result, index) {
                    const key = sendJobs[index].key;
                    if (result.status !== 'fulfilled') {
                        rejectedResultsByKey[key] = result.reason;
                        return;
                    }

                    successfulTargets.push(key);
                    successfulResultsByKey[key] = result.value;
                });

                const ceanSucceeded = successfulTargets.indexOf('cean') !== -1;
                const backupSucceeded = successfulTargets.indexOf('backup') !== -1;
                const termSucceeded = successfulTargets.indexOf('term') !== -1;
                const professorEmailSucceeded = successfulTargets.indexOf('professor-email') !== -1;
                const studentEmailRequested = !!studentEmailPayload;
                const studentEmailSucceeded = successfulTargets.indexOf('student-email') !== -1;

                if (!ceanSucceeded && !backupSucceeded) {
                    const ceanReason = rejectedResultsByKey.cean;
                    const backupReason = rejectedResultsByKey.backup;
                    const ceanMessage = ceanReason && ceanReason.message
                        ? ceanReason.message
                        : String(ceanReason || 'A planilha CEAN nao confirmou o recebimento deste envio.');
                    const backupMessage = backupReason && backupReason.message
                        ? backupReason.message
                        : String(backupReason || 'A planilha de seguranca nao confirmou o recebimento deste envio.');
                    throw new Error('Falha no envio principal e no backup. CEAN: ' + ceanMessage + ' | Backup: ' + backupMessage);
                }

                if (!termSucceeded && rejectedResultsByKey.term) {
                    warningMessages.push('Lancamento no diario trimestral nao foi confirmado nesta tentativa.');
                }

                if (!professorEmailSucceeded && rejectedResultsByKey['professor-email']) {
                    warningMessages.push('E-mail ao professor nao foi confirmado: ' + getFailureMessage(rejectedResultsByKey['professor-email'], 'tente novamente em instantes.'));
                }

                if (studentEmailRequested && !studentEmailSucceeded) {
                    warningMessages.push('Copia para o e-mail do aluno nao foi confirmada: ' + getFailureMessage(rejectedResultsByKey['student-email'], 'o servico pode estar temporariamente com limite de envios.'));
                }

                if (emailStatus) {
                    const sentToBackup = backupSucceeded;
                    const ceanResult = successfulResultsByKey.cean || {};
                    const ceanLocation = ceanResult.sheet && ceanResult.row
                        ? ' Aba ' + ceanResult.sheet + ', linha ' + ceanResult.row + '.'
                        : '';
                    if (ceanSucceeded) {
                        emailStatus.textContent = sentToBackup
                            ? '✅ CEAN confirmou o recebimento.' + ceanLocation + ' Backup tambem enviado.'
                            : '✅ CEAN confirmou o recebimento.' + ceanLocation;
                    } else {
                        emailStatus.textContent = '⚠ CEAN nao confirmou o envio nesta tentativa, mas a planilha de seguranca recebeu os dados.';
                    }

                    if (warningMessages.length) {
                        emailStatus.textContent += ' ⚠ ' + warningMessages.join(' ');
                        emailStatus.className = 'email-status warning-status';
                    } else if (ceanSucceeded) {
                        emailStatus.className = 'email-status sent';
                    } else {
                        emailStatus.className = 'email-status warning-status';
                    }
                }
                if (sendButton) {
                    sendButton.disabled = false;
                    sendButton.textContent = 'Enviar Resultados';
                }
                finalizeSuccessfulSubmissionReset();
            })
            .catch(function (error) {
                if (emailStatus) {
                    emailStatus.textContent = '❌ Erro ao enviar: ' + (error && error.message ? error.message : 'Tente novamente.');
                    emailStatus.className = 'email-status error-status';
                }
                if (sendButton) {
                    sendButton.disabled = false;
                    sendButton.textContent = 'Enviar Resultados';
                }
            });
    }

            window.__simulationEnhancerSendResults = enhancedSendResultsToSheet;

    function setupDelegatedSendHandler() {
        if (!document.body || document.body.dataset.enhancerSendBound === 'true') {
            return;
        }

        document.addEventListener('click', function (event) {
            const sendButton = event.target.closest('#sendResults');
            if (!sendButton) {
                return;
            }

            event.preventDefault();
            event.stopImmediatePropagation();
            enhancedSendResultsToSheet();
        }, true);

        document.body.dataset.enhancerSendBound = 'true';
    }

    function escapeHtml(text) {
        return String(text || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
})();
