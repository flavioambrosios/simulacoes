const test = require('node:test');
const assert = require('node:assert/strict');
const bank = require('./refracao-exercicios.js');

function exerciseForVariant(type, variant) {
    const count = bank.variantCounts[type];
    return bank.createExercise(type, -1, () => (variant + 0.1) / count);
}

test('a atividade tem dez questões com alternativas únicas e repetição com dados diferentes', () => {
    assert.equal(bank.createExercises().length, 10);
    assert.equal(bank.variantCounts.length, 10);

    bank.variantCounts.forEach((count, type) => {
        assert.ok(count >= 3);
        for (let variant = 0; variant < count; variant++) {
            const exercise = exerciseForVariant(type, variant);
            assert.equal(exercise.variantIndex, variant);
            assert.equal(exercise.options.length, 4);
            assert.equal(new Set(exercise.options).size, 4);
            assert.equal(exercise.options.filter(option => option === exercise.answer).length, 1);
            assert.ok(exercise.question && exercise.explanation);

            const retry = bank.createExercise(type, exercise.variantIndex, () => 0);
            assert.equal(retry.type, exercise.type);
            assert.notEqual(retry.variantIndex, exercise.variantIndex);
            assert.notEqual(retry.question, exercise.question);
            assert.notEqual(retry.id, exercise.id);
        }
    });
});

test('respostas numéricas e conceituais de todas as variantes correspondem aos valores esperados', () => {
    const total = 'Ocorre reflexão interna total; não há raio refratado propagante.';
    const refracted = 'Há raio refratado; não ocorre reflexão interna total.';
    const expected = [
        ['70°', '60°', '50°', '40°'],
        ['1,25', '1,5', '2'],
        ['2,5 × 10⁸ m/s', '2 × 10⁸ m/s', '1,5 × 10⁸ m/s'],
        ['Aproxima-se da normal.', 'Aproxima-se da normal.', 'Afasta-se da normal.', 'Afasta-se da normal.'],
        ['19,5°', '48,6°', '14,5°', '23,6°'],
        ['1,5', '2', '1,25'],
        ['400 nm', '360 nm', '400 nm', '300 nm'],
        ['4 × 10¹⁴ Hz', '5 × 10¹⁴ Hz', '6 × 10¹⁴ Hz'],
        [total, refracted, total, refracted],
        ['A luz violeta.', 'A luz azul.', 'A luz violeta.']
    ];

    expected.forEach((answers, type) => {
        assert.equal(answers.length, bank.variantCounts[type]);
        answers.forEach((answer, variant) => {
            assert.equal(exerciseForVariant(type, variant).answer, answer, `questão ${type + 1}, variante ${variant + 1}`);
        });
    });
});

test('rejeita tipos de questão inexistentes', () => {
    assert.throws(() => bank.createExercise(-1), RangeError);
    assert.throws(() => bank.createExercise(10), RangeError);
});
