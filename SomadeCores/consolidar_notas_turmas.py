import argparse
import csv
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path


GOOGLE_SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
DEFAULT_SPREADSHEET_NAME = "Notas CEAN 2026"
DEFAULT_SOURCE_WORKSHEET = "app web"
DEFAULT_EXPORT_DIR = "exports_turmas"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Le os envios brutos da aba 'app web', consolida a melhor tentativa geral "
            "em cada turma e exporta um resumo final."
        )
    )
    parser.add_argument(
        "--group",
        action="append",
        dest="groups",
        default=[],
        help="Turma ou codigo para filtrar. Pode ser usado mais de uma vez.",
    )
    parser.add_argument(
        "--source-worksheet",
        default=DEFAULT_SOURCE_WORKSHEET,
        help="Nome da aba com os dados brutos do app web.",
    )
    parser.add_argument(
        "--spreadsheet-name",
        default=None,
        help="Nome da planilha no Google Sheets. Usa a variavel GOOGLE_SHEETS_SPREADSHEET_NAME quando omitido.",
    )
    parser.add_argument(
        "--spreadsheet-id",
        default=None,
        help="ID da planilha no Google Sheets. Tem prioridade sobre o nome.",
    )
    parser.add_argument(
        "--export-dir",
        default=DEFAULT_EXPORT_DIR,
        help="Pasta local onde os CSVs por turma serao gerados.",
    )
    parser.add_argument(
        "--write-sheets",
        action="store_true",
        help="Atualiza ou cria abas das turmas na mesma planilha do Google Sheets.",
    )
    parser.add_argument(
        "--worksheet-prefix",
        default="",
        help="Prefixo opcional para as abas de turma no Google Sheets.",
    )
    return parser.parse_args()


def normalize_text(text):
    normalized = unicodedata.normalize("NFKD", text or "")
    return normalized.encode("ascii", "ignore").decode("ascii").lower().strip()


def normalize_student_name(name):
    cleaned = " ".join((name or "").split())
    return cleaned.strip()


def parse_score(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def parse_timestamp(value):
    if not value:
        return datetime.min
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.min


def load_service_account_info():
    from os import getenv

    service_account_json = (getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or "").strip()
    service_account_file = (getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "").strip()

    if service_account_json:
        return json.loads(service_account_json)
    if service_account_file:
        return json.loads(Path(service_account_file).read_text(encoding="utf-8"))

    raise RuntimeError(
        "Defina GOOGLE_SERVICE_ACCOUNT_JSON ou GOOGLE_SERVICE_ACCOUNT_FILE antes de executar o script."
    )


def get_google_sheets_client():
    import gspread
    from google.oauth2.service_account import Credentials

    credentials = Credentials.from_service_account_info(
        load_service_account_info(),
        scopes=GOOGLE_SHEETS_SCOPES,
    )
    return gspread.authorize(credentials)


def get_spreadsheet(args):
    from os import getenv

    client = get_google_sheets_client()
    spreadsheet_id = (args.spreadsheet_id or getenv("GOOGLE_SHEETS_SPREADSHEET_ID") or "").strip()
    spreadsheet_name = (
        args.spreadsheet_name
        or getenv("GOOGLE_SHEETS_SPREADSHEET_NAME")
        or DEFAULT_SPREADSHEET_NAME
    ).strip()
    return client.open_by_key(spreadsheet_id) if spreadsheet_id else client.open(spreadsheet_name)


def read_source_rows(spreadsheet, worksheet_name):
    worksheet = spreadsheet.worksheet(worksheet_name)
    return worksheet.get_all_records(default_blank="")


def select_groups(rows, requested_groups):
    available = {}
    for row in rows:
        group_name = (row.get("student_group") or "").strip()
        if not group_name or normalize_text(group_name) == "nao informado":
            continue
        available.setdefault(normalize_text(group_name), group_name)

    if requested_groups:
        selected = []
        for group_name in requested_groups:
            key = normalize_text(group_name)
            if key not in available:
                raise RuntimeError(f"Turma nao encontrada nos dados brutos: {group_name}")
            selected.append(available[key])
        return selected

    return sorted(available.values(), key=normalize_text)


def summarize_group(rows, group_name):
    group_key = normalize_text(group_name)
    students = {}
    skipped_rows = 0

    for row in rows:
        if normalize_text(row.get("student_group", "")) != group_key:
            continue

        student_name = normalize_student_name(row.get("student_name", ""))
        if not student_name or normalize_text(student_name) == "nao informado":
            skipped_rows += 1
            continue

        student_key = normalize_text(student_name)
        score = parse_score(row.get("score"))
        exercise_type = (row.get("exercise_type") or "").strip() or "sem-tipo"
        timestamp = parse_timestamp(row.get("timestamp"))
        student = students.setdefault(
            student_key,
            {
                "student_name": student_name,
                "student_group": group_name,
                "attempts": 0,
                "latest_submission": datetime.min,
                "best_attempt": None,
            },
        )

        student["attempts"] += 1
        if timestamp >= student["latest_submission"]:
            student["latest_submission"] = timestamp

        current_best = student["best_attempt"]
        should_replace = current_best is None
        if current_best is not None:
            best_score = current_best["score"]
            best_timestamp = current_best["timestamp"]
            should_replace = score > best_score or (score == best_score and timestamp >= best_timestamp)

        if should_replace:
            student["best_attempt"] = {
                "score": score,
                "timestamp": timestamp,
                "exercise_type": exercise_type,
                "exercise_title": (row.get("exercise_title") or "").strip(),
                "result": (row.get("result") or "").strip(),
                "metric_summary": (row.get("metric_summary") or "").strip(),
            }

    summary_rows = []
    for student in sorted(students.values(), key=lambda item: normalize_text(item["student_name"])):
        best_attempt = student["best_attempt"] or {
            "score": 0,
            "timestamp": datetime.min,
            "exercise_type": "",
            "exercise_title": "",
            "result": "",
            "metric_summary": "",
        }
        completed_attempts = 1 if best_attempt["score"] > 0 else 0
        final_score_100 = round(float(best_attempt["score"]), 2)
        final_grade_10 = round(final_score_100 / 10.0, 2)
        latest_submission = ""
        if student["latest_submission"] != datetime.min:
            latest_submission = student["latest_submission"].isoformat(timespec="seconds")
        best_submission = ""
        if best_attempt["timestamp"] != datetime.min:
            best_submission = best_attempt["timestamp"].isoformat(timespec="seconds")

        row = {
            "student_name": student["student_name"],
            "student_group": student["student_group"],
            "attempts": student["attempts"],
            "completed_attempts": completed_attempts,
            "final_score_100": final_score_100,
            "final_grade_10": final_grade_10,
            "best_result": best_attempt["result"],
            "best_exercise_type": best_attempt["exercise_type"],
            "best_exercise_title": best_attempt["exercise_title"],
            "best_metric_summary": best_attempt["metric_summary"],
            "best_submission": best_submission,
            "latest_submission": latest_submission,
        }
        summary_rows.append(row)

    return summary_rows, skipped_rows


def build_output_table(summary_rows):
    headers = [
        "student_name",
        "student_group",
        "attempts",
        "completed_attempts",
        "final_score_100",
        "final_grade_10",
        "best_result",
        "best_exercise_type",
        "best_exercise_title",
        "best_metric_summary",
        "best_submission",
        "latest_submission",
    ]
    values = [headers]
    for row in summary_rows:
        values.append([row.get(header, "") for header in headers])
    return headers, values


def sanitize_filename(value):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._") or "turma"


def sanitize_worksheet_title(value):
    cleaned = re.sub(r"[:\\/?*\[\]]", " ", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return (cleaned or "Turma")[:100]


def export_group_csv(export_dir, group_name, headers, summary_rows):
    export_dir.mkdir(parents=True, exist_ok=True)
    file_path = export_dir / f"{sanitize_filename(group_name)}.csv"
    with file_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(summary_rows)
    return file_path


def get_or_create_worksheet(spreadsheet, title, rows, cols):
    import gspread

    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)


def write_group_worksheet(spreadsheet, worksheet_title, table_values):
    row_count = max(100, len(table_values) + 10)
    col_count = max(12, len(table_values[0]) + 2)
    worksheet = get_or_create_worksheet(spreadsheet, worksheet_title, row_count, col_count)
    worksheet.clear()
    worksheet.update("A1", table_values)
    return worksheet


def main():
    args = parse_args()
    spreadsheet = get_spreadsheet(args)
    source_rows = read_source_rows(spreadsheet, args.source_worksheet)
    if not source_rows:
        raise RuntimeError("A aba de origem esta vazia. Nenhuma consolidacao foi gerada.")

    selected_groups = select_groups(source_rows, args.groups)
    if not selected_groups:
        raise RuntimeError("Nenhuma turma valida foi encontrada na aba de origem.")

    export_dir = Path(args.export_dir)
    print(f"Planilha: {spreadsheet.title}")
    print(f"Aba de origem: {args.source_worksheet}")

    for group_name in selected_groups:
        summary_rows, skipped_rows = summarize_group(source_rows, group_name)
        headers, table_values = build_output_table(summary_rows)
        csv_path = export_group_csv(export_dir, group_name, headers, summary_rows)
        print(f"Turma {group_name}: {len(summary_rows)} aluno(s) consolidados. CSV: {csv_path}")
        if skipped_rows:
            print(
                f"Turma {group_name}: {skipped_rows} envio(s) ignorado(s) por falta de identificacao do estudante."
            )

        if args.write_sheets:
            worksheet_title = sanitize_worksheet_title(f"{args.worksheet_prefix}{group_name}")
            write_group_worksheet(spreadsheet, worksheet_title, table_values)
            print(f"Turma {group_name}: aba atualizada em '{worksheet_title}'.")


if __name__ == "__main__":
    main()