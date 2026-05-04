from __future__ import annotations

from pathlib import Path
import csv

from database import (
    connect_database,
    export_results_csv,
    get_gradebook_report,
    get_gradebook_student_summary,
    initialize_database,
    sync_simulations_to_gradebook,
    upsert_gradebook_item,
    upsert_gradebook_score,
    upsert_student,
)


ITEM_REQUIRED_COLUMNS = {'categoria', 'atividade', 'bimestre'}
SCORE_REQUIRED_COLUMNS = {'estudante', 'turma', 'categoria', 'atividade', 'nota', 'bimestre'}


def import_gradebook_items(database_path: Path, input_csv: Path) -> dict:
    initialize_database(database_path)
    count = 0

    with input_csv.open('r', encoding='utf-8-sig', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        headers = {header.strip().lower() for header in (reader.fieldnames or [])}
        missing = ITEM_REQUIRED_COLUMNS - headers
        if missing:
            raise ValueError(f'CSV de componentes inválido. Faltam: {", ".join(sorted(missing))}')

        with connect_database(database_path) as connection:
            for raw_row in reader:
                row = normalize_row(raw_row)
                upsert_gradebook_item(
                    connection,
                    nome=row['atividade'],
                    categoria=row['categoria'],
                    bimestre=row['bimestre'],
                    recuperacao=to_bool(row.get('recuperacao', '')),
                    peso=to_float(row.get('peso', ''), 1.0),
                    nota_maxima=to_float(row.get('nota_maxima', ''), 10.0),
                    turma=row.get('turma') or None,
                    origem=row.get('origem') or 'csv_componentes'
                )
                count += 1
            connection.commit()

    return {'componentes_importados': count, 'banco_sqlite': str(database_path)}


def import_gradebook_scores(database_path: Path, input_csv: Path) -> dict:
    initialize_database(database_path)
    count = 0

    with input_csv.open('r', encoding='utf-8-sig', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        headers = {header.strip().lower() for header in (reader.fieldnames or [])}
        missing = SCORE_REQUIRED_COLUMNS - headers
        if missing:
            raise ValueError(f'CSV de notas inválido. Faltam: {", ".join(sorted(missing))}')

        with connect_database(database_path) as connection:
            for raw_row in reader:
                row = normalize_row(raw_row)
                student_id = upsert_student(connection, row['estudante'], row['turma'])
                item_id = upsert_gradebook_item(
                    connection,
                    nome=row['atividade'],
                    categoria=row['categoria'],
                    bimestre=row['bimestre'],
                    recuperacao=to_bool(row.get('recuperacao', '')),
                    peso=to_float(row.get('peso', ''), 1.0),
                    nota_maxima=to_float(row.get('nota_maxima', ''), 10.0),
                    turma=row.get('turma') or None,
                    origem=row.get('origem') or 'csv_notas'
                )
                upsert_gradebook_score(
                    connection,
                    student_id=student_id,
                    item_id=item_id,
                    nota=to_float(row['nota'], 0.0),
                    observacoes=row.get('observacoes') or None
                )
                count += 1
            connection.commit()

    return {'notas_importadas': count, 'banco_sqlite': str(database_path)}


def sync_gradebook_simulations(database_path: Path, bimestre: str, turma: str | None = None) -> dict:
    initialize_database(database_path)
    with connect_database(database_path) as connection:
        synced = sync_simulations_to_gradebook(connection, bimestre, turma)
        connection.commit()
    return {'registros_sincronizados': synced, 'bimestre': bimestre, 'banco_sqlite': str(database_path)}


def export_gradebook_report(
    database_path: Path,
    bimestre: str,
    output_csv: Path,
    turma: str | None = None,
    estudante: str | None = None,
) -> dict:
    initialize_database(database_path)
    with connect_database(database_path) as connection:
        rows = get_gradebook_report(connection, bimestre, turma=turma, estudante=estudante)
    export_results_csv(rows, output_csv)
    return {'linhas_exportadas': len(rows), 'arquivo_saida': str(output_csv)}


def get_consolidated_student_summary(database_path: Path, estudante: str, bimestre: str, turma: str | None = None) -> dict | None:
    initialize_database(database_path)
    with connect_database(database_path) as connection:
        return get_gradebook_student_summary(connection, estudante, bimestre, turma)


def normalize_row(raw_row: dict[str, str]) -> dict[str, str]:
    return {key.strip().lower(): (value or '').strip() for key, value in raw_row.items()}


def to_float(value: str, default: float) -> float:
    text = str(value or '').strip()
    if not text:
        return default
    return float(text.replace(',', '.'))


def to_bool(value: str) -> bool:
    return str(value or '').strip().lower() in {'1', 'sim', 'true', 'verdadeiro', 's'}