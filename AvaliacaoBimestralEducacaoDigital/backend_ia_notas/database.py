from __future__ import annotations

from datetime import datetime
from pathlib import Path
import csv
import sqlite3


def connect_database(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with connect_database(database_path) as connection:
        connection.executescript(
            '''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudante TEXT NOT NULL,
                turma TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(estudante, turma)
            );

            CREATE TABLE IF NOT EXISTS simulation_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                simulacao TEXT NOT NULL,
                nota REAL NOT NULL,
                conclusao TEXT,
                source_file TEXT,
                imported_at TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS conclusion_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_record_id INTEGER NOT NULL UNIQUE,
                word_count INTEGER NOT NULL,
                score_words REAL NOT NULL,
                score_coherence REAL NOT NULL,
                score_originality REAL NOT NULL,
                score_significance REAL NOT NULL,
                final_score REAL NOT NULL,
                feedback TEXT,
                evaluated_at TEXT NOT NULL,
                FOREIGN KEY(simulation_record_id) REFERENCES simulation_records(id)
            );

            CREATE TABLE IF NOT EXISTS gradebook_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                bimestre TEXT NOT NULL,
                recuperacao INTEGER NOT NULL DEFAULT 0,
                peso REAL NOT NULL DEFAULT 1,
                nota_maxima REAL NOT NULL DEFAULT 10,
                turma TEXT,
                origem TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(nome, categoria, bimestre, turma)
            );

            CREATE TABLE IF NOT EXISTS gradebook_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                nota REAL NOT NULL,
                observacoes TEXT,
                lancado_em TEXT NOT NULL,
                UNIQUE(student_id, item_id),
                FOREIGN KEY(student_id) REFERENCES students(id),
                FOREIGN KEY(item_id) REFERENCES gradebook_items(id)
            );
            '''
        )
        ensure_gradebook_schema(connection)


def ensure_gradebook_schema(connection: sqlite3.Connection) -> None:
    columns = {
        row['name']
        for row in connection.execute('PRAGMA table_info(gradebook_items)').fetchall()
    }

    if 'recuperacao' not in columns:
        connection.execute(
            'ALTER TABLE gradebook_items ADD COLUMN recuperacao INTEGER NOT NULL DEFAULT 0'
        )


def upsert_student(connection: sqlite3.Connection, estudante: str, turma: str) -> int:
    timestamp = datetime.utcnow().isoformat()
    connection.execute(
        '''
        INSERT INTO students (estudante, turma, created_at)
        VALUES (?, ?, ?)
        ON CONFLICT(estudante, turma) DO NOTHING
        ''',
        (estudante, turma, timestamp)
    )
    row = connection.execute(
        'SELECT id FROM students WHERE estudante = ? AND turma = ?',
        (estudante, turma)
    ).fetchone()
    return int(row['id'])


def insert_simulation_record(
    connection: sqlite3.Connection,
    student_id: int,
    simulacao: str,
    nota: float,
    conclusao: str,
    source_file: str
) -> int:
    cursor = connection.execute(
        '''
        INSERT INTO simulation_records (student_id, simulacao, nota, conclusao, source_file, imported_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (student_id, simulacao, nota, conclusao, source_file, datetime.utcnow().isoformat())
    )
    return int(cursor.lastrowid)


def upsert_conclusion_evaluation(connection: sqlite3.Connection, simulation_record_id: int, result: dict) -> None:
    connection.execute(
        '''
        INSERT INTO conclusion_evaluations (
            simulation_record_id,
            word_count,
            score_words,
            score_coherence,
            score_originality,
            score_significance,
            final_score,
            feedback,
            evaluated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(simulation_record_id) DO UPDATE SET
            word_count = excluded.word_count,
            score_words = excluded.score_words,
            score_coherence = excluded.score_coherence,
            score_originality = excluded.score_originality,
            score_significance = excluded.score_significance,
            final_score = excluded.final_score,
            feedback = excluded.feedback,
            evaluated_at = excluded.evaluated_at
        ''',
        (
            simulation_record_id,
            result['word_count'],
            result['score_words'],
            result['score_coherence'],
            result['score_originality'],
            result['score_significance'],
            result['final_score'],
            result['feedback'],
            datetime.utcnow().isoformat()
        )
    )


def export_results_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text('', encoding='utf-8')
        return

    with output_path.open('w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def calculate_student_average(connection: sqlite3.Connection, estudante: str, turma: str | None = None) -> dict | None:
    params: list = [estudante]
    turma_filter = ''
    if turma:
        turma_filter = 'AND s.turma = ?'
        params.append(turma)

    rows = connection.execute(
        f'''
        SELECT
            s.estudante,
            s.turma,
            sr.simulacao,
            sr.nota AS nota_simulacao,
            ce.final_score AS nota_conclusao
        FROM students s
        JOIN simulation_records sr ON sr.student_id = s.id
        LEFT JOIN conclusion_evaluations ce ON ce.simulation_record_id = sr.id
        WHERE s.estudante = ? {turma_filter}
        ORDER BY s.turma, sr.simulacao
        ''',
        params
    ).fetchall()

    if not rows:
        return None

    notas_simulacao = [float(row['nota_simulacao']) for row in rows]
    notas_conclusao = [float(row['nota_conclusao']) for row in rows if row['nota_conclusao'] is not None]
    notas_integradas = []

    for row in rows:
        componentes = [float(row['nota_simulacao'])]
        if row['nota_conclusao'] is not None:
            componentes.append(float(row['nota_conclusao']))
        notas_integradas.append(sum(componentes) / len(componentes))

    return {
        'estudante': rows[0]['estudante'],
        'turma': rows[0]['turma'],
        'media_simulacoes': round(sum(notas_simulacao) / len(notas_simulacao), 2),
        'media_conclusoes': round(sum(notas_conclusao) / len(notas_conclusao), 2) if notas_conclusao else None,
        'media_geral': round(sum(notas_integradas) / len(notas_integradas), 2),
        'quantidade_registros': len(rows)
    }


def list_students(connection: sqlite3.Connection, turma: str | None = None) -> list[dict]:
    if turma:
        rows = connection.execute(
            'SELECT estudante, turma FROM students WHERE turma = ? ORDER BY estudante',
            (turma,)
        ).fetchall()
    else:
        rows = connection.execute(
            'SELECT estudante, turma FROM students ORDER BY turma, estudante'
        ).fetchall()

    return [dict(row) for row in rows]


def upsert_gradebook_item(
    connection: sqlite3.Connection,
    nome: str,
    categoria: str,
    bimestre: str,
    recuperacao: bool = False,
    peso: float = 1.0,
    nota_maxima: float = 10.0,
    turma: str | None = None,
    origem: str | None = None,
) -> int:
    timestamp = datetime.utcnow().isoformat()
    turma_key = turma or ''
    connection.execute(
        '''
        INSERT INTO gradebook_items (nome, categoria, bimestre, recuperacao, peso, nota_maxima, turma, origem, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(nome, categoria, bimestre, turma) DO UPDATE SET
            recuperacao = excluded.recuperacao,
            peso = excluded.peso,
            nota_maxima = excluded.nota_maxima,
            origem = excluded.origem
        ''',
        (nome, categoria, bimestre, 1 if recuperacao else 0, peso, nota_maxima, turma_key, origem, timestamp)
    )
    row = connection.execute(
        '''
        SELECT id FROM gradebook_items
        WHERE nome = ? AND categoria = ? AND bimestre = ? AND COALESCE(turma, '') = COALESCE(?, '')
        ''',
        (nome, categoria, bimestre, turma_key)
    ).fetchone()
    return int(row['id'])


def upsert_gradebook_score(
    connection: sqlite3.Connection,
    student_id: int,
    item_id: int,
    nota: float,
    observacoes: str | None = None,
) -> None:
    connection.execute(
        '''
        INSERT INTO gradebook_scores (student_id, item_id, nota, observacoes, lancado_em)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(student_id, item_id) DO UPDATE SET
            nota = excluded.nota,
            observacoes = excluded.observacoes,
            lancado_em = excluded.lancado_em
        ''',
        (student_id, item_id, nota, observacoes, datetime.utcnow().isoformat())
    )


def get_gradebook_report(
    connection: sqlite3.Connection,
    bimestre: str,
    turma: str | None = None,
    estudante: str | None = None,
) -> list[dict]:
    params: list = [bimestre]
    filters = ['gi.bimestre = ?']

    if turma:
        filters.append('s.turma = ?')
        params.append(turma)

    if estudante:
        filters.append('s.estudante = ?')
        params.append(estudante)

    rows = connection.execute(
        f'''
        SELECT
            s.estudante,
            s.turma,
            gi.bimestre,
            gi.recuperacao,
            gi.categoria,
            gi.nome AS atividade,
            gi.peso,
            gi.nota_maxima,
            gs.nota,
            gs.observacoes,
            gi.origem
        FROM gradebook_scores gs
        JOIN students s ON s.id = gs.student_id
        JOIN gradebook_items gi ON gi.id = gs.item_id
        WHERE {' AND '.join(filters)}
        ORDER BY s.turma, s.estudante, gi.categoria, gi.nome
        ''',
        params
    ).fetchall()
    return [dict(row) for row in rows]


def get_gradebook_student_summary(
    connection: sqlite3.Connection,
    estudante: str,
    bimestre: str,
    turma: str | None = None,
) -> dict | None:
    rows = get_gradebook_report(connection, bimestre, turma=turma, estudante=estudante)
    if not rows:
        return None

    category_scores: dict[str, list[tuple[float, float, float]]] = {}
    overall_weighted_sum = 0.0
    overall_weight = 0.0

    for row in rows:
        normalized_score = 0.0 if float(row['nota_maxima']) == 0 else (float(row['nota']) / float(row['nota_maxima'])) * 10
        weight = float(row['peso'])
        category_scores.setdefault(row['categoria'], []).append((normalized_score, weight, float(row['nota'])))
        overall_weighted_sum += normalized_score * weight
        overall_weight += weight

    categories = {}
    for category, values in category_scores.items():
        weighted_sum = sum(score * weight for score, weight, _ in values)
        total_weight = sum(weight for _, weight, _ in values)
        categories[category] = round(weighted_sum / total_weight, 2) if total_weight else None

    return {
        'estudante': rows[0]['estudante'],
        'turma': rows[0]['turma'],
        'bimestre': bimestre,
        'media_geral_bimestral': round(overall_weighted_sum / overall_weight, 2) if overall_weight else None,
        'categorias': categories,
        'quantidade_lancamentos': len(rows)
    }


def sync_simulations_to_gradebook(connection: sqlite3.Connection, bimestre: str, turma: str | None = None) -> int:
    params: list = []
    turma_filter = ''
    if turma:
        turma_filter = 'WHERE s.turma = ?'
        params.append(turma)

    rows = connection.execute(
        f'''
        SELECT
            sr.id AS simulation_record_id,
            s.id AS student_id,
            s.estudante,
            s.turma,
            sr.simulacao,
            sr.nota AS nota_simulacao,
            ce.final_score AS nota_conclusao
        FROM simulation_records sr
        JOIN students s ON s.id = sr.student_id
        LEFT JOIN conclusion_evaluations ce ON ce.simulation_record_id = sr.id
        {turma_filter}
        ORDER BY s.turma, s.estudante, sr.simulacao
        ''',
        params
    ).fetchall()

    synced = 0
    for row in rows:
        componentes = [float(row['nota_simulacao'])]
        if row['nota_conclusao'] is not None:
            componentes.append(float(row['nota_conclusao']))
        nota_integrada = sum(componentes) / len(componentes)

        item_id = upsert_gradebook_item(
            connection,
            nome=row['simulacao'],
            categoria='simulacao',
            bimestre=bimestre,
            recuperacao=False,
            peso=1.0,
            nota_maxima=10.0,
            turma=row['turma'],
            origem='sync_simulation_records'
        )
        upsert_gradebook_score(
            connection,
            student_id=int(row['student_id']),
            item_id=item_id,
            nota=round(nota_integrada, 2),
            observacoes='Nota integrada da simulação com conclusão avaliada.'
        )
        synced += 1

    return synced