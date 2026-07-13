const STUDENT_DATABASE = {
    "bySheet": {
        "2o ano A": [
            ""
        ],
        "2o ano B": [
            ""
        ],
        "3o ano A": [
            ""
        ],
        "3o ano B": [
            ""
        ],
        "3o ano C": [
            ""
        ],
        "3o ano D": [
            ""
        ],
        "3o ano G": [
            "ALUNO TESTE"
        ],
        "PCA - Educação Digital 3o ano E": [
            ""
        ],
        "PCA - Educação Digital 3o ano G": [
            ""
        ],
        "Sustentabilidade 2o ano C": [
            ""
        ]
    },
    "bySerieTurma": {
        "2o ano|A": [
            ""
        ],
        "2o ano|B": [
            ""
        ],
        "3o ano|A": [
            ""
        ],
        "3o ano|B": [
            ""
        ],
        "3o ano|C": [
            ""
        ],
        "3o ano|D": [
            ""
        ],
        "3o ano|G": [
            ""
        ],
        "3o ano|E": [
            ""
        ],
        "2o ano|C": [
            ""
        ]
    },
    "byTrilha": {
        "PCA - Educação Digital 3o ano E": [
            ""
        ],
        "PCA - Educação Digital 3o ano G": [
            ""
        ],
        "Sustentabilidade 2o ano C": [
            ""
        ]
    },
    "accessControl": {
        "enabled": true,
        "salt": "EDU-DIGITAL-2026",
        "passwordHash": "0e71f1560760cf5cc90d84c76c5028354b4d2366d8841144d34b1fa4b6dacb60",
        "hint": "Solicite ao professor a senha de acesso do estudante."
    }
};

if (typeof window !== 'undefined') {
    window.STUDENT_DATABASE = STUDENT_DATABASE;
}
