from __future__ import annotations

from pathlib import Path
import argparse

from ai_client import AIClient
from config import Settings
from database import export_results_csv
from gradebook_services import (
    export_gradebook_report,
    get_consolidated_student_summary,
    import_gradebook_items,
    import_gradebook_scores,
    sync_gradebook_simulations,
)
from services import EvaluationService, get_student_average, get_student_roster


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Sistema em Python para avaliar conclusões de alunos com IA e consolidar notas.'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    evaluate_parser = subparsers.add_parser('evaluate', help='Lê um CSV, avalia conclusões e salva no banco/CSV.')
    evaluate_parser.add_argument('input_csv', type=Path, help='Arquivo CSV com estudante, turma, simulacao, nota e conclusao.')
    evaluate_parser.add_argument('--output-csv', type=Path, default=Path('resultados_conclusoes.csv'))
    evaluate_parser.add_argument('--db', type=Path, default=None, help='Caminho do banco SQLite. Padrão: notas.db na pasta atual.')

    average_parser = subparsers.add_parser('student-average', help='Calcula média geral do aluno.')
    average_parser.add_argument('estudante', help='Nome completo do estudante.')
    average_parser.add_argument('--turma', default=None, help='Turma do estudante, para evitar ambiguidades.')
    average_parser.add_argument('--db', type=Path, default=None, help='Caminho do banco SQLite.')

    roster_parser = subparsers.add_parser('list-students', help='Lista alunos cadastrados para reutilizar nas simulações.')
    roster_parser.add_argument('--turma', default=None, help='Filtra por turma.')
    roster_parser.add_argument('--db', type=Path, default=None, help='Caminho do banco SQLite.')
    roster_parser.add_argument('--output-csv', type=Path, default=None, help='Se informado, exporta a lista para CSV.')

    gradebook_items_parser = subparsers.add_parser('gradebook-import-items', help='Importa componentes bimestrais como avaliação, experiência e outras notas.')
    gradebook_items_parser.add_argument('input_csv', type=Path, help='CSV com categoria, atividade, bimestre e opcionais peso, nota_maxima, turma, origem.')
    gradebook_items_parser.add_argument('--db', type=Path, default=None, help='Caminho do banco SQLite.')

    gradebook_scores_parser = subparsers.add_parser('gradebook-import-scores', help='Importa lançamentos de notas bimestrais por aluno.')
    gradebook_scores_parser.add_argument('input_csv', type=Path, help='CSV com estudante, turma, categoria, atividade, nota, bimestre e opcionais.')
    gradebook_scores_parser.add_argument('--db', type=Path, default=None, help='Caminho do banco SQLite.')

    sync_parser = subparsers.add_parser('gradebook-sync-simulations', help='Sincroniza as simulações já avaliadas para o módulo consolidado.')
    sync_parser.add_argument('--bimestre', required=True, help='Exemplo: 1o bimestre')
    sync_parser.add_argument('--turma', default=None, help='Opcional: sincroniza apenas uma turma.')
    sync_parser.add_argument('--db', type=Path, default=None, help='Caminho do banco SQLite.')

    report_parser = subparsers.add_parser('gradebook-report', help='Exporta relatório consolidado do bimestre para CSV.')
    report_parser.add_argument('--bimestre', required=True, help='Exemplo: 1o bimestre')
    report_parser.add_argument('--output-csv', type=Path, default=Path('relatorio_bimestral.csv'))
    report_parser.add_argument('--turma', default=None, help='Opcional: filtra por turma.')
    report_parser.add_argument('--estudante', default=None, help='Opcional: filtra por estudante.')
    report_parser.add_argument('--db', type=Path, default=None, help='Caminho do banco SQLite.')

    summary_parser = subparsers.add_parser('gradebook-student-summary', help='Mostra resumo consolidado do bimestre para um estudante.')
    summary_parser.add_argument('estudante', help='Nome completo do estudante.')
    summary_parser.add_argument('--bimestre', required=True, help='Exemplo: 1o bimestre')
    summary_parser.add_argument('--turma', default=None, help='Opcional: filtra por turma.')
    summary_parser.add_argument('--db', type=Path, default=None, help='Caminho do banco SQLite.')

    return parser


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    settings = Settings.from_env(base_dir)
    parser = build_parser()
    args = parser.parse_args()

    database_path = args.db or settings.sqlite_path

    if args.command == 'evaluate':
        service = EvaluationService(database_path, AIClient(settings))
        summary = service.evaluate_csv(args.input_csv, args.output_csv)
        print('Avaliação concluída.')
        print(f"Linhas processadas: {summary['linhas_processadas']}")
        print(f"Banco SQLite: {summary['banco_sqlite']}")
        if summary['arquivo_saida']:
            print(f"CSV de saída: {summary['arquivo_saida']}")
        return

    if args.command == 'student-average':
        summary = get_student_average(database_path, args.estudante, args.turma)
        if not summary:
            print('Nenhum registro encontrado para esse estudante.')
            return

        print(f"Estudante: {summary['estudante']}")
        print(f"Turma: {summary['turma']}")
        print(f"Média das simulações: {summary['media_simulacoes']}")
        print(f"Média das conclusões: {summary['media_conclusoes']}")
        print(f"Média geral integrada: {summary['media_geral']}")
        print(f"Quantidade de registros: {summary['quantidade_registros']}")
        return

    if args.command == 'list-students':
        rows = get_student_roster(database_path, args.turma)
        if args.output_csv:
            export_results_csv(rows, args.output_csv)
            print(f'Lista exportada para: {args.output_csv}')
            return

        if not rows:
            print('Nenhum aluno encontrado.')
            return

        for row in rows:
            print(f"{row['turma']} - {row['estudante']}")
        return

    if args.command == 'gradebook-import-items':
        summary = import_gradebook_items(database_path, args.input_csv)
        print(f"Componentes importados: {summary['componentes_importados']}")
        print(f"Banco SQLite: {summary['banco_sqlite']}")
        return

    if args.command == 'gradebook-import-scores':
        summary = import_gradebook_scores(database_path, args.input_csv)
        print(f"Notas importadas: {summary['notas_importadas']}")
        print(f"Banco SQLite: {summary['banco_sqlite']}")
        return

    if args.command == 'gradebook-sync-simulations':
        summary = sync_gradebook_simulations(database_path, args.bimestre, args.turma)
        print(f"Registros sincronizados: {summary['registros_sincronizados']}")
        print(f"Bimestre: {summary['bimestre']}")
        print(f"Banco SQLite: {summary['banco_sqlite']}")
        return

    if args.command == 'gradebook-report':
        summary = export_gradebook_report(database_path, args.bimestre, args.output_csv, args.turma, args.estudante)
        print(f"Linhas exportadas: {summary['linhas_exportadas']}")
        print(f"Arquivo de saída: {summary['arquivo_saida']}")
        return

    if args.command == 'gradebook-student-summary':
        summary = get_consolidated_student_summary(database_path, args.estudante, args.bimestre, args.turma)
        if not summary:
            print('Nenhum lançamento encontrado para esse estudante nesse bimestre.')
            return

        print(f"Estudante: {summary['estudante']}")
        print(f"Turma: {summary['turma']}")
        print(f"Bimestre: {summary['bimestre']}")
        print(f"Média geral bimestral: {summary['media_geral_bimestral']}")
        print(f"Quantidade de lançamentos: {summary['quantidade_lancamentos']}")
        for categoria, media in summary['categorias'].items():
            print(f"{categoria}: {media}")
        return


if __name__ == '__main__':
    main()