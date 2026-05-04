from __future__ import annotations

import re
import unicodedata


GENERIC_PHRASES = [
    'aprendi que e importante',
    'aprendi que e muito importante',
    'foi legal aprender',
    'gostei muito da simulacao',
    'foi muito interessante',
    'isso e importante para a vida',
    'essa atividade foi importante',
    'eu aprendi bastante',
    'foi uma experiencia muito boa'
]


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize('NFD', text.lower())
    normalized = ''.join(char for char in normalized if unicodedata.category(char) != 'Mn')
    return re.sub(r'\s+', ' ', normalized).strip()


def word_count(text: str) -> int:
    return len(re.findall(r'\b\w+\b', text, flags=re.UNICODE))


def score_word_count(total_words: int) -> float:
    if total_words <= 0:
        return 0.0
    if total_words >= 80:
        return 10.0
    return round((total_words / 80) * 10, 1)


def score_originality(text: str) -> float:
    normalized = normalize_text(text)
    total_words = word_count(text)

    if total_words == 0:
        return 0.0

    score = 10.0

    for phrase in GENERIC_PHRASES:
        if phrase in normalized:
            score -= 1.3

    unique_words = {word for word in re.findall(r'\b\w+\b', normalized) if len(word) > 2}
    lexical_diversity = len(unique_words) / max(total_words, 1)

    if total_words < 18:
        score -= 2.0
    elif total_words < 30:
        score -= 1.0

    if lexical_diversity < 0.38:
        score -= 2.0
    elif lexical_diversity < 0.5:
        score -= 1.0

    if normalized.count('muito') >= 3:
        score -= 0.7

    return round(max(0.0, min(10.0, score)), 1)