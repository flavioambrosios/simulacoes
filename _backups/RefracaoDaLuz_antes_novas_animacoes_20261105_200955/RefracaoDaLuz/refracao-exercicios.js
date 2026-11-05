(function (root) {
    'use strict';

    const variants = [
        [20, 30, 40, 50],
        [2.4, 2, 1.5],
        [1.2, 1.5, 2],
        [
            { from: 'ar', n1: 1, to: 'água', n2: 1.33, angle: 30 },
            { from: 'água', n1: 1.33, to: 'vidro', n2: 1.5, angle: 40 },
            { from: 'vidro', n1: 1.5, to: 'ar', n2: 1, angle: 25 },
            { from: 'água', n1: 1.33, to: 'ar', n2: 1, angle: 30 }
        ],
        [
            { n1: 1, n2: 1.5 },
            { n1: 1.5, n2: 1 },
            { n1: 1, n2: 2 },
            { n1: 1.2, n2: 1.5 }
        ],
        [
            { incident: 0.6, refracted: 0.4 },
            { incident: 0.8, refracted: 0.4 },
            { incident: 0.5, refracted: 0.4 }
        ],
        [
            { wavelength: 600, n: 1.5 },
            { wavelength: 540, n: 1.5 },
            { wavelength: 500, n: 1.25 },
            { wavelength: 600, n: 2 }
        ],
        [4, 5, 6],
        [
            { from: 'vidro', n1: 1.5, critical: 41.8, angle: 50 },
            { from: 'vidro', n1: 1.5, critical: 41.8, angle: 30 },
            { from: 'água', n1: 1.33, critical: 48.8, angle: 60 },
            { from: 'água', n1: 1.33, critical: 48.8, angle: 35 }
        ],
        [
            { first: 'vermelha', n1: 1.5, second: 'violeta', n2: 1.53, angle: 30 },
            { first: 'azul', n1: 1.52, second: 'vermelha', n2: 1.49, angle: 40 },
            { first: 'vermelha', n1: 1.48, second: 'violeta', n2: 1.51, angle: 20 }
        ]
    ];

    const sessionId = Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    let nextQuestionId = 0;

    function formatNumber(value, digits = 2) {
        return new Intl.NumberFormat('pt-BR', { maximumFractionDigits: digits }).format(value);
    }

    function fromMedium(name) {
        return name === 'água' ? 'da água' : 'do ' + name;
    }

    function toMedium(name) {
        return name === 'água' ? 'para a água' : 'para o ' + name;
    }

    function buildQuestion(type, data) {
        const format = formatNumber;
        switch (type) {
            case 0: {
                const answer = (90 - data) + '°';
                return {
                    question: `Um raio forma ${data}° com a superfície que separa dois meios. Qual é seu ângulo de incidência, medido em relação à normal?`,
                    answer,
                    wrong: [data + '°', '90°', '0°'],
                    explanation: `A normal é perpendicular à superfície. Assim, o ângulo de incidência é 90° − ${data}° = ${answer}.`
                };
            }
            case 1: {
                const n = 3 / data;
                return {
                    question: `Em um meio, a velocidade da luz é ${format(data)} × 10⁸ m/s. Usando c = 3 × 10⁸ m/s, qual é o índice de refração desse meio?`,
                    answer: format(n),
                    wrong: [format(data / 3), format(data), '3'],
                    explanation: `Pela relação n = c/v, n = 3/${format(data)} = ${format(n)}. O índice de refração não tem unidade.`
                };
            }
            case 2: {
                const speed = 3 / data;
                const speedText = value => format(value) + ' × 10⁸ m/s';
                return {
                    question: `Um meio tem índice de refração n = ${format(data)}. Se c = 3 × 10⁸ m/s, qual é a velocidade da luz nesse meio?`,
                    answer: speedText(speed),
                    wrong: [speedText(3), speedText(data), speedText(3 * data)],
                    explanation: `De n = c/v, obtemos v = c/n = 3/${format(data)} × 10⁸ = ${speedText(speed)}.`
                };
            }
            case 3: {
                const closer = 'Aproxima-se da normal.';
                const farther = 'Afasta-se da normal.';
                const increases = data.n2 > data.n1;
                return {
                    question: `Um raio passa ${fromMedium(data.from)} (n = ${format(data.n1)}) ${toMedium(data.to)} (n = ${format(data.n2)}), com incidência de ${data.angle}° em relação à normal. Sabendo que existe raio refratado, como ele se comporta?`,
                    answer: increases ? closer : farther,
                    wrong: [increases ? farther : closer, 'Segue exatamente sobre a normal.', 'Mantém a mesma velocidade do meio inicial.'],
                    explanation: increases
                        ? 'Ao entrar em um meio de maior índice, a luz diminui sua velocidade e o raio refratado se aproxima da normal.'
                        : 'Ao entrar em um meio de menor índice, a luz aumenta sua velocidade e o raio refratado se afasta da normal.'
                };
            }
            case 4: {
                const angle = Math.asin(data.n1 * 0.5 / data.n2) * 180 / Math.PI;
                const answer = format(angle, 1) + '°';
                return {
                    question: `A luz passa de um meio com n₁ = ${format(data.n1)} para outro com n₂ = ${format(data.n2)}. O ângulo de incidência é 30° e sen 30° = 0,5. Pela Lei de Snell, qual é o ângulo de refração em relação à normal? Arredonde para uma casa decimal.`,
                    answer,
                    wrong: ['30°', '0°', '90°'],
                    explanation: `Pela Lei de Snell, sen θ₂ = n₁ sen 30°/n₂ = ${format(data.n1)} × 0,5/${format(data.n2)}. Portanto, θ₂ ≈ ${answer}.`
                };
            }
            case 5: {
                const answer = format(data.incident / data.refracted);
                return {
                    question: `Um raio passa do ar (n₁ = 1) para outro meio. Foram medidos sen θ₁ = ${format(data.incident)} e sen θ₂ = ${format(data.refracted)}, com ângulos em relação à normal. Qual é o índice n₂?`,
                    answer,
                    wrong: ['1,25', '1,5', '2', '3'].filter(option => option !== answer),
                    explanation: `De n₁ sen θ₁ = n₂ sen θ₂, resulta n₂ = ${format(data.incident)}/${format(data.refracted)} = ${answer}.`
                };
            }
            case 6: {
                const wavelength = data.wavelength / data.n;
                const wavelengthText = value => format(value, 1) + ' nm';
                return {
                    question: `No vácuo, uma luz monocromática tem comprimento de onda de ${data.wavelength} nm. Ao entrar em um meio de índice ${format(data.n)}, qual é seu comprimento de onda? Arredonde para uma casa decimal, se necessário.`,
                    answer: wavelengthText(wavelength),
                    wrong: [
                        wavelengthText(data.wavelength),
                        wavelengthText(data.wavelength * data.n),
                        wavelengthText(data.wavelength / (data.n * data.n))
                    ],
                    explanation: `A frequência permanece constante; como v = fλ e v = c/n, λ = λ₀/n = ${data.wavelength}/${format(data.n)} = ${wavelengthText(wavelength)}.`
                };
            }
            case 7: {
                const frequencyText = value => format(value) + ' × 10¹⁴ Hz';
                return {
                    question: `Uma luz monocromática de frequência ${frequencyText(data)} passa do ar para o vidro. Qual é sua frequência no vidro?`,
                    answer: frequencyText(data),
                    wrong: [frequencyText(data / 2), frequencyText(data * 2), '0 Hz'],
                    explanation: 'A frequência é determinada pela fonte e permanece a mesma na passagem de um meio para outro; a velocidade e o comprimento de onda mudam.'
                };
            }
            case 8: {
                const total = 'Ocorre reflexão interna total; não há raio refratado propagante.';
                const refracted = 'Há raio refratado; não ocorre reflexão interna total.';
                const isTotal = data.angle > data.critical;
                return {
                    question: `A luz passa ${fromMedium(data.from)} (n₁ = ${format(data.n1)}) para o ar (n₂ = 1). O ângulo crítico é aproximadamente ${format(data.critical, 1)}° e o ângulo de incidência é ${data.angle}°. O que acontece?`,
                    answer: isTotal ? total : refracted,
                    wrong: [
                        isTotal ? refracted : total,
                        'A frequência da luz se torna zero.',
                        'A reflexão interna total acontece em qualquer ângulo.'
                    ],
                    explanation: `A luz vai do maior para o menor índice. Como ${data.angle}° é ${isTotal ? 'maior' : 'menor'} que o ângulo crítico de ${format(data.critical, 1)}°, ${isTotal ? 'ocorre reflexão interna total' : 'existe raio refratado e não ocorre reflexão interna total'}.`
                };
            }
            case 9: {
                const first = `A luz ${data.first}.`;
                const second = `A luz ${data.second}.`;
                const firstHasGreaterIndex = data.n1 > data.n2;
                return {
                    question: `Em um prisma, o índice para a luz ${data.first} é ${format(data.n1)} e para a luz ${data.second} é ${format(data.n2)}. Ambas entram do ar com o mesmo ângulo de incidência de ${data.angle}°. Qual fica mais próxima da normal dentro do prisma?`,
                    answer: firstHasGreaterIndex ? first : second,
                    wrong: [
                        firstHasGreaterIndex ? second : first,
                        'Ambas têm o mesmo ângulo refratado.',
                        'Nenhuma das luzes é refratada.'
                    ],
                    explanation: `Para a mesma incidência, a luz com maior índice no prisma apresenta menor ângulo de refração. A dependência do índice com o comprimento de onda está relacionada à dispersão.`
                };
            }
            default:
                throw new RangeError('Tipo de exercício desconhecido.');
        }
    }

    function shuffle(values, random) {
        const result = values.slice();
        for (let index = result.length - 1; index > 0; index--) {
            const other = Math.floor(random() * (index + 1));
            [result[index], result[other]] = [result[other], result[index]];
        }
        return result;
    }

    function createExercise(type, previousVariant = -1, random = Math.random) {
        if (!Number.isInteger(type) || !variants[type]) {
            throw new RangeError('Tipo de exercício desconhecido.');
        }

        const available = variants[type].map((_, index) => index).filter(index => index !== previousVariant);
        const variantIndex = available[Math.floor(random() * available.length)];
        const question = buildQuestion(type, variants[type][variantIndex]);
        const options = [question.answer, ...question.wrong];
        if (options.length !== 4 || new Set(options).size !== 4) {
            throw new Error('O exercício deve ter quatro alternativas distintas.');
        }

        return {
            type,
            variantIndex,
            id: sessionId + '-' + (++nextQuestionId),
            question: question.question,
            answer: question.answer,
            explanation: question.explanation,
            options: shuffle(options, random),
            status: 'unanswered',
            selectedValue: ''
        };
    }

    function createExercises() {
        return variants.map((_, type) => createExercise(type));
    }

    const api = {
        createExercise,
        createExercises,
        variantCounts: variants.map(items => items.length)
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    } else {
        root.RefractionExercises = api;
    }
})(globalThis);
