import argparse
import base64
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
DEFAULT_SOURCE_WORKSHEET = "app web resultados"
DEFAULT_EXPORT_DIR = "exports_turmas"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Le os relatórios finais da aba 'app web resultados', calcula a média das etapas "
            "em escala 0 a 10 e exporta um resumo por turma."
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


def parse_percentage_score(value):
    cleaned = (value or "").strip().replace("%", "")
    try:
        return float(cleaned)
    except (TypeError, ValueError):
        return 0.0


def parse_timestamp(value):
    if not value:
        return datetime.min
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    return datetime.min


def build_group_name(serie, turma):
    serie_text = (serie or "").strip()
    turma_text = (turma or "").strip()
    if not serie_text and not turma_text:
        return ""
    if not serie_text:
        return turma_text
    if not turma_text:
        return serie_text
    return f"{serie_text} {turma_text}"


def parse_stage_details(value):
    if not value:
        return []

    try:
        parsed = json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return []

    if not isinstance(parsed, list):
        return []

    return [item for item in parsed if isinstance(item, dict)]


def compute_stage_average_100(stage_details):
    if not stage_details:
        return 0.0

    scores = []
    for item in stage_details:
        try:
            scores.append(float(item.get("score", 0) or 0))
        except (TypeError, ValueError):
            scores.append(0.0)

    if not scores:
        return 0.0

    return round(sum(scores) / len(scores), 2)


def parse_service_account_json(raw_value):
    candidates = [raw_value]

    stripped = raw_value.strip()
    if stripped.startswith(("'", '"')) and stripped.endswith(("'", '"')):
        candidates.append(stripped[1:-1])

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, str):
                parsed = json.loads(parsed)
            if isinstance(parsed, dict):
                return parsed
        except (TypeError, ValueError, json.JSONDecodeError):
            pass

    for candidate in candidates:
        try:
            decoded = base64.b64decode(candidate).decode("utf-8")
            parsed = json.loads(decoded)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    raise RuntimeError(
        "GOOGLE_SERVICE_ACCOUNT_JSON invalido. Use JSON bruto, JSON serializado em uma linha ou base64."
    )


def load_service_account_info():
    from os import getenv

    service_account_json = (getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or "").strip()
    service_account_file = (getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "").strip()

    if service_account_json:
        return parse_service_account_json(service_account_json)
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


def open_google_spreadsheet(client, spreadsheet_id, spreadsheet_name):
    if spreadsheet_id:
        try:
            return client.open_by_key(spreadsheet_id)
        except Exception as exc:
            if spreadsheet_name:
                try:
                    return client.open(spreadsheet_name)
                except Exception:
                    pass

            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code == 404:
                raise RuntimeError(
                    "Planilha nao encontrada pelo GOOGLE_SHEETS_SPREADSHEET_ID. Confira o ID ou remova essa variavel para usar o nome da planilha."
                ) from exc
            raise RuntimeError(f"Nao foi possivel abrir a planilha pelo ID informado: {exc}") from exc

    if spreadsheet_name:
        try:
            return client.open(spreadsheet_name)
        except Exception as exc:
            raise RuntimeError(
                "Planilha nao encontrada pelo nome informado. Confira GOOGLE_SHEETS_SPREADSHEET_NAME e o compartilhamento com a conta de servico."
            ) from exc

    raise RuntimeError("Nenhum identificador de planilha foi configurado.")


def get_spreadsheet(args):
    from os import getenv

    client = get_google_sheets_client()
    spreadsheet_id = (args.spreadsheet_id or getenv("GOOGLE_SHEETS_SPREADSHEET_ID") or "").strip()
    spreadsheet_name = (
        args.spreadsheet_name
        or getenv("GOOGLE_SHEETS_SPREADSHEET_NAME")
        or DEFAULT_SPREADSHEET_NAME
    ).strip()
    return open_google_spreadsheet(client, spreadsheet_id, spreadsheet_name)


def read_source_rows(spreadsheet, worksheet_name):
    worksheet = spreadsheet.worksheet(worksheet_name)
    return worksheet.get_all_records(default_blank="")


def select_groups(rows, requested_groups):
    available = {}
    for row in rows:
        group_name = build_group_name(row.get("serie", ""), row.get("turma", ""))
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
        row_group_name = build_group_name(row.get("serie", ""), row.get("turma", ""))
        if normalize_text(row_group_name) != group_key:
            continue

        student_name = normalize_student_name(row.get("estudante", ""))
        if not student_name or normalize_text(student_name) == "nao informado":
            skipped_rows += 1
            continue

        student_key = normalize_text(student_name)
        stage_details = parse_stage_details(row.get("detalhes_exercicios"))
        average_score_100 = compute_stage_average_100(stage_details)
        reported_score_100 = parse_percentage_score(row.get("nota"))
        timestamp = parse_timestamp(row.get("timestamp") or row.get("data_envio"))
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
            best_score = current_best["average_score_100"]
            best_timestamp = current_best["timestamp"]
            should_replace = average_score_100 > best_score or (average_score_100 == best_score and timestamp >= best_timestamp)

        if should_replace:
            student["best_attempt"] = {
                "average_score_100": average_score_100,
                "reported_score_100": reported_score_100,
                "timestamp": timestamp,
                "trilha": (row.get("trilha") or "").strip(),
                "bimestre": (row.get("bimestre") or "").strip(),
                "acertos": (row.get("acertos") or "").strip(),
                "acertos_erros": (row.get("acertos_erros") or "").strip(),
                "total_questoes": parse_score(row.get("total_questoes")),
                "tentativas_totais": parse_score(row.get("tentativas_totais")),
                "questoes_puladas": parse_score(row.get("questoes_puladas")),
                "conclusao": (row.get("conclusao") or "").strip(),
                "email": (row.get("email") or "").strip(),
                "stage_count": len(stage_details),
            }

    summary_rows = []
    for student in sorted(students.values(), key=lambda item: normalize_text(item["student_name"])):
        best_attempt = student["best_attempt"] or {
            "average_score_100": 0.0,
            "reported_score_100": 0.0,
            "timestamp": datetime.min,
            "trilha": "",
            "bimestre": "",
            "acertos": "",
            "acertos_erros": "",
            "total_questoes": 0,
            "tentativas_totais": 0,
            "questoes_puladas": 0,
            "conclusao": "",
            "email": "",
            "stage_count": 0,
        }
        completed_attempts = 1 if best_attempt["stage_count"] > 0 else 0
        final_score_100 = round(float(best_attempt["average_score_100"]), 2)
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
            "stage_count": best_attempt["stage_count"],
            "final_score_100": final_score_100,
            "final_grade_10": final_grade_10,
            "reported_score_100": round(float(best_attempt["reported_score_100"]), 2),
            "track": best_attempt["trilha"],
            "bimester": best_attempt["bimestre"],
            "acertos": best_attempt["acertos"],
            "acertos_erros": best_attempt["acertos_erros"],
            "total_questoes": best_attempt["total_questoes"],
            "tentativas_totais": best_attempt["tentativas_totais"],
            "questoes_puladas": best_attempt["questoes_puladas"],
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
        "stage_count",
        "final_score_100",
        "final_grade_10",
        "reported_score_100",
        "track",
        "bimester",
        "acertos",
        "acertos_erros",
        "total_questoes",
        "tentativas_totais",
        "questoes_puladas",
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