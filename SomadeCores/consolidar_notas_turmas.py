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
FINAL_SESSION_HEADERS = [
    "timestamp",
    "trilha",
    "serie",
    "turma",
    "bimestre",
    "estudante",
    "simulacao",
    "questoes_puladas",
    "acertos_erros",
    "nota",
    "conclusao",
    "criticas",
    "sugestoes",
    "email",
    "to_email",
    "nome_aluno",
    "acertos",
    "data_envio",
    "total_questoes",
    "tentativas_totais",
    "detalhes_exercicios",
]
DEFAULT_SPREADSHEET_NAME = "Notas CEAN 2026"
DEFAULT_SOURCE_WORKSHEET = "app web resultados"
DEFAULT_EXPORT_DIR = "exports_turmas"
SIMULATION_COLUMN_TITLE = "Soma de Cores"


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


def format_grade_10(value):
    try:
        numeric_value = round(float(value), 2)
    except (TypeError, ValueError):
        return ""

    if abs(numeric_value - round(numeric_value)) < 1e-9:
        return str(int(round(numeric_value)))

    return f"{numeric_value:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def is_bimester_label(value):
    return normalize_text(value) in {
        "1o bimestre",
        "2o bimestre",
        "3o bimestre",
        "4o bimestre",
    }


def column_index_to_letter(index):
    letters = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


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


def build_unique_headers(raw_headers):
    headers = []
    seen = {}

    for index, header in enumerate(raw_headers):
        cleaned = " ".join(str(header or "").split())
        if not cleaned:
            cleaned = f"__blank_{index + 1}"

        duplicate_count = seen.get(cleaned, 0)
        seen[cleaned] = duplicate_count + 1
        if duplicate_count:
            cleaned = f"{cleaned}__dup_{duplicate_count + 1}"

        headers.append(cleaned)

    return headers


def looks_like_final_session_row(row_values):
    if len(row_values) < len(FINAL_SESSION_HEADERS):
        return False

    simulation_name = (row_values[6] or "").strip()
    stage_details = (row_values[20] or "").strip()
    return simulation_name == "Soma de Cores - App Web" and stage_details.startswith("[")


def normalize_source_row(headers, row_values):
    named_row = {headers[index]: row_values[index] for index in range(len(headers))}
    if {"trilha", "serie", "turma", "estudante", "detalhes_exercicios"}.issubset(named_row):
        return named_row

    if looks_like_final_session_row(row_values):
        return {FINAL_SESSION_HEADERS[index]: row_values[index] for index in range(len(FINAL_SESSION_HEADERS))}

    return None


def read_source_rows(spreadsheet, worksheet_name):
    worksheet = spreadsheet.worksheet(worksheet_name)
    values = worksheet.get_all_values()
    if not values:
        return []

    headers = build_unique_headers(values[0])
    rows = []

    for raw_row in values[1:]:
        padded_row = list(raw_row) + [""] * max(0, len(headers) - len(raw_row))
        trimmed_row = padded_row[: len(headers)]
        if not any((cell or "").strip() for cell in trimmed_row):
            continue
        normalized_row = normalize_source_row(headers, trimmed_row)
        if normalized_row is not None:
            rows.append(normalized_row)

    return rows


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


def ensure_worksheet_size(worksheet, min_rows, min_cols):
    if worksheet.row_count < min_rows:
        worksheet.add_rows(min_rows - worksheet.row_count)
    if worksheet.col_count < min_cols:
        worksheet.add_cols(min_cols - worksheet.col_count)


def get_header_rows(worksheet):
    values = worksheet.get_all_values()
    if not values:
        ensure_worksheet_size(worksheet, 2, 2)
        worksheet.update(range_name="A1:B2", values=[["Nº", "ESTUDANTE"], ["", "pesos"]])
        return ["Nº", "ESTUDANTE"], ["", "pesos"]

    header_row = list(values[0])
    weight_row = list(values[1]) if len(values) > 1 else []

    if normalize_text(header_row[0] if header_row else "") == "student_name":
        raise RuntimeError(
            f"A aba '{worksheet.title}' parece ter sido sobrescrita pelo formato antigo do script. "
            "Restaure essa aba pelo historico de versoes do Google Sheets antes de rodar novamente com --write-sheets."
        )

    if len(header_row) < 2:
        header_row += [""] * (2 - len(header_row))
    if len(weight_row) < 2:
        weight_row += [""] * (2 - len(weight_row))

    updates = []
    if normalize_text(header_row[0]) != "no":
        header_row[0] = "Nº"
        updates.append(("A1", "Nº"))
    if normalize_text(header_row[1]) != "estudante":
        header_row[1] = "ESTUDANTE"
        updates.append(("B1", "ESTUDANTE"))
    if normalize_text(weight_row[1]) != "pesos":
        weight_row[1] = "pesos"
        updates.append(("B2", "pesos"))

    for cell, value in updates:
        worksheet.update_acell(cell, value)

    return header_row, weight_row


def build_student_row_map(worksheet):
    names = worksheet.col_values(2)
    student_rows = {}
    for row_index, value in enumerate(names[2:], start=3):
        student_name = normalize_student_name(value)
        if student_name:
            student_rows[normalize_text(student_name)] = row_index
    return student_rows


def append_missing_students(worksheet, summary_rows, student_rows):
    next_row = max(len(worksheet.col_values(2)) + 1, 3)
    next_number = max(len(student_rows) + 1, 1)
    appended = []

    for row in summary_rows:
        student_name = normalize_student_name(row.get("student_name", ""))
        student_key = normalize_text(student_name)
        if not student_name or student_key in student_rows:
            continue

        appended.append([str(next_number), student_name])
        student_rows[student_key] = next_row
        next_row += 1
        next_number += 1

    if appended:
        ensure_worksheet_size(worksheet, next_row - 1, 2)
        start = len(worksheet.col_values(2)) + 1
        end = start + len(appended) - 1
        worksheet.update(range_name=f"A{start}:B{end}", values=appended)

    return student_rows


def find_bimester_start(header_row, bimester_label):
    target = normalize_text(bimester_label)
    for index, value in enumerate(header_row):
        if normalize_text(value) == target:
            return index
    return None


def get_next_bimester_start(header_row, start_index):
    for index in range(start_index + 1, len(header_row)):
        if is_bimester_label(header_row[index]):
            return index
    return None


def ensure_bimester_and_simulation_column(worksheet, header_row, weight_row, bimester_label):
    start_index = find_bimester_start(header_row, bimester_label)
    if start_index is None:
        start_index = len(header_row)
        ensure_worksheet_size(worksheet, 2, start_index + 2)
        header_row.extend([""] * max(0, start_index + 2 - len(header_row)))
        weight_row.extend([""] * max(0, start_index + 2 - len(weight_row)))
        worksheet.update(range_name=f"{column_index_to_letter(start_index + 1)}1:{column_index_to_letter(start_index + 2)}2", values=[[bimester_label, SIMULATION_COLUMN_TITLE], ["", ""]])
        header_row[start_index] = bimester_label
        header_row[start_index + 1] = SIMULATION_COLUMN_TITLE
        weight_row[start_index] = ""
        weight_row[start_index + 1] = ""
        return start_index, start_index + 1

    next_bimester_start = get_next_bimester_start(header_row, start_index)
    search_end = next_bimester_start if next_bimester_start is not None else len(header_row)
    simulation_index = None
    empty_slots = []

    for index in range(start_index + 1, search_end):
        normalized_header = normalize_text(header_row[index])
        if normalized_header == normalize_text(SIMULATION_COLUMN_TITLE):
            simulation_index = index
            break
        if not (header_row[index] or "").strip():
            empty_slots.append(index)

    if simulation_index is None and empty_slots:
        simulation_index = empty_slots[0]
        worksheet.update(range_name=f"{column_index_to_letter(simulation_index + 1)}1:{column_index_to_letter(simulation_index + 1)}2", values=[[SIMULATION_COLUMN_TITLE], [""]])
        header_row[simulation_index] = SIMULATION_COLUMN_TITLE
        if len(weight_row) <= simulation_index:
            weight_row.extend([""] * (simulation_index + 1 - len(weight_row)))
        weight_row[simulation_index] = ""

    if simulation_index is None:
        if next_bimester_start is not None:
            raise RuntimeError(
                f"A aba '{worksheet.title}' nao tem espaco livre no bloco de {bimester_label} para adicionar a coluna {SIMULATION_COLUMN_TITLE}."
            )

        simulation_index = len(header_row)
        ensure_worksheet_size(worksheet, 2, simulation_index + 1)
        header_row.append(SIMULATION_COLUMN_TITLE)
        if len(weight_row) < len(header_row):
            weight_row.extend([""] * (len(header_row) - len(weight_row)))
        worksheet.update(range_name=f"{column_index_to_letter(simulation_index + 1)}1:{column_index_to_letter(simulation_index + 1)}2", values=[[SIMULATION_COLUMN_TITLE], [""]])

    return start_index, simulation_index


def update_simulation_column(worksheet, simulation_index, summary_rows, student_rows):
    last_row = max(student_rows.values(), default=2)
    ensure_worksheet_size(worksheet, last_row, simulation_index + 1)
    current_values = worksheet.col_values(simulation_index + 1)
    column_values = list(current_values) + [""] * max(0, last_row - len(current_values))

    if len(column_values) < 2:
        column_values += [""] * (2 - len(column_values))
    column_values[0] = SIMULATION_COLUMN_TITLE
    column_values[1] = ""

    for row in summary_rows:
        student_key = normalize_text(row.get("student_name", ""))
        target_row = student_rows.get(student_key)
        if target_row is None:
            continue
        while len(column_values) < target_row:
            column_values.append("")
        column_values[target_row - 1] = format_grade_10(row.get("final_grade_10"))

    col_letter = column_index_to_letter(simulation_index + 1)
    worksheet.update(
        range_name=f"{col_letter}1:{col_letter}{len(column_values)}",
        values=[[value] for value in column_values],
    )


def update_bimester_total_column(worksheet, total_index, simulation_indexes, student_rows):
    if not simulation_indexes:
        return

    last_row = max(student_rows.values(), default=2)
    formulas = []
    for row_number in range(3, last_row + 1):
        references = [f"{column_index_to_letter(index + 1)}{row_number}" for index in simulation_indexes]
        formulas.append(["=" + "+".join(references)])

    col_letter = column_index_to_letter(total_index + 1)
    worksheet.update(
        range_name=f"{col_letter}3:{col_letter}{last_row}",
        values=formulas,
        value_input_option="USER_ENTERED",
    )


def write_group_worksheet(spreadsheet, worksheet_title, summary_rows):
    worksheet = get_or_create_worksheet(spreadsheet, worksheet_title, rows=100, cols=30)
    header_row, weight_row = get_header_rows(worksheet)
    student_rows = build_student_row_map(worksheet)
    student_rows = append_missing_students(worksheet, summary_rows, student_rows)

    rows_by_bimester = {}
    for row in summary_rows:
        bimester_label = (row.get("bimester") or "").strip()
        if not bimester_label:
            continue
        rows_by_bimester.setdefault(bimester_label, []).append(row)

    for bimester_label, bimester_rows in rows_by_bimester.items():
        total_index, simulation_index = ensure_bimester_and_simulation_column(worksheet, header_row, weight_row, bimester_label)
        update_simulation_column(worksheet, simulation_index, bimester_rows, student_rows)

        refreshed_header = worksheet.row_values(1)
        next_bimester_start = get_next_bimester_start(refreshed_header, total_index)
        search_end = next_bimester_start if next_bimester_start is not None else len(refreshed_header)
        simulation_indexes = [
            index
            for index in range(total_index + 1, search_end)
            if (refreshed_header[index] or "").strip() and not is_bimester_label(refreshed_header[index])
        ]
        update_bimester_total_column(worksheet, total_index, simulation_indexes, student_rows)

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
            write_group_worksheet(spreadsheet, worksheet_title, summary_rows)
            print(f"Turma {group_name}: aba atualizada em '{worksheet_title}'.")


if __name__ == "__main__":
    main()