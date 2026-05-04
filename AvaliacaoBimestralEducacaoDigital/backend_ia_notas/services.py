from __future__ import annotations

from pathlib import Path
import csv

from ai_client import AIClient
from database import (
    calculate_student_average,
    connect_database,
    export_results_csv,
    initialize_database,
    insert_simulation_record,
    list_students,
    upsert_conclusion_evaluation,
    upsert_student,
)
from heuristics import score_originality, score_word_count, word_count


REQUIRED_COLUMNS = {'estudante', 'turma', 'simulacao', 'nota', 'conclusao'}
WEIGHTS = {
    'score_words': 0.10,
    'score_coherence': 0.30,
    'score_originality': 0.30,
    'score_significance': 0.30,
}


class EvaluationService:
    def __init__(self, database_path: Path, ai_client: AIClient) -> None:
        self.database_path = database_path
        self.ai_client = ai_client

    def evaluate_csv(self, input_csv: Path, output_csv: Path | None = None) -> dict:
        initialize_database(self.database_path)

        with input_csv.open('r', encoding='utf-8-sig', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            headers = {header.strip().lower() for header in (reader.fieldnames or [])}
            missing = REQUIRED_COLUMNS - headers
            if missing:
                missing_columns = ', '.join(sorted(missing))
                raise ValueError(f'CSV inválido. Faltam as colunas: {missing_columns}')

            exported_rows = []
            total_rows = 0

            with connect_database(self.database_path) as connection:
                for raw_row in reader:
                    row = {key.strip().lower(): (value or '').strip() for key, value in raw_row.items()}
                    total_rows += 1
                    result = self.evaluate_row(row)

                    student_id = upsert_student(connection, row['estudante'], row['turma'])
                    record_id = insert_simulation_record(
                        connection,
                        student_id,
                        row['simulacao'],
                        float(str(row['nota']).replace(',', '.')),
                        row['conclusao'],
                        str(input_csv)
                    )
                    upsert_conclusion_evaluation(connection, record_id, result)

                    exported_rows.append({
                        'estudante': row['estudante'],
                        'turma': row['turma'],
                        'simulacao': row['simulacao'],
                        'nota_simulacao': row['nota'],
                        'palavras': result['word_count'],
                        'nota_palavras': result['score_words'],
                        'nota_coerencia': result['score_coherence'],
                        'nota_originalidade': result['score_originality'],
                        'nota_significancia': result['score_significance'],
                        'nota_final_conclusao': result['final_score'],
                        'feedback_ia': result['feedback'],
                    })

                connection.commit()

        if output_csv:
            export_results_csv(exported_rows, output_csv)

        return {
            'linhas_processadas': total_rows,
            'arquivo_saida': str(output_csv) if output_csv else '',
            'banco_sqlite': str(self.database_path)
        }

    def evaluate_row(self, row: dict[str, str]) -> dict:
        conclusion = row['conclusao']
        total_words = word_count(conclusion)
        words_score = score_word_count(total_words)
        originality_score = score_originality(conclusion)
        ai_result = self.ai_client.evaluate_conclusion(
            conclusion,
            {
                'estudante': row['estudante'],
                'turma': row['turma'],
                'simulacao': row['simulacao'],
                'nota': row['nota'],
            }
        )

        result = {
            'word_count': total_words,
            'score_words': words_score,
            'score_coherence': ai_result['coerencia'],
            'score_originality': originality_score,
            'score_significance': ai_result['significancia'],
            'feedback': ai_result['comentario'],
        }
        result['final_score'] = weighted_average(result)
        return result


def weighted_average(result: dict) -> float:
    final_score = (
        result['score_words'] * WEIGHTS['score_words']
        + result['score_coherence'] * WEIGHTS['score_coherence']
        + result['score_originality'] * WEIGHTS['score_originality']
        + result['score_significance'] * WEIGHTS['score_significance']
    )
    return round(final_score, 2)


def get_student_average(database_path: Path, estudante: str, turma: str | None = None) -> dict | None:
    initialize_database(database_path)
    with connect_database(database_path) as connection:
        return calculate_student_average(connection, estudante, turma)


def get_student_roster(database_path: Path, turma: str | None = None) -> list[dict]:
    initialize_database(database_path)
    with connect_database(database_path) as connection:
        return list_students(connection, turma)