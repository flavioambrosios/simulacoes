"""Versão web do simulador de ondas com Dash e Plotly.

Mapa mental do arquivo para iniciantes:
1. Constantes globais e parâmetros do simulador.
2. Funções numéricas: ondas, envelopes e otimização.
3. Funções visuais: gráficos, resumos e Lab RGB.
4. Funções pedagógicas: exercícios, sessão e avaliação.
5. Callbacks do Dash: ligam a interface ao cálculo.
"""

import base64
import hashlib
import json
import logging
import os
import re
import unicodedata
import urllib.request
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import numpy as np
from dash import Dash, Input, Output, State, ctx, dcc, html, dash_table
from dash import no_update
import gspread
from google.oauth2.service_account import Credentials
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy.optimize import minimize
from scipy.signal import hilbert


# Essas constantes definem a malha espectral, a malha temporal e os limites físicos usados em todo o app.
FREQS = np.arange(400, 801, 10)
N_FREQS = len(FREQS)
T = np.linspace(0, 2e-13, 4000)
T_OPT = np.linspace(0, 2e-13, 1200)
TIME_FS = T * 1e15
AMP_MIN = -1.0
AMP_MAX = 1.0
TARGET_DIFF = 0.25
ZERO_AMPS = np.zeros(N_FREQS)
BASIS = np.sin(2 * np.pi * FREQS[:, None] * 1e12 * T[None, :])
BASIS_OPT = np.sin(2 * np.pi * FREQS[:, None] * 1e12 * T_OPT[None, :])
TIME_WINDOW_OPTIONS = [200, 150, 100, 50]
DEFAULT_TIME_WINDOW_FS = TIME_WINDOW_OPTIONS[0]
MAX_FREQ_DELTA = int(FREQS[-1] - FREQS[0])
DEFAULT_SMOOTHING = 1
DEFAULT_FREQ_DELTA = MAX_FREQ_DELTA
TABLE_DECIMALS = 3
GOOGLE_SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SHEET_HEADERS = [
    "timestamp",
    "student_name",
    "student_group",
    "exercise_id",
    "exercise_type",
    "exercise_title",
    "difficulty",
    "result",
    "score",
    "metric_summary",
    "max_diff",
    "smoothing_window",
    "freq_delta",
    "has_optimization",
    "active_count1",
    "active_count2",
    "answer_text",
    "table_data_json",
    "history_data_json",
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
SIMULATION_NAME = "Soma de Cores - App Web"
PROFESSOR_EMAIL = "flavio.ambrosio@edu.se.df.gov.br"
PLANILHA_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxX6bygZyd5PwiPXZtLz4GfpqatnFT_ZRGSPPcQYSxrc2cWqD8YyX-ic4oOTG1QvRzX/exec"
EMAIL_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyVQeiZ9lxSy86Lp-85VlJWRXamY2uc_-s9dCo472uLkeg_ezHeGdQPjl4HAH7Uonfi/exec"
CLASS_SHEET_SIMULATION_TITLE = "Soma de Cores"
SIMULATION_DOI = "10.5281/zenodo.20737876"
SIMULATION_URL = "https://flavioambrosios.github.io/simulacoes/SomadeCores/"
SESSION_EXERCISE_TYPES = [
    "envelope-target",
    "smoothing-observe",
    "frequency-window",
    "color-compare",
    "real-world-correlation",
]
STUDENT_DATABASE_PATH = Path(__file__).resolve().parents[1] / "AvaliacaoBimestralEducacaoDigital" / "alunos.js"
GRADE_OPTIONS = [
    {"label": "1o ano", "value": "1o ano"},
    {"label": "2o ano", "value": "2o ano"},
    {"label": "3o ano", "value": "3o ano"},
]
BIMESTER_OPTIONS = [
    {"label": "1o bimestre", "value": "1o bimestre"},
    {"label": "2o bimestre", "value": "2o bimestre"},
    {"label": "3o bimestre", "value": "3o bimestre"},
    {"label": "4o bimestre", "value": "4o bimestre"},
]
STUDENT_ACCESS_SALT = "EDU-DIGITAL-2026"
STUDENT_ACCESS_PASSWORD_HASH = "ecb5bbc15dbfec02cd9e9d723a8ddfdd2010c266898074340752eeebb2ea4f55"


def hash_student_access_password(raw_password):
    seed = f"{STUDENT_ACCESS_SALT}{raw_password or ''}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def is_student_access_granted(access_state):
    if not isinstance(access_state, dict):
        return False
    return bool(access_state.get("authenticated"))


# Funções deste primeiro bloco fazem a tradução entre tabela da interface e vetores numéricos.
def clamp_amp(value):
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    return float(np.clip(numeric, AMP_MIN, AMP_MAX))


def amps_to_table_data(amps1, amps2):
    return [
        {
            "frequencia": int(freq),
            "onda1": round(float(amp1), TABLE_DECIMALS),
            "onda2": round(float(amp2), TABLE_DECIMALS),
        }
        for freq, amp1, amp2 in zip(FREQS, amps1, amps2)
    ]


def table_data_to_amps(table_data):
    amps1 = []
    amps2 = []
    for row in table_data:
        amps1.append(clamp_amp(row.get("onda1", 0)))
        amps2.append(clamp_amp(row.get("onda2", 0)))
    return np.array(amps1, dtype=float), np.array(amps2, dtype=float)


def generate_wave(amps, basis=BASIS):
    # A base senoidal já foi pré-calculada; aqui só combinamos os pesos escolhidos pelo usuário.
    return amps @ basis


def sanitize_smoothing_window(value, signal_length):
    window = max(1, int(value or 1))
    if window % 2 == 0:
        window += 1
    max_allowed = signal_length if signal_length % 2 == 1 else signal_length - 1
    window = min(window, max_allowed)
    return max(1, window)


def smooth_signal(signal, smoothing_window):
    window = sanitize_smoothing_window(smoothing_window, len(signal))
    if window <= 1:
        return signal

    pad = window // 2
    kernel = np.ones(window, dtype=float) / window
    padded = np.pad(signal, (pad, pad), mode="edge")
    return np.convolve(padded, kernel, mode="valid")


def optimization_smoothing_window(smoothing_window):
    base_window = sanitize_smoothing_window(smoothing_window, len(T))
    scaled_window = max(1, int(round(base_window * len(T_OPT) / len(T))))
    return sanitize_smoothing_window(scaled_window, len(T_OPT))


def compute_envelope(wave, smoothing_window=DEFAULT_SMOOTHING):
    # O envelope de Hilbert é a grandeza usada para comparar o comportamento global das duas ondas.
    envelope = np.abs(hilbert(wave))
    return smooth_signal(envelope, smoothing_window)


def max_envelope_difference(amps1, amps2, smoothing_window=DEFAULT_SMOOTHING):
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    return float(np.max(np.abs(
        compute_envelope(wave1, smoothing_window) - compute_envelope(wave2, smoothing_window)
    )))


def max_envelope_difference_fast(amps1, amps2, smoothing_window=DEFAULT_SMOOTHING):
    wave1 = generate_wave(amps1, BASIS_OPT)
    wave2 = generate_wave(amps2, BASIS_OPT)
    optimization_window = optimization_smoothing_window(smoothing_window)
    return float(np.max(np.abs(
        compute_envelope(wave1, optimization_window) - compute_envelope(wave2, optimization_window)
    )))


def is_frequency_delta_unrestricted(freq_delta):
    return int(freq_delta) >= MAX_FREQ_DELTA


def format_frequency_delta(freq_delta):
    if is_frequency_delta_unrestricted(freq_delta):
        return "livre"
    return f"+-{int(freq_delta)} THz"


def build_single_wave_optimization_mask(initial_amps, freq_delta):
    if is_frequency_delta_unrestricted(freq_delta):
        return np.ones(N_FREQS, dtype=bool)

    active_mask = np.abs(initial_amps) > 1e-12
    if not np.any(active_mask):
        return np.ones(N_FREQS, dtype=bool)

    active_freqs = FREQS[active_mask]
    distances = np.abs(FREQS[:, None] - active_freqs[None, :])
    return np.min(distances, axis=1) <= int(freq_delta)


def build_optimization_masks(initial_amps1, initial_amps2, freq_delta):
    return (
        build_single_wave_optimization_mask(initial_amps1, freq_delta),
        build_single_wave_optimization_mask(initial_amps2, freq_delta),
    )


def merge_optimized_values(optimized_values, base_amps1, base_amps2, optimize_masks):
    optimize_mask1, optimize_mask2 = optimize_masks
    free_count1 = int(np.sum(optimize_mask1))
    amps1 = base_amps1.copy()
    amps2 = base_amps2.copy()
    amps1[optimize_mask1] = optimized_values[:free_count1]
    amps2[optimize_mask2] = optimized_values[free_count1:]
    return amps1, amps2


def normalize_text(text):
    # Normalizar texto evita problemas com maiúsculas, acentos e pequenas variações de escrita.
    normalized = unicodedata.normalize("NFKD", text or "")
    return normalized.encode("ascii", "ignore").decode("ascii").lower()


def infer_grade_class_from_track(track_name):
    match = re.search(r"([123]o ano)\s+([A-Z])$", (track_name or "").strip())
    if not match:
        return "", ""
    return match.group(1), match.group(2)


def load_student_database():
    # O banco de alunos alimenta os seletores do formulário final da sessão.
    empty_database = {"bySheet": {}, "bySerieTurma": {}, "byTrilha": {}}

    try:
        file_text = STUDENT_DATABASE_PATH.read_text(encoding="utf-8")
    except OSError:
        logging.exception("Nao foi possivel ler o banco de alunos em %s.", STUDENT_DATABASE_PATH)
        return empty_database

    match = re.search(r"const\s+STUDENT_DATABASE\s*=\s*(\{.*\})\s*;\s*$", file_text, re.DOTALL)
    if not match:
        logging.warning("Formato inesperado no arquivo de alunos: %s", STUDENT_DATABASE_PATH)
        return empty_database

    try:
        parsed = json.loads(match.group(1))
    except json.JSONDecodeError:
        logging.exception("Nao foi possivel interpretar o arquivo de alunos em %s.", STUDENT_DATABASE_PATH)
        return empty_database

    return {
        "bySheet": parsed.get("bySheet", {}),
        "bySerieTurma": parsed.get("bySerieTurma", {}),
        "byTrilha": parsed.get("byTrilha", {}),
    }


def should_skip_student_worksheet(title):
    normalized = normalize_text(title).strip()
    return normalized in {
        "app web",
        "app web resultados",
    }


def normalize_student_name_list(names):
    unique_names = sorted({name.strip() for name in names if (name or "").strip()}, key=normalize_text)
    return unique_names


def load_student_database_from_google_sheets():
    # Quando possível, usa a planilha Google como fonte principal dos nomes de estudantes.
    empty_database = {"bySheet": {}, "bySerieTurma": {}, "byTrilha": {}}

    if not is_google_sheets_configured():
        return empty_database

    try:
        spreadsheet = get_google_spreadsheet()
        worksheets = spreadsheet.worksheets()
    except Exception:
        logging.exception("Nao foi possivel ler o banco de alunos da planilha Google.")
        return empty_database

    by_sheet = {}
    by_serie_turma = {}
    by_trilha = {}

    for worksheet in worksheets:
        title = (worksheet.title or "").strip()
        if not title or should_skip_student_worksheet(title):
            continue

        try:
            column_values = worksheet.col_values(2)
        except Exception:
            logging.exception("Falha ao ler coluna de estudantes da aba %s.", title)
            continue

        if len(column_values) <= 2:
            continue

        names = normalize_student_name_list(column_values[2:])
        if not names:
            continue

        by_sheet[title] = names

        regular_match = re.match(r"^([123]o ano)\s+([A-Z])$", title)
        if regular_match:
            by_serie_turma[f"{regular_match.group(1)}|{regular_match.group(2)}"] = names
        else:
            by_trilha[title] = names

    return {
        "bySheet": by_sheet,
        "bySerieTurma": by_serie_turma,
        "byTrilha": by_trilha,
    }


def merge_student_databases(local_database, google_database):
    merged = {"bySheet": {}, "bySerieTurma": {}, "byTrilha": {}}

    for key in ("bySheet", "bySerieTurma", "byTrilha"):
        combined = {}

        for source in (local_database.get(key, {}), google_database.get(key, {})):
            for group_name, names in source.items():
                current = combined.setdefault(group_name, set())
                current.update(name for name in names if (name or "").strip())

        merged[key] = {
            group_name: sorted({name.strip() for name in names}, key=normalize_text)
            for group_name, names in combined.items()
        }

    return merged


def build_track_options(student_database):
    options = [{"label": "Turma regular (sem trilha)", "value": ""}]
    track_names = set(student_database.get("byTrilha", {}).keys())

    for sheet_name in student_database.get("bySheet", {}):
        if not re.match(r"^[123]o ano\s+[A-Z]$", (sheet_name or "").strip()):
            track_names.add(sheet_name)

    track_names = sorted(track_names, key=normalize_text)
    options.extend({"label": track_name, "value": track_name} for track_name in track_names)
    return options


def build_class_options(student_database):
    classes = set()

    for sheet_name in student_database.get("bySheet", {}):
        match = re.match(r"^[123]o ano\s+([A-Z])$", (sheet_name or "").strip())
        if match:
            classes.add(match.group(1).upper())

    for key in student_database.get("bySerieTurma", {}):
        parts = key.split("|", 1)
        if len(parts) == 2 and parts[1].strip():
            classes.add(parts[1].strip().upper())

    for track_name in student_database.get("byTrilha", {}):
        _, track_class = infer_grade_class_from_track(track_name)
        if track_class:
            classes.add(track_class)

    return [{"label": student_class, "value": student_class} for student_class in sorted(classes)]


def build_student_name_options(track_name, student_grade, student_class):
    names = set()

    preferred_sheet = ""
    if track_name and track_name in STUDENT_DATABASE.get("bySheet", {}):
        preferred_sheet = track_name
    elif student_grade and student_class:
        candidate_sheet = f"{student_grade.strip()} {student_class.strip().upper()}"
        if candidate_sheet in STUDENT_DATABASE.get("bySheet", {}):
            preferred_sheet = candidate_sheet

    if preferred_sheet:
        names.update(STUDENT_DATABASE.get("bySheet", {}).get(preferred_sheet, []))

    if track_name:
        names.update(STUDENT_DATABASE.get("byTrilha", {}).get(track_name, []))

    if student_grade and student_class:
        key = f"{student_grade.strip()}|{student_class.strip().upper()}"
        names.update(STUDENT_DATABASE.get("bySerieTurma", {}).get(key, []))

    unique_names = sorted({name.strip() for name in names if (name or "").strip()}, key=normalize_text)
    return [{"label": name, "value": name} for name in unique_names]


STUDENT_DATABASE_LOCAL = load_student_database()
STUDENT_DATABASE = STUDENT_DATABASE_LOCAL
TRACK_OPTIONS = build_track_options(STUDENT_DATABASE)
CLASS_OPTIONS = build_class_options(STUDENT_DATABASE)


def serialize_json_value(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Tipo nao serializavel: {type(value)!r}")


def is_google_sheets_configured():
    return bool(
        (os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or "").strip()
        or (os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "").strip()
    )


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
    service_account_json = (os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or "").strip()
    service_account_file = (os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "").strip()

    if service_account_json:
        return parse_service_account_json(service_account_json)

    if service_account_file:
        with open(service_account_file, "r", encoding="utf-8") as file_obj:
            return json.load(file_obj)

    raise RuntimeError("Credenciais do Google Sheets nao configuradas.")


@lru_cache(maxsize=1)
def get_google_sheets_client():
    # O cache evita recriar autenticação a cada envio para a planilha.
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


def get_google_worksheet_with_headers(worksheet_name, headers):
    # Esta função garante duas coisas: que a aba exista e que a primeira linha tenha o cabeçalho esperado.
    spreadsheet = get_google_spreadsheet()

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows=2000,
            cols=max(26, len(headers) + 4),
        )

    if not worksheet.row_values(1):
        worksheet.append_row(headers, value_input_option="USER_ENTERED")

    return worksheet


def get_google_spreadsheet():
    client = get_google_sheets_client()
    spreadsheet_id = (os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID") or "").strip()
    spreadsheet_name = (os.getenv("GOOGLE_SHEETS_SPREADSHEET_NAME") or "Notas CEAN 2026").strip()
    return open_google_spreadsheet(client, spreadsheet_id, spreadsheet_name)


def get_google_worksheet():
    worksheet_name = (os.getenv("GOOGLE_SHEETS_WORKSHEET_NAME") or "app web").strip()
    return get_google_worksheet_with_headers(worksheet_name, SHEET_HEADERS)


def get_google_final_results_worksheet():
    worksheet_name = (os.getenv("GOOGLE_SHEETS_RESULTS_WORKSHEET_NAME") or "app web resultados").strip()
    return get_google_worksheet_with_headers(worksheet_name, FINAL_SESSION_HEADERS)


def refresh_student_database_from_sources():
    global STUDENT_DATABASE
    global TRACK_OPTIONS
    global CLASS_OPTIONS

    google_database = load_student_database_from_google_sheets()
    STUDENT_DATABASE = merge_student_databases(STUDENT_DATABASE_LOCAL, google_database)
    TRACK_OPTIONS = build_track_options(STUDENT_DATABASE)
    CLASS_OPTIONS = build_class_options(STUDENT_DATABASE)


refresh_student_database_from_sources()


def send_submission_to_google_sheets(submission):
    if not is_google_sheets_configured():
        return False, "Integracao com Google Sheets nao configurada neste deploy."

    try:
        worksheet = get_google_worksheet()
        row = [submission.get(header, "") for header in SHEET_HEADERS]
        worksheet.append_row(row, value_input_option="USER_ENTERED")
        return True, f"Dados enviados para a planilha {worksheet.spreadsheet.title} / {worksheet.title}."
    except Exception as exc:
        logging.exception("Falha ao enviar submissao para Google Sheets.")
        reason = str(exc).strip() or exc.__class__.__name__
        return False, f"Registro na planilha nao concluido: {reason}"


def send_final_session_to_google_sheets(payload):
    if not is_google_sheets_configured():
        return False, "Integracao com Google Sheets nao configurada neste deploy."

    try:
        worksheet = get_google_final_results_worksheet()
        row = [payload.get(header, "") for header in FINAL_SESSION_HEADERS]
        worksheet.append_row(row, value_input_option="USER_ENTERED")
        return True, f"Dados enviados para a planilha {worksheet.spreadsheet.title} / {worksheet.title}."
    except Exception as exc:
        logging.exception("Falha ao enviar resultados finais para Google Sheets.")
        reason = str(exc).strip() or exc.__class__.__name__
        return False, f"planilha: {reason}"


def parse_stage_details(value):
    # Os detalhes das etapas chegam serializados em JSON; aqui voltam para uma lista de dicionários Python.
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
    # A nota da turma é derivada da média das pontuações registradas na sessão de exercícios.
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


def sanitize_worksheet_title(value):
    cleaned = re.sub(r"[:\\/?*\[\]]", " ", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return (cleaned or "Turma")[:100]


def format_grade_10(value):
    try:
        numeric_value = round(float(value), 2)
    except (TypeError, ValueError):
        return ""

    if abs(numeric_value - round(numeric_value)) < 1e-9:
        return int(round(numeric_value))

    return float(f"{numeric_value:.2f}".rstrip("0").rstrip("."))


def is_bimester_label(value):
    return normalize_text(value).strip() in {
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


def ensure_worksheet_size(worksheet, min_rows, min_cols):
    if worksheet.row_count < min_rows:
        worksheet.add_rows(min_rows - worksheet.row_count)
    if worksheet.col_count < min_cols:
        worksheet.add_cols(min_cols - worksheet.col_count)


def get_or_create_class_worksheet(spreadsheet, title):
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=100, cols=30)


def get_class_header_rows(worksheet):
    # Esta é uma função defensiva: ela lê a estrutura atual da aba e evita continuar se o formato parecer corrompido.
    values = worksheet.get_all_values()
    if not values:
        ensure_worksheet_size(worksheet, 2, 2)
        worksheet.update(range_name="A1:B2", values=[["Nº", "ESTUDANTE"], ["", "pesos"]])
        return ["Nº", "ESTUDANTE"], ["", "pesos"]

    header_row = list(values[0])
    weight_row = list(values[1]) if len(values) > 1 else []

    if normalize_text(header_row[0] if header_row else "").strip() == "student_name":
        raise RuntimeError(
            f"A aba '{worksheet.title}' parece ter sido sobrescrita por um formato antigo. "
            "Restaure a aba pelo historico de versoes do Google Sheets antes de continuar."
        )

    if len(header_row) < 2:
        header_row += [""] * (2 - len(header_row))
    if len(weight_row) < 2:
        weight_row += [""] * (2 - len(weight_row))

    updates = []
    if normalize_text(header_row[0]).strip() != "no":
        header_row[0] = "Nº"
        updates.append(("A1", "Nº"))
    if normalize_text(header_row[1]).strip() != "estudante":
        header_row[1] = "ESTUDANTE"
        updates.append(("B1", "ESTUDANTE"))
    if normalize_text(weight_row[1]).strip() != "pesos":
        weight_row[1] = "pesos"
        updates.append(("B2", "pesos"))

    for cell, value in updates:
        worksheet.update_acell(cell, value)

    return header_row, weight_row


def build_class_student_row_map(worksheet):
    names = worksheet.col_values(2)
    student_rows = {}
    for row_index, value in enumerate(names[2:], start=3):
        student_name = " ".join((value or "").split()).strip()
        if student_name:
            student_rows[normalize_text(student_name).strip()] = row_index
    return student_rows


def append_missing_class_students(worksheet, summary_rows, student_rows):
    # Se um estudante ainda não existir na aba da turma, ele é acrescentado antes de gravar a nota da simulação.
    existing_names = worksheet.col_values(2)
    next_row = max(len(existing_names) + 1, 3)
    next_number = max(len(student_rows) + 1, 1)
    appended = []

    for row in summary_rows:
        student_name = " ".join((row.get("student_name", "") or "").split()).strip()
        student_key = normalize_text(student_name).strip()
        if not student_name or student_key in student_rows:
            continue

        appended.append([str(next_number), student_name])
        student_rows[student_key] = next_row
        next_row += 1
        next_number += 1

    if appended:
        ensure_worksheet_size(worksheet, next_row - 1, 2)
        start = len(existing_names) + 1
        end = start + len(appended) - 1
        worksheet.update(range_name=f"A{start}:B{end}", values=appended)

    return student_rows


def find_bimester_start(header_row, bimester_label):
    target = normalize_text(bimester_label).strip()
    for index, value in enumerate(header_row):
        if normalize_text(value).strip() == target:
            return index
    return None


def get_next_bimester_start(header_row, start_index):
    for index in range(start_index + 1, len(header_row)):
        if is_bimester_label(header_row[index]):
            return index
    return None


def ensure_bimester_and_simulation_column(worksheet, header_row, weight_row, bimester_label):
    # O objetivo aqui é localizar ou criar a coluna "Soma de Cores" dentro do bloco certo do bimestre.
    start_index = find_bimester_start(header_row, bimester_label)
    if start_index is None:
        start_index = len(header_row)
        ensure_worksheet_size(worksheet, 2, start_index + 2)
        header_row.extend([""] * max(0, start_index + 2 - len(header_row)))
        weight_row.extend([""] * max(0, start_index + 2 - len(weight_row)))
        start_letter = column_index_to_letter(start_index + 1)
        end_letter = column_index_to_letter(start_index + 2)
        worksheet.update(
            range_name=f"{start_letter}1:{end_letter}2",
            values=[[bimester_label, CLASS_SHEET_SIMULATION_TITLE], ["", ""]],
        )
        header_row[start_index] = bimester_label
        header_row[start_index + 1] = CLASS_SHEET_SIMULATION_TITLE
        return start_index, start_index + 1

    next_bimester_start = get_next_bimester_start(header_row, start_index)
    search_end = next_bimester_start if next_bimester_start is not None else len(header_row)
    simulation_index = None
    empty_slots = []

    for index in range(start_index + 1, search_end):
        normalized_header = normalize_text(header_row[index]).strip()
        if normalized_header == normalize_text(CLASS_SHEET_SIMULATION_TITLE).strip():
            simulation_index = index
            break
        if not (header_row[index] or "").strip():
            empty_slots.append(index)

    if simulation_index is None and empty_slots:
        simulation_index = empty_slots[0]
        column_letter = column_index_to_letter(simulation_index + 1)
        worksheet.update(range_name=f"{column_letter}1:{column_letter}2", values=[[CLASS_SHEET_SIMULATION_TITLE], [""]])
        header_row[simulation_index] = CLASS_SHEET_SIMULATION_TITLE

    if simulation_index is None:
        if next_bimester_start is not None:
            raise RuntimeError(
                f"A aba '{worksheet.title}' nao tem espaco livre no bloco de {bimester_label} para adicionar a coluna {CLASS_SHEET_SIMULATION_TITLE}."
            )

        simulation_index = len(header_row)
        ensure_worksheet_size(worksheet, 2, simulation_index + 1)
        header_row.append(CLASS_SHEET_SIMULATION_TITLE)
        if len(weight_row) < len(header_row):
            weight_row.extend([""] * (len(header_row) - len(weight_row)))
        column_letter = column_index_to_letter(simulation_index + 1)
        worksheet.update(range_name=f"{column_letter}1:{column_letter}2", values=[[CLASS_SHEET_SIMULATION_TITLE], [""]])

    return start_index, simulation_index


def update_class_simulation_column(worksheet, simulation_index, summary_rows, student_rows):
    # Aqui escrevemos apenas a coluna da simulação, sem apagar o restante da planilha da turma.
    last_row = max(student_rows.values(), default=2)
    ensure_worksheet_size(worksheet, last_row, simulation_index + 1)
    current_values = worksheet.col_values(simulation_index + 1)
    column_values = list(current_values) + [""] * max(0, last_row - len(current_values))

    if len(column_values) < 2:
        column_values += [""] * (2 - len(column_values))
    column_values[0] = CLASS_SHEET_SIMULATION_TITLE
    column_values[1] = ""

    for row in summary_rows:
        student_key = normalize_text(row.get("student_name", "")).strip()
        target_row = student_rows.get(student_key)
        if target_row is None:
            continue
        while len(column_values) < target_row:
            column_values.append("")
        column_values[target_row - 1] = format_grade_10(row.get("final_grade_10"))

    col_letter = column_index_to_letter(simulation_index + 1)
    worksheet.update(range_name=f"{col_letter}1:{col_letter}{len(column_values)}", values=[[value] for value in column_values])


def update_class_bimester_total_column(worksheet, total_index, simulation_indexes, student_rows):
    # Depois de atualizar a coluna da simulação, recalculamos a fórmula do total do bimestre.
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


def write_class_sheet_worksheet(spreadsheet, worksheet_title, summary_rows):
    # Esta função coordena toda a atualização segura da aba da turma, preservando outras avaliações já existentes.
    worksheet = get_or_create_class_worksheet(spreadsheet, worksheet_title)
    header_row, weight_row = get_class_header_rows(worksheet)
    student_rows = build_class_student_row_map(worksheet)
    student_rows = append_missing_class_students(worksheet, summary_rows, student_rows)

    rows_by_bimester = {}
    for row in summary_rows:
        bimester_label = (row.get("bimester") or "").strip()
        if not bimester_label:
            continue
        rows_by_bimester.setdefault(bimester_label, []).append(row)

    for bimester_label, bimester_rows in rows_by_bimester.items():
        total_index, simulation_index = ensure_bimester_and_simulation_column(worksheet, header_row, weight_row, bimester_label)
        update_class_simulation_column(worksheet, simulation_index, bimester_rows, student_rows)

        refreshed_header = worksheet.row_values(1)
        next_bimester_start = get_next_bimester_start(refreshed_header, total_index)
        search_end = next_bimester_start if next_bimester_start is not None else len(refreshed_header)
        simulation_indexes = [
            index
            for index in range(total_index + 1, search_end)
            if (refreshed_header[index] or "").strip() and not is_bimester_label(refreshed_header[index])
        ]
        update_class_bimester_total_column(worksheet, total_index, simulation_indexes, student_rows)

    return worksheet


def build_class_sheet_summary_row(payload):
    # O payload final da sessão ainda é muito rico; aqui extraímos só o que a aba da turma precisa: nome, bimestre e nota.
    stage_details = parse_stage_details(payload.get("detalhes_exercicios"))
    average_score_100 = compute_stage_average_100(stage_details)
    final_grade_10 = round(average_score_100 / 10.0, 2)
    return {
        "student_name": (payload.get("estudante") or payload.get("nome_aluno") or "").strip(),
        "bimester": (payload.get("bimestre") or "").strip(),
        "final_grade_10": final_grade_10,
    }


def send_final_session_to_class_worksheet(payload):
    # Este envio é separado do registro bruto para que a aba da turma continue com sua própria estrutura.
    if not is_google_sheets_configured():
        return False, "Integracao com Google Sheets nao configurada neste deploy."

    group_name = build_group_name(payload.get("serie", ""), payload.get("turma", "")).strip()
    student_name = (payload.get("estudante") or payload.get("nome_aluno") or "").strip()
    bimester = (payload.get("bimestre") or "").strip()

    if not group_name or normalize_text(group_name) == "nao informado":
        return False, "serie/turma nao informadas para atualizar a aba da turma"
    if not student_name or normalize_text(student_name) == "nao informado":
        return False, "nome do estudante nao informado para atualizar a aba da turma"
    if not bimester or normalize_text(bimester) == "nao informado":
        return False, "bimestre nao informado para atualizar a aba da turma"

    try:
        spreadsheet = get_google_spreadsheet()
        worksheet_title = sanitize_worksheet_title(group_name)
        summary_row = build_class_sheet_summary_row(payload)
        write_class_sheet_worksheet(spreadsheet, worksheet_title, [summary_row])
        return True, f"Aba da turma atualizada em {worksheet_title}."
    except Exception as exc:
        logging.exception("Falha ao atualizar a aba da turma.")
        reason = str(exc).strip() or exc.__class__.__name__
        return False, reason


def post_json_to_apps_script(url, data):
    try:
        payload = json.dumps(data, ensure_ascii=False, default=serialize_json_value).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="ignore").strip()
            return True, body or f"HTTP {getattr(response, 'status', 200)}"
    except Exception as exc:
        logging.exception("Falha ao enviar dados para Apps Script.")
        reason = str(exc).strip() or exc.__class__.__name__
        return False, reason


def build_final_session_payload(
    session_data,
    student_name,
    student_track,
    student_grade,
    student_class,
    student_bimester,
    student_email,
    criticism,
    suggestion,
    final_conclusion,
):
    # O payload final reúne identidade do estudante, resumo da sessão e um retrato das etapas resolvidas.
    exercises = list(session_data.get("exercises", []))
    results = list(session_data.get("results", []))
    total = len(exercises)
    correct = sum(1 for item in results if item.get("correct"))
    skipped = int(session_data.get("skipped_questions", 0))
    total_attempts = sum(int(item.get("attempts", 0)) for item in results)
    score_percent = int(round((correct / total) * 100)) if total else 0
    exercise_snapshot = []

    for index, exercise in enumerate(exercises):
        result = results[index] if index < len(results) else {}
        exercise_snapshot.append({
            "ordem": index + 1,
            "tipo": exercise.get("type", ""),
            "titulo": exercise.get("title", ""),
            "resultado": "acerto" if result.get("correct") else "pulado" if result.get("skipped") else "pendente",
            "tentativas": int(result.get("attempts", 0)),
            "score": int(result.get("score", 0)),
        })

    return {
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "trilha": (student_track or "").strip() or "Turma regular",
        "serie": (student_grade or "").strip() or "Nao informado",
        "turma": (student_class or "").strip() or "Nao informado",
        "bimestre": (student_bimester or "").strip() or "Nao informado",
        "estudante": (student_name or "").strip() or "Nao informado",
        "simulacao": SIMULATION_NAME,
        "questoes_puladas": skipped,
        "acertos_erros": f"{correct}/{max(total - correct, 0)}",
        "nota": score_percent,
        "conclusao": (final_conclusion or "").strip(),
        "criticas": (criticism or "").strip(),
        "sugestoes": (suggestion or "").strip(),
        "email": (student_email or "").strip(),
        "to_email": PROFESSOR_EMAIL,
        "nome_aluno": (student_name or "").strip() or "Nao informado",
        "acertos": correct,
        "data_envio": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "total_questoes": total,
        "tentativas_totais": total_attempts,
        "detalhes_exercicios": json.dumps(exercise_snapshot, ensure_ascii=False),
    }


def send_final_session_results(payload, student_email):
    # O envio completo é um encadeamento: salva a sessão, atualiza a turma e dispara as comunicações.
    messages = []
    success = True

    sheet_ok, sheet_message = send_final_session_to_google_sheets(payload)
    success = success and sheet_ok
    messages.append("planilha ok" if sheet_ok else f"planilha: {sheet_message}")

    is_visitor = normalize_text(payload.get("serie", "")) == "visitante"

    if is_visitor:
        class_ok, class_message = True, "modo visitante: sem atualizacao de aba da turma"
    else:
        class_ok, class_message = send_final_session_to_class_worksheet(payload)
    success = success and class_ok
    messages.append("aba da turma ok" if class_ok else f"aba turma: {class_message}")

    email_ok, email_message = post_json_to_apps_script(EMAIL_SCRIPT_URL, payload)
    success = success and email_ok
    messages.append("email do professor ok" if email_ok else f"email professor: {email_message}")

    student_email = (student_email or "").strip()
    if student_email:
        student_copy = dict(payload)
        student_copy["to_email"] = student_email
        student_copy["mensagem"] = (
            f"Confirmação de envio - {SIMULATION_NAME}\n"
            f"Nota: {payload.get('nota', 0)}\n"
            f"Acertos: {payload.get('acertos', 0)}/{payload.get('total_questoes', 0)}\n"
            f"Questões puladas: {payload.get('questoes_puladas', 0)}"
        )
        copy_ok, copy_message = post_json_to_apps_script(EMAIL_SCRIPT_URL, student_copy)
        success = success and copy_ok
        messages.append("copia para estudante ok" if copy_ok else f"copia estudante: {copy_message}")

    return success, " | ".join(messages)


def append_feedback_detail(feedback, detail):
    if not detail:
        return feedback

    updated_feedback = dict(feedback)
    updated_feedback["details"] = list(updated_feedback.get("details", [])) + [detail]
    return updated_feedback


def build_exercise_submission(
    exercise,
    metrics,
    answer_text,
    total_score,
    metric_summary,
    result_label,
    table_data,
    history_data,
    student_name,
    student_group,
    submitted_at,
):
    return {
        "timestamp": submitted_at.isoformat(timespec="seconds"),
        "student_name": (student_name or "").strip() or "Nao informado",
        "student_group": (student_group or "").strip() or "Nao informado",
        "exercise_id": exercise.get("id", ""),
        "exercise_type": exercise.get("type", ""),
        "exercise_title": exercise.get("title", ""),
        "difficulty": exercise.get("difficulty", "fundamental"),
        "result": result_label,
        "score": int(total_score),
        "metric_summary": metric_summary,
        "max_diff": round(float(metrics.get("max_diff", 0.0)), 6),
        "smoothing_window": int(metrics.get("smoothing_window", DEFAULT_SMOOTHING)),
        "freq_delta": int(metrics.get("freq_delta", DEFAULT_FREQ_DELTA)),
        "has_optimization": "sim" if metrics.get("has_optimization") else "nao",
        "active_count1": int(metrics.get("active_count1", 0)),
        "active_count2": int(metrics.get("active_count2", 0)),
        "answer_text": answer_text or "",
        "table_data_json": json.dumps(table_data or [], ensure_ascii=False, default=serialize_json_value),
        "history_data_json": json.dumps(history_data or {}, ensure_ascii=False, default=serialize_json_value),
    }


def generate_fourier_equation(amps, wave_name):
    non_zero_indices = np.where(np.abs(amps) > 1e-12)[0]
    if len(non_zero_indices) == 0:
        return f"{wave_name}: y(t) = 0"

    terms = []
    for index in non_zero_indices:
        amp = float(amps[index])
        freq = int(FREQS[index])
        sign = "+" if amp >= 0 else "-"
        abs_amp = abs(amp)
        if np.isclose(abs_amp, 1.0):
            term = f"{sign} sin(2*pi*{freq}*t)"
        else:
            term = f"{sign} {abs_amp:.3f}*sin(2*pi*{freq}*t)"
        terms.append(term)

    if terms[0].startswith("+ "):
        terms[0] = terms[0][2:]

    grouped_terms = []
    for start in range(0, len(terms), 3):
        grouped_terms.append(" ".join(terms[start:start + 3]))

    return f"{wave_name}: y(t) = " + "\n    ".join(grouped_terms)


def frequency_to_wavelength_nm(freq_thz):
    return 299792.458 / freq_thz


def clamp_to_visible_wavelength(wavelength_nm):
    return float(np.clip(wavelength_nm, 380.0, 780.0))


def frequency_to_rgb(freq_thz):
    wavelength_nm = clamp_to_visible_wavelength(frequency_to_wavelength_nm(freq_thz))

    if 380 <= wavelength_nm < 440:
        red = -(wavelength_nm - 440) / (440 - 380)
        green = 0.0
        blue = 1.0
    elif wavelength_nm < 490:
        red = 0.0
        green = (wavelength_nm - 440) / (490 - 440)
        blue = 1.0
    elif wavelength_nm < 510:
        red = 0.0
        green = 1.0
        blue = -(wavelength_nm - 510) / (510 - 490)
    elif wavelength_nm < 580:
        red = (wavelength_nm - 510) / (580 - 510)
        green = 1.0
        blue = 0.0
    elif wavelength_nm < 645:
        red = 1.0
        green = -(wavelength_nm - 645) / (645 - 580)
        blue = 0.0
    else:
        red = 1.0
        green = 0.0
        blue = 0.0

    if 380 <= wavelength_nm < 420:
        factor = 0.3 + 0.7 * (wavelength_nm - 380) / (420 - 380)
    elif wavelength_nm < 701:
        factor = 1.0
    elif wavelength_nm <= 780:
        factor = 0.3 + 0.7 * (780 - wavelength_nm) / (780 - 700)
    else:
        factor = 0.0

    gamma = 0.8
    rgb = np.array([red, green, blue]) * factor
    rgb = np.where(rgb > 0, rgb ** gamma, 0)
    return np.clip(rgb, 0, 1)


def normalize_rgb(rgb):
    peak = np.max(rgb)
    if peak > 1e-12:
        return rgb / peak
    return rgb


def compute_emitted_rgb(amps):
    weights = np.abs(amps)
    total = np.sum(weights)
    if total <= 1e-12:
        return np.array([0.0, 0.0, 0.0])
    colors = np.array([frequency_to_rgb(freq) for freq in FREQS])
    emitted_rgb = np.sum(colors * weights[:, None], axis=0) / total
    return np.clip(emitted_rgb, 0, 1)


def compute_display_rgb_visual(amps):
    return np.clip(normalize_rgb(compute_emitted_rgb(amps)), 0, 1)


def compute_display_rgb_palette(amps):
    return np.clip(compute_emitted_rgb(amps), 0, 1)


def rgb_to_hex(rgb):
    values = np.clip(np.round(rgb * 255), 0, 255).astype(int)
    return "#{:02X}{:02X}{:02X}".format(*values)


def format_rgb(rgb):
    return f"{rgb_to_hex(rgb)} | R={rgb[0]:.2f} G={rgb[1]:.2f} B={rgb[2]:.2f}"


def has_valid_optimization_result(current1, current2, history_data):
    if not history_data or not bool(history_data.get("has_optimization", False)):
        return False

    after1 = np.array(history_data.get("after1", current1.tolist()), dtype=float)
    after2 = np.array(history_data.get("after2", current2.tolist()), dtype=float)
    return (
        after1.shape == current1.shape
        and after2.shape == current2.shape
        and np.allclose(current1, after1, atol=1e-12)
        and np.allclose(current2, after2, atol=1e-12)
    )


GRAPH_CONFIG = {
    "displayModeBar": False,
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": False,
    "doubleClick": False,
}


def lock_figure_interaction(figure):
    figure.update_xaxes(fixedrange=True)
    figure.update_yaxes(fixedrange=True)
    return figure


def build_main_figure(amps1, amps2, smoothing_window=DEFAULT_SMOOTHING, time_window_fs=DEFAULT_TIME_WINDOW_FS):
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    envelope1 = compute_envelope(wave1, smoothing_window)
    envelope2 = compute_envelope(wave2, smoothing_window)
    diff = envelope1 - envelope2
    envelope_title = "Envelopes"
    sanitized_window = int(time_window_fs or DEFAULT_TIME_WINDOW_FS)
    if sanitized_window not in TIME_WINDOW_OPTIONS:
        sanitized_window = DEFAULT_TIME_WINDOW_FS
    tick_map = {200: 25, 150: 25, 100: 20, 50: 10}
    axis_tick = tick_map.get(sanitized_window, 25)

    figure = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Onda 1",
            "Onda 2",
            envelope_title,
            "Diferença",
        ),
        vertical_spacing=0.22,
        horizontal_spacing=0.12,
    )

    figure.add_trace(
        go.Scatter(x=TIME_FS, y=wave1, mode="lines", name="Onda 1", line=dict(color="royalblue")),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Scatter(x=TIME_FS, y=wave2, mode="lines", name="Onda 2", line=dict(color="darkorange")),
        row=1,
        col=2,
    )
    figure.add_trace(
        go.Scatter(x=TIME_FS, y=envelope1, mode="lines", name="Envelope 1", line=dict(color="royalblue")),
        row=2,
        col=1,
    )
    figure.add_trace(
        go.Scatter(x=TIME_FS, y=envelope2, mode="lines", name="Envelope 2", line=dict(color="darkorange")),
        row=2,
        col=1,
    )
    figure.add_trace(
        go.Scatter(x=TIME_FS, y=diff, mode="lines", name="Delta envelopes", line=dict(color="green")),
        row=2,
        col=2,
    )
    figure.add_hline(y=0, line_width=1, line_color="black", opacity=0.5, row=2, col=2)

    for col in [1, 2]:
        figure.update_xaxes(range=[0, sanitized_window], dtick=axis_tick, row=1, col=col)
        figure.update_xaxes(
            title_text="Tempo (fs)",
            title_standoff=10,
            range=[0, sanitized_window],
            dtick=axis_tick,
            row=2,
            col=col,
        )

    for row, col in [(1, 1), (1, 2), (2, 1), (2, 2)]:
        figure.update_yaxes(row=row, col=col)

    figure.update_layout(
        height=820,
        template="plotly_white",
        margin=dict(l=30, r=30, t=110, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5),
    )
    return lock_figure_interaction(figure)


def build_intensity_figure(amps1, amps2):
    figure = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Amplitude 1",
            "Amplitude 2",
        ),
        horizontal_spacing=0.1,
    )

    figure.add_trace(
        go.Bar(
            x=FREQS,
            y=amps1,
            name="Onda 1",
            marker=dict(color=[rgb_to_hex(normalize_rgb(frequency_to_rgb(freq))) for freq in FREQS]),
            hovertemplate="%{x} THz<br>Amplitude: %{y:.1f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Bar(
            x=FREQS,
            y=amps2,
            name="Onda 2",
            marker=dict(color=[rgb_to_hex(normalize_rgb(frequency_to_rgb(freq))) for freq in FREQS]),
            hovertemplate="%{x} THz<br>Amplitude: %{y:.1f}<extra></extra>",
        ),
        row=1,
        col=2,
    )

    for col in [1, 2]:
        figure.update_xaxes(title_text="Frequência (THz)", dtick=40, row=1, col=col)
        figure.update_yaxes(title_text=None, range=[AMP_MIN, AMP_MAX], row=1, col=col)

    figure.update_layout(
        height=360,
        template="plotly_white",
        margin=dict(l=30, r=30, t=60, b=30),
        showlegend=False,
    )
    return lock_figure_interaction(figure)


def build_summary(amps1, amps2, smoothing_window=DEFAULT_SMOOTHING, freq_delta=DEFAULT_FREQ_DELTA):
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    envelope1 = compute_envelope(wave1, smoothing_window)
    envelope2 = compute_envelope(wave2, smoothing_window)
    max_diff = float(np.max(np.abs(envelope1 - envelope2)))
    return html.Ul(
        [
            html.Li(f"Pico da Onda 1: {np.max(np.abs(wave1)):.3f}"),
            html.Li(f"Pico da Onda 2: {np.max(np.abs(wave2)):.3f}"),
            html.Li(f"Diferença máxima entre envelopes: {max_diff:.3f}"),
            html.Li("Envelopes: comparam a intensidade instantânea das duas ondas após o cálculo de Hilbert."),
            html.Li("Diferença: mostra quanto os envelopes ainda estão afastados em cada instante de tempo."),
            html.Li(f"Componentes ativas na Onda 1: {int(np.sum(np.abs(amps1) > 1e-12))}"),
            html.Li(f"Componentes ativas na Onda 2: {int(np.sum(np.abs(amps2) > 1e-12))}"),
            html.Li(f"Suavização de Hilbert: {sanitize_smoothing_window(smoothing_window, len(T))} ponto(s)"),
            html.Li(f"Janela da otimização em delta f: {format_frequency_delta(freq_delta)}"),
        ],
        style={"margin": "0", "paddingLeft": "18px", "lineHeight": "1.7"},
    )


def build_color_scale_figure(mode):
    if mode == "visual":
        colors = [rgb_to_hex(normalize_rgb(frequency_to_rgb(freq))) for freq in FREQS]
        title = "Escala de cores por frequência no modo RGB visual"
    else:
        colors = [rgb_to_hex(frequency_to_rgb(freq)) for freq in FREQS]
        title = "Escala de cores por frequência no modo paleta em RGB"

    figure = go.Figure(
        go.Bar(
            x=[str(freq) for freq in FREQS],
            y=[1] * len(FREQS),
            marker_color=colors,
            hovertext=[f"{freq} THz | {frequency_to_wavelength_nm(freq):.1f} nm" for freq in FREQS],
            hoverinfo="text",
        )
    )
    figure.update_layout(
        title=title,
        template="plotly_white",
        height=260,
        margin=dict(l=30, r=30, t=60, b=80),
        yaxis=dict(visible=False),
        xaxis=dict(title="Frequência (THz)"),
        bargap=0,
        showlegend=False,
    )
    return lock_figure_interaction(figure)


def build_rgb_card(amps, wave_name, stage_name, mode):
    emitted_rgb = compute_emitted_rgb(amps)
    if mode == "visual":
        displayed_rgb = compute_display_rgb_visual(amps)
        mode_label = "RGB visual renormalizado"
    else:
        displayed_rgb = compute_display_rgb_palette(amps)
        mode_label = "Paleta em RGB"

    background = rgb_to_hex(displayed_rgb)
    text_color = "white" if np.mean(displayed_rgb) < 0.45 else "black"
    return html.Div(
        [
            html.Strong(f"{wave_name} | {stage_name}"),
            html.Div(mode_label, style={"marginTop": "6px"}),
            html.Div(f"Emite: {format_rgb(emitted_rgb)}", style={"marginTop": "10px"}),
            html.Div(f"Mostra: {format_rgb(displayed_rgb)}", style={"marginTop": "4px"}),
        ],
        style={
            "background": background,
            "color": text_color,
            "padding": "16px",
            "borderRadius": "12px",
            "border": "1px solid rgba(0, 0, 0, 0.18)",
            "boxShadow": "0 8px 18px rgba(15, 23, 42, 0.08)",
            "lineHeight": "1.6",
            "minHeight": "140px",
        },
    )


def build_pending_rgb_card(wave_name, stage_name):
    return html.Div(
        [
            html.Strong(f"{wave_name} | {stage_name}"),
            html.Div("Aguardando otimização", style={"marginTop": "6px"}),
            html.Div("Este cartão só é preenchido depois que a otimização é executada.", style={"marginTop": "10px"}),
        ],
        style={
            "background": "#e2e8f0",
            "color": "#334155",
            "padding": "16px",
            "borderRadius": "12px",
            "border": "1px dashed rgba(51, 65, 85, 0.35)",
            "boxShadow": "0 8px 18px rgba(15, 23, 42, 0.04)",
            "lineHeight": "1.6",
            "minHeight": "140px",
        },
    )


def optimize_amplitudes(
    initial_amps1,
    initial_amps2,
    max_iterations,
    smoothing_window=DEFAULT_SMOOTHING,
    freq_delta=DEFAULT_FREQ_DELTA,
):
    class OptimizationStopped(Exception):
        def __init__(self, amps_flat, diff, reason):
            self.amps_flat = amps_flat.copy()
            self.diff = diff
            self.reason = reason

    optimize_masks = build_optimization_masks(initial_amps1, initial_amps2, freq_delta)
    optimize_mask1, optimize_mask2 = optimize_masks
    free_count1 = int(np.sum(optimize_mask1))
    free_count2 = int(np.sum(optimize_mask2))
    free_count = free_count1 + free_count2

    if free_count == 0:
        final_diff = max_envelope_difference(initial_amps1, initial_amps2, smoothing_window)
        return initial_amps1.copy(), initial_amps2.copy(), final_diff, "blocked"

    def cost_function(amps_flat):
        # Durante a busca, o custo medido é a distância entre envelopes, não entre as ondas brutas.
        amps1, amps2 = merge_optimized_values(amps_flat, initial_amps1, initial_amps2, optimize_masks)
        return max_envelope_difference_fast(amps1, amps2, smoothing_window)

    iteration_counter = {"count": 0}

    def iteration_callback(xk):
        iteration_counter["count"] += 1
        amps1, amps2 = merge_optimized_values(xk, initial_amps1, initial_amps2, optimize_masks)
        current_diff = max_envelope_difference_fast(amps1, amps2, smoothing_window)
        if current_diff <= TARGET_DIFF:
            displayed_diff = max_envelope_difference(amps1, amps2, smoothing_window)
            if displayed_diff <= TARGET_DIFF:
                raise OptimizationStopped(xk, displayed_diff, "target")
        if iteration_counter["count"] >= max_iterations:
            displayed_diff = max_envelope_difference(amps1, amps2, smoothing_window)
            raise OptimizationStopped(xk, displayed_diff, "limit")

    x0 = np.concatenate([initial_amps1[optimize_mask1], initial_amps2[optimize_mask2]])
    bounds = [(AMP_MIN, AMP_MAX) for _ in range(free_count)]

    initial_diff = max_envelope_difference_fast(initial_amps1, initial_amps2, smoothing_window)
    if initial_diff <= TARGET_DIFF:
        final_diff = max_envelope_difference(initial_amps1, initial_amps2, smoothing_window)
        if final_diff <= TARGET_DIFF:
            return initial_amps1.copy(), initial_amps2.copy(), final_diff, "target"

    try:
        # L-BFGS-B lida bem com amplitudes contínuas e com limites mínimo/máximo em cada variável.
        result = minimize(
            cost_function,
            x0,
            method="L-BFGS-B",
            bounds=bounds,
            callback=iteration_callback,
            options={"maxiter": int(max_iterations)},
        )
        final_amps1, final_amps2 = merge_optimized_values(result.x, initial_amps1, initial_amps2, optimize_masks)
        final_diff = max_envelope_difference(final_amps1, final_amps2, smoothing_window)
        if final_diff <= TARGET_DIFF:
            reason = "target"
        elif getattr(result, "nit", 0) >= max_iterations:
            reason = "limit"
        else:
            reason = "partial"
    except OptimizationStopped as stopped:
        final_amps1, final_amps2 = merge_optimized_values(stopped.amps_flat, initial_amps1, initial_amps2, optimize_masks)
        final_diff = max_envelope_difference(final_amps1, final_amps2, smoothing_window)
        reason = stopped.reason

    return final_amps1, final_amps2, final_diff, reason


def build_hilbert_notes(smoothing_window, freq_delta):
    smoothing_window = sanitize_smoothing_window(smoothing_window, len(T))
    smoothing_text = (
        f"Suavização adicional atual: desligada (janela = {smoothing_window} ponto)."
        if smoothing_window <= 1
        else f"Suavização adicional atual: média móvel de {smoothing_window} pontos após o módulo de Hilbert."
    )
    delta_text = (
        "Janela atual da otimização: toda a faixa espectral está liberada."
        if is_frequency_delta_unrestricted(freq_delta)
        else f"Janela atual da otimização: apenas frequências dentro de +- {int(freq_delta)} THz das componentes iniciais podem variar."
    )
    return smoothing_text, delta_text


def generate_random_exercise(previous_id=None, forced_type=None):
    # Cada exercício nasce com metas numéricas e textuais para orientar uma observação diferente do simulador.
    seed = int(datetime.now().timestamp() * 1000000) % 1000000000
    rng = np.random.default_rng(seed)
    target_diff = float(rng.choice([0.35, 0.30, 0.25]))
    target_smoothing = int(rng.choice([5, 9, 13, 17]))
    target_delta = int(rng.choice([40, 60, 80, 100]))

    exercises = [
        {
            "type": "envelope-target",
            "title": "Exercicio: aproximar envelopes",
            "difficulty": "fundamental",
            "prompt": (
                f"Tente fazer os dois envelopes ficarem mais parecidos. Voce pode ajustar manualmente ou usar a otimizacao. "
                f"O objetivo e deixar a diferenca maxima menor ou igual a {target_diff:.2f}. "
                "Ao final, escreva uma conclusao bem curta dizendo o que aconteceu com a diferenca entre os envelopes."
            ),
            "checklist": [
                f"A meta e: diferenca maxima <= {target_diff:.2f}.",
                "Observe se os envelopes ficaram mais proximos ao longo do tempo.",
                "Escreva uma conclusao bem curta antes de enviar.",
            ],
            "keyword_groups": [["envelope", "envelopes"], ["diferenca", "aproximou", "reduziu"]],
            "min_keyword_groups": 0,
            "min_words": 4,
            "target_diff": target_diff,
        },
        {
            "type": "smoothing-observe",
            "title": "Exercicio: observar a suavizacao",
            "difficulty": "intermediario",
            "prompt": (
                f"Aumente a suavizacao de Hilbert para pelo menos {target_smoothing} pontos e observe com calma o grafico dos envelopes. "
                "Depois, descreva em uma frase curta o que mudou nos picos e nas variacoes mais rapidas do grafico."
            ),
            "checklist": [
                f"Ajuste o controle para suavizacao >= {target_smoothing} pontos.",
                "Descreva o efeito visual da suavizacao no grafico.",
                "Use uma explicacao curta e objetiva.",
            ],
            "keyword_groups": [["suavizacao", "suavizar", "media"], ["pico", "variacao", "oscilacao"]],
            "min_keyword_groups": 0,
            "min_words": 4,
            "target_smoothing": target_smoothing,
        },
        {
            "type": "frequency-window",
            "title": "Exercicio: limitar frequencias da otimizacao",
            "difficulty": "intermediario",
            "prompt": (
                f"Defina delta f em no maximo {target_delta} THz. Deixe pelo menos uma frequencia ativa em cada onda e execute a otimizacao. "
                "Na conclusao, explique em uma frase curta por que esse limite ajuda a evitar frequencias novas muito distantes das iniciais."
            ),
            "checklist": [
                f"Ajuste o controle para delta f <= {target_delta} THz.",
                "Mantenha ao menos uma componente ativa em cada onda.",
                "Explique a ideia da restricao espectral com suas palavras.",
            ],
            "keyword_groups": [["frequencia", "espectral", "delta"], ["distante", "janela", "restricao"]],
            "min_keyword_groups": 0,
            "min_words": 4,
            "target_delta": target_delta,
        },
        {
            "type": "color-compare",
            "title": "Exercicio: relacionar envelope e cor",
            "difficulty": "avancado",
            "prompt": (
                f"Use a otimizacao para atingir diferenca maxima menor ou igual a {target_diff:.2f}. Depois, abra o Lab RGB e compare os cartoes Antes da otimizacao e Depois da otimizacao. "
                "Na conclusao, diga em uma frase curta se a aproximacao dos envelopes mudou muito ou pouco a cor mostrada na tela."
            ),
            "checklist": [
                f"A meta e: diferenca maxima <= {target_diff:.2f}.",
                "Use o Lab RGB para comparar antes e depois.",
                "Explique a relacao observada entre envelopes e cor.",
            ],
            "keyword_groups": [["cor", "rgb", "cartao"], ["envelope", "mudanca", "comparacao"]],
            "min_keyword_groups": 0,
            "min_words": 4,
            "target_diff": target_diff,
        },
        {
            "type": "real-world-correlation",
            "title": "Exercicio: simulacao e decomposicao da luz real",
            "difficulty": "avancado",
            "prompt": (
                "Relacione esta simulacao com uma experiencia real de decomposicao da luz (como prisma, CD/DVD ou goticulas de agua formando arco-iris). "
                "Escreva uma conclusao curta explicando como a separacao por frequencias observada no simulador ajuda a interpretar o fenomeno real."
            ),
            "checklist": [
                "Cite ao menos uma experiencia real de decomposicao da luz.",
                "Conecte frequencia/cor do simulador com o que aparece no experimento real.",
                "Descreva a relacao em linguagem curta e objetiva.",
            ],
            "keyword_groups": [["prisma", "arco-iris", "cd", "dvd", "goticulas"], ["frequencia", "cor", "decomposicao", "espectro"]],
            "min_keyword_groups": 1,
            "min_words": 8,
        },
    ]

    if previous_id is not None and len(exercises) > 1:
        previous_type = str(previous_id).split("-", 1)[0]
        filtered = [exercise for exercise in exercises if exercise["type"] != previous_type]
        if filtered:
            exercises = filtered

    if forced_type:
        filtered = [exercise for exercise in exercises if exercise["type"] == forced_type]
        if filtered:
            exercises = filtered

    index = int(rng.integers(0, len(exercises)))
    exercise = exercises[index]
    exercise["id"] = f"{exercise['type']}-{seed}"
    return exercise


def build_exercise_rubric(exercise):
    return html.Ul(
        [html.Li(item) for item in exercise.get("checklist", [])],
        style={"margin": "0", "paddingLeft": "18px", "lineHeight": "1.8"},
    )


def build_exercise_feedback(feedback=None):
    if feedback is None:
        feedback = {
            "title": "Pronto para comecar",
            "message": "Clique em Sortear novo exercicio para gerar uma atividade ou responda o exercicio atual com os dados da simulacao.",
            "details": [],
            "accent": "#2563eb",
            "background": "#eff6ff",
        }

    return html.Div(
        [
            html.Strong(feedback["title"]),
            html.P(feedback["message"], style={"margin": "10px 0 0 0", "lineHeight": "1.7"}),
            html.Ul(
                [html.Li(detail) for detail in feedback.get("details", [])],
                style={"margin": "10px 0 0 0", "paddingLeft": "18px", "lineHeight": "1.7"},
            ) if feedback.get("details") else html.Div(),
        ],
        style={
            "border": f"1px solid {feedback['accent']}",
            "background": feedback["background"],
            "borderRadius": "12px",
            "padding": "14px 16px",
            "marginTop": "14px",
        },
    )


def create_exercise_session():
    # A sessão completa sempre tem uma etapa de cada tipo previsto em SESSION_EXERCISE_TYPES.
    return {
        "exercises": [generate_random_exercise(forced_type=exercise_type) for exercise_type in SESSION_EXERCISE_TYPES],
        "current_index": 0,
        "results": [],
        "skipped_questions": 0,
        "current_attempts": 0,
        "stage": "exercise",
        "final_conclusion": "",
    }


def normalize_exercise_session(session_data):
    # Como o estado fica salvo no navegador, esta função corrige faltas e valores inconsistentes antes do uso.
    if not isinstance(session_data, dict) or not isinstance(session_data.get("exercises"), list) or not session_data.get("exercises"):
        return create_exercise_session()

    exercises = list(session_data.get("exercises", []))
    max_index = max(len(exercises) - 1, 0)
    try:
        current_index = int(session_data.get("current_index", 0))
    except (TypeError, ValueError):
        current_index = 0

    return {
        "exercises": exercises,
        "current_index": max(0, min(current_index, max_index)),
        "results": list(session_data.get("results", [])),
        "skipped_questions": int(session_data.get("skipped_questions", 0) or 0),
        "current_attempts": int(session_data.get("current_attempts", 0) or 0),
        "stage": session_data.get("stage") if session_data.get("stage") in {"exercise", "conclusion", "results"} else "exercise",
        "final_conclusion": session_data.get("final_conclusion", "") or "",
    }


def get_current_session_exercise(session_data):
    normalized = normalize_exercise_session(session_data)
    exercises = normalized["exercises"]
    return exercises[normalized["current_index"]]


def build_stage_rubric(stage, exercise=None):
    # A rubrica muda conforme o momento da sessão: resolver etapa, escrever conclusão ou revisar o envio final.
    if stage == "exercise" and exercise:
        return build_exercise_rubric(exercise)

    if stage == "conclusion":
        return html.Ul(
            [
                html.Li("Explique o que mudou nos envelopes, na cor ou na janela espectral ao longo da sessão."),
                html.Li("Relacione pelo menos uma decisão sua de ajuste aos resultados observados na simulação."),
                html.Li("Escreva uma conclusão um pouco mais desenvolvida do que as respostas curtas das etapas."),
            ],
            style={"margin": "0", "paddingLeft": "18px", "lineHeight": "1.8"},
        )

    return html.Ul(
        [
            html.Li("Confira o resumo da sessão antes de enviar os dados."),
            html.Li("Preencha nome, série, turma e conclusão final."),
            html.Li("Se desejar, acrescente críticas, sugestões e e-mail para cópia."),
        ],
        style={"margin": "0", "paddingLeft": "18px", "lineHeight": "1.8"},
    )


def build_session_results_summary(session_data):
    # Este resumo transforma a sessão inteira em indicadores simples, úteis para estudante e professor.
    normalized = normalize_exercise_session(session_data)
    exercises = normalized["exercises"]
    results = normalized["results"]
    total = len(exercises)
    correct = sum(1 for item in results if item.get("correct"))
    skipped = int(normalized.get("skipped_questions", 0))
    incorrect = sum(1 for item in results if not item.get("correct"))
    attempts = sum(int(item.get("attempts", 0)) for item in results)
    pending = max(0, total - len(results))
    percent = int(round((correct / total) * 100)) if total else 0

    return html.Div(
        [
            html.P(f"Exercícios previstos: {total}", style={"margin": "0 0 8px 0"}),
            html.P(f"Etapas concluídas com acerto: {correct}", style={"margin": "0 0 8px 0"}),
            html.P(f"Etapas puladas: {skipped}", style={"margin": "0 0 8px 0"}),
            html.P(f"Etapas sem acerto registrado: {incorrect}", style={"margin": "0 0 8px 0"}),
            html.P(f"Tentativas acumuladas nesta sessão: {attempts}", style={"margin": "0 0 8px 0"}),
            html.P(f"Etapas ainda pendentes: {pending}", style={"margin": "0 0 8px 0"}),
            html.P(f"Nota final da sessão: {percent}%", style={"margin": "0", "fontWeight": "bold"}),
        ],
        style={
            "border": "1px solid #d7deea",
            "borderRadius": "12px",
            "padding": "16px",
            "background": "#ffffff",
            "lineHeight": "1.7",
        },
    )


def normalize_stage_statuses(progress_data):
    raw_statuses = progress_data.get("stage_statuses")
    normalized = {}
    valid_results = {"acerto", "parcial", "erro", "pulado"}

    if isinstance(raw_statuses, dict):
        for key, value in raw_statuses.items():
            if not isinstance(value, dict):
                continue
            result = value.get("result")
            if result not in valid_results:
                continue
            try:
                score = int(value.get("score", 0) or 0)
            except (TypeError, ValueError):
                score = 0
            normalized[str(key)] = {"result": result, "score": score}
        return normalized

    history_entries = progress_data.get("history", [])
    if not isinstance(history_entries, list):
        return normalized

    for entry in history_entries:
        if not isinstance(entry, dict):
            continue
        stage_key = str(entry.get("title", "")).strip()
        result = entry.get("result")
        if not stage_key or result not in valid_results:
            continue
        try:
            score = int(entry.get("score", 0) or 0)
        except (TypeError, ValueError):
            score = 0
        normalized[stage_key] = {"result": result, "score": score}

    return normalized


def count_stage_statuses(stage_statuses):
    values = list(stage_statuses.values()) if isinstance(stage_statuses, dict) else []
    correct = sum(1 for item in values if item.get("result") == "acerto")
    partial = sum(1 for item in values if item.get("result") == "parcial")
    incorrect = sum(1 for item in values if item.get("result") in {"erro", "pulado"})
    return correct, partial, incorrect


def update_stage_statuses(progress_data, stage_key, result_label, score):
    stage_statuses = normalize_stage_statuses(progress_data)
    stage_statuses[str(stage_key)] = {"result": result_label, "score": int(score)}
    correct, partial, incorrect = count_stage_statuses(stage_statuses)
    return stage_statuses, correct, partial, incorrect


def build_exercise_stage_outputs(session_data, progress_data, feedback_data, answer_value="", session_conclusion_value=None, final_conclusion_value=None):
    # Esta função decide o que a interface da aba Exercícios deve mostrar em cada estágio da sessão.
    normalized = normalize_exercise_session(session_data)
    current_exercise = get_current_session_exercise(normalized)
    stage = normalized["stage"]

    if stage == "exercise":
        title = current_exercise["title"]
        difficulty = f"Etapa {normalized['current_index'] + 1} de {len(normalized['exercises'])} | Nivel: {current_exercise.get('difficulty', 'fundamental')}"
        prompt = current_exercise["prompt"]
        rubric = build_stage_rubric(stage, current_exercise)
        indicator = f"Etapa atual: {normalized['current_index'] + 1} de {len(normalized['exercises'])}"
    elif stage == "conclusion":
        title = "Conclusão final da sessão"
        difficulty = "Etapa final antes do envio"
        prompt = "As etapas guiadas já foram concluídas. Agora registre uma conclusão mais ampla sobre o que você observou na simulação e como suas escolhas alteraram os resultados."
        rubric = build_stage_rubric(stage)
        indicator = "Etapa atual: conclusão final"
    else:
        title = "Resultados e envio"
        difficulty = "Resumo final da sessão"
        prompt = "Confira o resumo, complete os dados do estudante e envie o relatório final para a planilha e para os e-mails."
        rubric = build_stage_rubric(stage)
        indicator = "Etapa atual: resultados e envio"

    answer_style = {"marginTop": "18px", "display": "block"} if stage == "exercise" else {"display": "none"}
    actions_style = {
        "marginTop": "18px",
        "display": "flex",
        "gap": "10px",
        "flexWrap": "wrap",
    } if stage == "exercise" else {"display": "none"}
    conclusion_style = {
        "marginTop": "18px",
        "display": "block",
        "border": "1px solid #d7deea",
        "borderRadius": "12px",
        "padding": "16px",
        "background": "#ffffff",
    } if stage == "conclusion" else {"display": "none"}
    results_style = {
        "marginTop": "18px",
        "display": "block",
        "border": "1px solid #d7deea",
        "borderRadius": "12px",
        "padding": "16px",
        "background": "#ffffff",
    } if stage == "results" else {"display": "none"}

    stored_conclusion = normalized.get("final_conclusion", "")
    if session_conclusion_value is None:
        session_conclusion_value = stored_conclusion
    if final_conclusion_value is None:
        final_conclusion_value = stored_conclusion

    return (
        normalized,
        progress_data,
        title,
        difficulty,
        prompt,
        rubric,
        build_exercise_feedback(feedback_data),
        build_exercise_progress_panel(progress_data),
        answer_value,
        indicator,
        answer_style,
        actions_style,
        conclusion_style,
        results_style,
        build_session_results_summary(normalized),
        session_conclusion_value,
        final_conclusion_value,
    )


def build_exercise_progress_panel(progress_data):
    # O painel lateral serve como memória curta da trajetória do estudante durante a sessão.
    attempts = int(progress_data.get("attempts", 0))
    stage_statuses = normalize_stage_statuses(progress_data)
    if stage_statuses:
        correct, partial, incorrect = count_stage_statuses(stage_statuses)
    else:
        correct = int(progress_data.get("correct", 0))
        partial = int(progress_data.get("partial", 0))
        incorrect = int(progress_data.get("incorrect", 0))
    streak = int(progress_data.get("streak", 0))
    best_streak = int(progress_data.get("best_streak", 0))
    best_score = int(progress_data.get("best_score", 0))
    last_score = int(progress_data.get("last_score", 0))
    history_entries = progress_data.get("history", [])[-5:][::-1]
    accuracy = 0.0 if attempts == 0 else 100.0 * correct / attempts

    return html.Div(
        [
            html.Div(
                [
                    html.Div([
                        html.Strong("Tentativas"),
                        html.Div(str(attempts), style={"fontSize": "1.5rem", "marginTop": "6px"}),
                    ], style={"padding": "12px", "borderRadius": "12px", "background": "#eff6ff"}),
                    html.Div([
                        html.Strong("Acertos"),
                        html.Div(str(correct), style={"fontSize": "1.5rem", "marginTop": "6px"}),
                    ], style={"padding": "12px", "borderRadius": "12px", "background": "#ecfdf5"}),
                    html.Div([
                        html.Strong("Parciais"),
                        html.Div(str(partial), style={"fontSize": "1.5rem", "marginTop": "6px"}),
                    ], style={"padding": "12px", "borderRadius": "12px", "background": "#fef3c7"}),
                    html.Div([
                        html.Strong("Precisao"),
                        html.Div(f"{accuracy:.0f}%", style={"fontSize": "1.5rem", "marginTop": "6px"}),
                    ], style={"padding": "12px", "borderRadius": "12px", "background": "#fff7ed"}),
                    html.Div([
                        html.Strong("Sequencia"),
                        html.Div(str(streak), style={"fontSize": "1.5rem", "marginTop": "6px"}),
                    ], style={"padding": "12px", "borderRadius": "12px", "background": "#ede9fe"}),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(110px, 1fr))", "gap": "12px"},
            ),
            html.P(
                f"Ultima pontuacao: {last_score}/100 | Melhor pontuacao: {best_score}/100 | Melhor sequencia: {best_streak}.",
                style={"marginTop": "14px", "marginBottom": "0", "color": "#475569", "lineHeight": "1.7"},
            ),
            html.H4("Ultimos envios", style={"marginTop": "18px", "marginBottom": "10px"}),
            html.Ul(
                [
                    html.Li(
                        f"{entry['timestamp']} | {entry['title']} | {entry['result']} | {entry['score']}/100 | {entry['metric']}"
                    )
                    for entry in history_entries
                ],
                style={"margin": "0", "paddingLeft": "18px", "lineHeight": "1.8"},
            ) if history_entries else html.P(
                "Nenhum envio registrado ainda. O progresso ficara salvo neste navegador.",
                style={"margin": "0", "lineHeight": "1.7"},
            ),
            html.P(
                f"Erros registrados: {incorrect}. Cada novo envio atualiza o historico salvo localmente.",
                style={"marginTop": "16px", "color": "#475569", "lineHeight": "1.7"},
            ),
        ]
    )


def collect_simulation_metrics(table_data, history_data, smoothing_window, freq_delta):
    # Antes de avaliar uma resposta, extraímos do simulador as medidas numéricas relevantes para aquela etapa.
    if table_data is None:
        table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
    amps1, amps2 = table_data_to_amps(table_data)
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    envelope1 = compute_envelope(wave1, smoothing_window)
    envelope2 = compute_envelope(wave2, smoothing_window)
    active_count1 = int(np.sum(np.abs(amps1) > 1e-12))
    active_count2 = int(np.sum(np.abs(amps2) > 1e-12))
    valid_optimization = has_valid_optimization_result(amps1, amps2, history_data)

    if valid_optimization:
        optimized_diff = history_data.get("after_diff")
        if optimized_diff is None:
            optimized_diff = max_envelope_difference(amps1, amps2, smoothing_window)
        max_diff = float(optimized_diff)
    else:
        max_diff = float(np.max(np.abs(envelope1 - envelope2)))

    return {
        "max_diff": max_diff,
        "smoothing_window": sanitize_smoothing_window(smoothing_window, len(T)),
        "freq_delta": int(freq_delta),
        "active_count1": active_count1,
        "active_count2": active_count2,
        "has_optimization": valid_optimization,
    }


def evaluate_exercise(exercise, metrics, answer_text):
    # A avaliação combina dois lados: o que o estudante fez na simulação e o que ele conseguiu explicar em texto.
    answer_normalized = normalize_text(answer_text)
    answer_word_count = len([word for word in answer_normalized.split() if word])
    keyword_groups = exercise.get("keyword_groups", [])
    matched_groups = 0
    missing_topics = []

    for group in keyword_groups:
        if any(keyword in answer_normalized for keyword in group):
            matched_groups += 1
        else:
            missing_topics.append(group[0])

    min_keyword_groups = int(exercise.get("min_keyword_groups", len(keyword_groups)))
    min_words = int(exercise.get("min_words", 4))
    keyword_score = 0.0 if len(keyword_groups) == 0 else matched_groups / len(keyword_groups)
    depth_score = min(1.0, answer_word_count / max(1, min_words))
    text_score = max(depth_score, 0.45 * keyword_score + 0.55 * depth_score)
    text_pass = answer_word_count >= min_words and (min_keyword_groups <= 0 or matched_groups >= min_keyword_groups)
    numeric_pass = False
    metric_message = ""
    numeric_score = 0.0

    if exercise["type"] == "envelope-target":
        numeric_pass = metrics["max_diff"] <= float(exercise["target_diff"])
        numeric_score = 1.0 if numeric_pass else min(1.0, float(exercise["target_diff"]) / max(metrics["max_diff"], 1e-9))
        metric_message = f"Diferença atual: {metrics['max_diff']:.3f}. Meta: <= {exercise['target_diff']:.2f}."
    elif exercise["type"] == "smoothing-observe":
        numeric_pass = metrics["smoothing_window"] >= int(exercise["target_smoothing"])
        numeric_score = min(1.0, metrics["smoothing_window"] / max(1, int(exercise["target_smoothing"])))
        metric_message = (
            f"Suavização atual: {metrics['smoothing_window']} ponto(s). "
            f"Meta: >= {exercise['target_smoothing']} ponto(s)."
        )
    elif exercise["type"] == "frequency-window":
        delta_ratio = min(1.0, int(exercise["target_delta"]) / max(metrics["freq_delta"], 1))
        active_ratio = 0.5 * int(metrics["active_count1"] > 0) + 0.5 * int(metrics["active_count2"] > 0)
        optimization_ratio = 1.0 if metrics["has_optimization"] else 0.0
        numeric_pass = (
            metrics["freq_delta"] <= int(exercise["target_delta"])
            and metrics["active_count1"] > 0
            and metrics["active_count2"] > 0
        )
        numeric_score = 0.5 * delta_ratio + 0.25 * active_ratio + 0.25 * optimization_ratio
        metric_message = (
            f"delta f atual: {metrics['freq_delta']} THz. Meta: <= {exercise['target_delta']} THz. "
            f"Otimizacao executada: {'sim' if metrics['has_optimization'] else 'nao'}."
        )
    elif exercise["type"] == "color-compare":
        numeric_pass = metrics["max_diff"] <= float(exercise["target_diff"])
        diff_ratio = min(1.0, float(exercise["target_diff"]) / max(metrics["max_diff"], 1e-9))
        optimization_ratio = 1.0 if metrics["has_optimization"] else 0.0
        numeric_score = 0.75 * diff_ratio + 0.25 * optimization_ratio
        metric_message = (
            f"Diferença atual: {metrics['max_diff']:.3f}. Meta: <= {exercise['target_diff']:.2f}. "
            f"Otimizacao executada: {'sim' if metrics['has_optimization'] else 'nao'}."
        )
    elif exercise["type"] == "real-world-correlation":
        active_total = int(metrics["active_count1"] + metrics["active_count2"])
        numeric_pass = active_total >= 2
        numeric_score = 1.0 if numeric_pass else 0.5
        metric_message = (
            "Etapa de correlacao com fenomeno real. "
            f"Componentes ativas totais: {active_total}. "
            "Meta: usar o simulador para sustentar a explicacao do experimento real."
        )

    total_score = int(round((0.65 * numeric_score + 0.35 * text_score) * 100))
    passed = numeric_pass and text_pass
    partial = (numeric_pass or total_score >= 55) and not passed
    details = [metric_message]
    details.append(
        f"Conclusao textual: {matched_groups}/{max(1, len(keyword_groups))} topico(s) essenciais identificados em {answer_word_count} palavra(s)."
    )
    details.append(f"Pontuacao da tentativa: {total_score}/100.")
    if missing_topics and not text_pass:
        details.append("Sugestao para a conclusao: inclua termos ligados a " + ", ".join(missing_topics[:2]) + ".")
    if answer_word_count < min_words:
        details.append(f"A conclusao ainda esta curta. Tente usar pelo menos {min_words} palavras.")

    if passed:
        feedback = {
            "title": "Acerto registrado",
            "message": "Envio recebido com criterio numerico e conclusao textual consistentes.",
            "details": details,
            "accent": "#15803d",
            "background": "#ecfdf5",
        }
    elif partial:
        feedback = {
            "title": "Envio registrado com avanço parcial",
            "message": "A conclusao foi salva. Houve progresso, mas a meta numerica ou a analise textual ainda pode melhorar.",
            "details": details,
            "accent": "#b45309",
            "background": "#fffbeb",
        }
    else:
        feedback = {
            "title": "Envio registrado",
            "message": "A conclusao foi salva mesmo sem atingir a meta do exercicio nesta tentativa.",
            "details": details,
            "accent": "#c2410c",
            "background": "#fff7ed",
        }

    metric_summary = metric_message.replace("Meta: ", "meta ")
    result_label = "acerto" if passed else "parcial" if partial else "erro"
    return passed, partial, total_score, feedback, metric_summary, result_label


def build_mobile_active_summary(table_data):
        if table_data is None:
                table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)

        amps1, amps2 = table_data_to_amps(table_data)
        active_wave1 = [str(int(freq)) for freq, amp in zip(FREQS, amps1) if abs(amp) > 1e-12]
        active_wave2 = [str(int(freq)) for freq, amp in zip(FREQS, amps2) if abs(amp) > 1e-12]

        def summarize(freqs):
                if not freqs:
                        return "nenhuma ativa"
                preview = ", ".join(freqs[:6])
                if len(freqs) > 6:
                        preview += ", ..."
                return preview + " THz"

        return html.Div(
                [
                        html.Strong("Resumo rapido das frequencias ativas"),
                        html.Div(f"Onda 1: {summarize(active_wave1)}", style={"marginTop": "8px"}),
                        html.Div(f"Onda 2: {summarize(active_wave2)}", style={"marginTop": "4px"}),
                ],
                style={"lineHeight": "1.7"},
        )


def clone_figure_for_mobile(figure, height, top_margin=58):
    cloned = go.Figure(figure)
    for trace in cloned.data:
        if getattr(trace, "type", None) == "scatter" and "lines" in str(getattr(trace, "mode", "")):
            trace.line.width = 1.4
    for shape in cloned.layout.shapes or []:
        if hasattr(shape, "line"):
            shape.line.width = min(getattr(shape.line, "width", 1), 1)
    cloned.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=top_margin, b=18),
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5),
    )
    return cloned


def build_mobile_visual_content(view_name, intensity_figure, main_figure, scale_figure, cards, summary_box, control_note):
        if view_name == "controls":
                return html.Div(
                        [
                                html.H4("Controle das amplitudes", style={"marginBottom": "10px"}),
                                dcc.Graph(
                                        figure=clone_figure_for_mobile(intensity_figure, 300),
                                    config=GRAPH_CONFIG,
                                ),
                        ]
                )

        if view_name == "rgb":
                return html.Div(
                        [
                                html.H4("Lab RGB no celular", style={"marginBottom": "10px"}),
                                dcc.Graph(
                                        figure=clone_figure_for_mobile(scale_figure, 240),
                                    config=GRAPH_CONFIG,
                                ),
                                html.Div(
                                        cards,
                                        style={
                                                "display": "grid",
                                                "gridTemplateColumns": "1fr",
                                                "gap": "12px",
                                                "marginTop": "12px",
                                        },
                                ),
                        ]
                )

        if view_name == "summary":
                return html.Div(
                        [
                                html.H4("Resumo da simulacao", style={"marginBottom": "10px"}),
                                html.Div(
                                        [summary_box],
                                        style={
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "padding": "14px",
                                                "background": "#ffffff",
                                        },
                                ),
                                html.Div(
                                        [control_note],
                                        style={
                                                "marginTop": "12px",
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "padding": "14px",
                                                "background": "#ffffff",
                                        },
                                ),
                        ]
                )

        return html.Div(
                [
                        html.H4("Ondas, envelopes e diferenca", style={"marginBottom": "10px"}),
                        dcc.Graph(
                    figure=clone_figure_for_mobile(main_figure, 620, top_margin=88),
                            config=GRAPH_CONFIG,
                        ),
                ]
        )


app = Dash(
        __name__,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1, maximum-scale=1"},
            {"name": "citation_title", "content": "Simulacao: Soma de Cores"},
            {"name": "citation_author", "content": "Flavio Ambrosio Campos"},
            {"name": "citation_publication_date", "content": "2026"},
            {"name": "citation_doi", "content": SIMULATION_DOI},
            {"name": "citation_publisher", "content": "GitHub Pages - CEAN"},
            {"name": "citation_url", "content": SIMULATION_URL},
            {
                "name": "description",
                "content": (
                    "Concepcao e planejamento pedagogico: Flavio Ambrosio Campos. "
                    "Codigo assistido por ferramentas de IA sob supervisao humana."
                ),
            },
        ],
)
server = app.server

initial_history = {
    "before1": ZERO_AMPS.tolist(),
    "before2": ZERO_AMPS.tolist(),
    "after1": ZERO_AMPS.tolist(),
    "after2": ZERO_AMPS.tolist(),
    "after_diff": None,
    "has_optimization": False,
}

initial_exercise_progress = {
    "attempts": 0,
    "correct": 0,
    "partial": 0,
    "incorrect": 0,
    "streak": 0,
    "best_streak": 0,
    "last_score": 0,
    "best_score": 0,
    "stage_statuses": {},
    "history": [],
}

initial_exercise_session = create_exercise_session()
initial_exercise = get_current_session_exercise(initial_exercise_session)

app.layout = html.Div(
    [
        dcc.Store(id="history-store", data=initial_history),
        dcc.Store(id="exercise-store", data=initial_exercise_session, storage_type="memory"),
        dcc.Store(id="exercise-progress-store", data=initial_exercise_progress, storage_type="local"),
        html.H1("Simulador de Ondas e Envelopes de Hilbert - Versão Web"),
        html.P(
            "Esta versão foi adaptada para navegador. As janelas do programa original foram preservadas como abas da página, o que funciona melhor para uso online.",
            style={"lineHeight": "1.6"},
        ),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Simulador",
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3("Controles das amplitudes"),
                                        html.P(
                                            "Edite os valores das colunas Onda 1 e Onda 2. Cada linha corresponde a uma frequência em THz.",
                                            style={"lineHeight": "1.6"},
                                        ),
                                        html.Div(
                                            className="desktop-only",
                                            children=[
                                                dash_table.DataTable(
                                                    id="amp-table",
                                                    columns=[
                                                        {"name": "Freq. (THz)", "id": "frequencia", "editable": False},
                                                        {"name": "Onda 1", "id": "onda1", "editable": True},
                                                        {"name": "Onda 2", "id": "onda2", "editable": True},
                                                    ],
                                                    data=amps_to_table_data(ZERO_AMPS, ZERO_AMPS),
                                                    editable=True,
                                                    persistence=False,
                                                    style_table={
                                                        "height": "520px",
                                                        "overflowY": "auto",
                                                        "overflowX": "auto",
                                                        "border": "1px solid #d7deea",
                                                    },
                                                    style_header={
                                                        "fontWeight": "bold",
                                                        "backgroundColor": "#eef4ff",
                                                        "fontSize": "11px",
                                                        "whiteSpace": "normal",
                                                        "height": "auto",
                                                    },
                                                    style_cell={
                                                        "textAlign": "center",
                                                        "padding": "4px",
                                                        "fontSize": "11px",
                                                        "minWidth": "60px",
                                                        "width": "60px",
                                                        "maxWidth": "60px",
                                                    },
                                                )
                                            ],
                                        ),
                                        html.Div(
                                            className="mobile-only mobile-card",
                                            children=[
                                                html.P(
                                                    "No celular, a edicao acontece uma frequencia por vez. Escolha a frequencia, ajuste os dois valores e toque em Aplicar.",
                                                    style={"marginTop": "0", "lineHeight": "1.7"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Button("Anterior", id="mobile-prev-freq-btn", n_clicks=0),
                                                        html.Button("Proxima", id="mobile-next-freq-btn", n_clicks=0),
                                                    ],
                                                    style={"display": "flex", "gap": "10px", "flexWrap": "wrap", "marginTop": "12px"},
                                                ),
                                                dcc.Dropdown(
                                                    id="mobile-frequency-picker",
                                                    options=[
                                                        {"label": f"{int(freq)} THz", "value": int(freq)}
                                                        for freq in FREQS
                                                    ],
                                                    value=int(FREQS[0]),
                                                    clearable=False,
                                                    searchable=False,
                                                    style={"marginTop": "12px"},
                                                ),
                                                html.Div(id="mobile-frequency-position", style={"marginTop": "10px", "color": "#475569"}),
                                                html.Div(
                                                    className="mobile-controls-grid",
                                                    children=[
                                                        html.Div(
                                                            [
                                                                html.Label("Amplitude da Onda 1"),
                                                                dcc.Input(
                                                                    id="mobile-amp1-input",
                                                                    type="number",
                                                                    step=0.1,
                                                                    min=AMP_MIN,
                                                                    max=AMP_MAX,
                                                                    value=0,
                                                                    style={"width": "100%", "marginTop": "6px", "padding": "10px"},
                                                                ),
                                                            ]
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Label("Amplitude da Onda 2"),
                                                                dcc.Input(
                                                                    id="mobile-amp2-input",
                                                                    type="number",
                                                                    step=0.1,
                                                                    min=AMP_MIN,
                                                                    max=AMP_MAX,
                                                                    value=0,
                                                                    style={"width": "100%", "marginTop": "6px", "padding": "10px"},
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                    style={"marginTop": "12px"},
                                                ),
                                                html.Button(
                                                    "Aplicar a frequencia",
                                                    id="mobile-apply-btn",
                                                    n_clicks=0,
                                                    style={"marginTop": "14px", "width": "100%"},
                                                ),
                                                html.Div(id="mobile-active-summary", style={"marginTop": "14px"}),
                                            ],
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Suavização dos envelopes de Hilbert"),
                                                dcc.Slider(
                                                    id="smoothing-slider",
                                                    min=1,
                                                    max=121,
                                                    step=2,
                                                    value=DEFAULT_SMOOTHING,
                                                    marks={value: str(value) for value in [1, 11, 21, 31, 51, 81, 121]},
                                                ),
                                            ],
                                            style={"marginTop": "18px"},
                                        ),
                                        html.Div(
                                            [
                                                html.Label("delta f limite para a otimização"),
                                                dcc.Slider(
                                                    id="freq-delta-slider",
                                                    min=0,
                                                    max=MAX_FREQ_DELTA,
                                                    step=10,
                                                    value=DEFAULT_FREQ_DELTA,
                                                    marks={value: str(value) for value in [0, 40, 80, 120, 200, 300, 400]},
                                                ),
                                            ],
                                            style={"marginTop": "18px"},
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Máximo de iterações da otimização"),
                                                dcc.Slider(
                                                    id="max-iter-slider",
                                                    min=1000,
                                                    max=10000,
                                                    step=500,
                                                    value=2000,
                                                    marks={value: str(value) for value in range(1000, 10001, 1500)},
                                                ),
                                            ],
                                            style={"marginTop": "18px"},
                                        ),
                                        html.Div(
                                            id="control-note-box",
                                            style={
                                                "marginTop": "18px",
                                                "padding": "12px 14px",
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "10px",
                                                "background": "#f8fafc",
                                                "lineHeight": "1.7",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Button("OTIMIZAR", id="optimize-btn", n_clicks=0, style={"marginRight": "10px"}),
                                                html.Button("ZERAR", id="reset-btn", n_clicks=0),
                                            ],
                                            style={"marginTop": "18px", "display": "flex", "gap": "10px"},
                                        ),
                                        dcc.Loading(
                                            id="optimize-loading",
                                            type="circle",
                                            color="#2563eb",
                                            children=html.Div(
                                                id="optimization-indicator",
                                                style={"marginTop": "12px", "minHeight": "24px", "fontWeight": "bold", "color": "#2563eb"},
                                            ),
                                        ),
                                        html.Div(
                                            "Pronto para editar e otimizar as ondas.",
                                            id="status-message",
                                            style={
                                                "marginTop": "18px",
                                                "padding": "12px 14px",
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "10px",
                                                "background": "#ffffff",
                                            },
                                        ),
                                    ],
                                    className="panel-card",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Label("Janela de tempo dos graficos (zoom horizontal)"),
                                                dcc.RadioItems(
                                                    id="time-window-selector",
                                                    options=[
                                                        {"label": f"{value} fs", "value": value}
                                                        for value in TIME_WINDOW_OPTIONS
                                                    ],
                                                    value=DEFAULT_TIME_WINDOW_FS,
                                                    inline=True,
                                                    labelStyle={"display": "inline-block", "marginRight": "12px", "marginBottom": "8px"},
                                                    style={"marginTop": "8px"},
                                                ),
                                            ],
                                            style={
                                                "marginBottom": "14px",
                                                "padding": "12px",
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "background": "#ffffff",
                                            },
                                        ),
                                        html.Div(
                                            className="desktop-only graph-stack",
                                            children=[
                                                dcc.Graph(id="intensity-graph", config=GRAPH_CONFIG),
                                                dcc.Graph(id="main-graph", config=GRAPH_CONFIG),
                                                html.Div(
                                                    [
                                                        html.H3("Resumo rápido"),
                                                        html.Div(id="summary-box"),
                                                    ],
                                                    style={
                                                        "border": "1px solid #d7deea",
                                                        "borderRadius": "12px",
                                                        "padding": "16px",
                                                        "background": "#ffffff",
                                                    },
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            className="mobile-only mobile-card",
                                            children=[
                                                html.H3("Visualização no celular"),
                                                html.P(
                                                    "Escolha uma etapa para visualizar um bloco por vez. Isso deixa a leitura mais confortável em telas pequenas.",
                                                    style={"lineHeight": "1.7"},
                                                ),
                                                dcc.RadioItems(
                                                    id="mobile-visual-view",
                                                    options=[
                                                        {"label": "Ondas e envelopes", "value": "main"},
                                                        {"label": "Controles", "value": "controls"},
                                                        {"label": "Lab RGB", "value": "rgb"},
                                                        {"label": "Resumo", "value": "summary"},
                                                    ],
                                                    value="main",
                                                    inline=False,
                                                    labelStyle={"display": "block", "marginBottom": "8px"},
                                                    style={"marginTop": "12px"},
                                                ),
                                                html.Div(id="mobile-visual-content", style={"marginTop": "14px"}),
                                            ],
                                        ),
                                    ],
                                    className="panel-card",
                                ),
                            ],
                            className="simulator-grid",
                        )
                    ],
                ),
                dcc.Tab(
                    label="Fourier Antes",
                    children=[
                        html.Div(
                            [
                                html.H3("Equações de Fourier antes da otimização"),
                                html.Pre(id="fourier-before", style={"whiteSpace": "pre-wrap", "lineHeight": "1.7"}),
                            ],
                            style={"padding": "20px"},
                        )
                    ],
                ),
                dcc.Tab(
                    label="Fourier Depois",
                    children=[
                        html.Div(
                            [
                                html.H3("Equações de Fourier depois da otimização"),
                                html.Pre(id="fourier-after", style={"whiteSpace": "pre-wrap", "lineHeight": "1.7"}),
                            ],
                            style={"padding": "20px"},
                        )
                    ],
                ),
                dcc.Tab(
                    label="Hilbert",
                    children=[
                        html.Div(
                            [
                                html.H3("Envelopes de Hilbert - teoria e aplicação"),
                                html.P("Para um sinal real x(t), o envelope complexo é z(t) = x(t) + j*H{x(t)}."),
                                html.P("O envelope de amplitude é A(t) = sqrt(x^2(t) + H^2{x(t)})."),
                                html.P("Nesta aplicação, os envelopes são calculados com scipy.signal.hilbert e a otimização busca reduzir a diferença máxima entre os dois envelopes."),
                                html.P(id="hilbert-smoothing-note"),
                                html.P(id="hilbert-delta-note"),
                                html.P("Critério principal: minimizar max|A1(t) - A2(t)|."),
                            ],
                            style={"padding": "20px", "lineHeight": "1.8"},
                        )
                    ],
                ),
                dcc.Tab(
                    label="Lab RGB",
                    children=[
                        html.Div(
                            [
                                html.H3("Laboratório RGB do Monitor"),
                                html.Div(
                                    [
                                        dcc.RadioItems(
                                            id="rgb-mode",
                                            options=[
                                                {"label": "RGB visual", "value": "visual"},
                                                {"label": "Paleta em RGB", "value": "palette"},
                                            ],
                                            value="visual",
                                            inline=True,
                                        ),
                                        html.Button("Atualizar", id="rgb-refresh-btn", n_clicks=0),
                                    ],
                                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "gap": "12px", "flexWrap": "wrap"},
                                ),
                                html.Div(
                                    "Clique em Atualizar para recalcular os cartões do laboratório RGB com o estado atual.",
                                    id="rgb-refresh-message",
                                    style={"marginTop": "10px", "fontWeight": "bold", "color": "#2563eb", "minHeight": "24px"},
                                ),
                                dcc.Graph(id="rgb-scale-graph", config=GRAPH_CONFIG),
                                html.Div(
                                    id="rgb-cards-container",
                                    style={
                                        "display": "grid",
                                        "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                                        "gap": "16px",
                                    },
                                ),
                            ],
                            style={"padding": "20px"},
                        )
                    ],
                ),
                dcc.Tab(
                    label="Exercícios",
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(id="exercise-title", children=initial_exercise["title"]),
                                        html.Div(
                                            id="exercise-difficulty",
                                            children=f"Nivel atual: {initial_exercise.get('difficulty', 'fundamental')}",
                                            style={
                                                "display": "inline-block",
                                                "marginBottom": "12px",
                                                "padding": "6px 10px",
                                                "borderRadius": "999px",
                                                "background": "#e0f2fe",
                                                "color": "#0f172a",
                                                "fontWeight": "bold",
                                                "fontSize": "0.92rem",
                                            },
                                        ),
                                        html.P(
                                            id="exercise-prompt",
                                            children=initial_exercise["prompt"],
                                            style={"lineHeight": "1.8"},
                                        ),
                                        html.Div(
                                            [
                                                html.H4("Critérios de conferência"),
                                                html.Div(id="exercise-rubric", children=build_exercise_rubric(initial_exercise)),
                                            ],
                                            style={
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "padding": "16px",
                                                "background": "#ffffff",
                                            },
                                        ),
                                        html.Div(
                                            id="exercise-stage-indicator",
                                            children=f"Etapa atual: 1 de {len(initial_exercise_session['exercises'])}",
                                            style={
                                                "display": "inline-block",
                                                "marginBottom": "12px",
                                                "padding": "6px 10px",
                                                "borderRadius": "999px",
                                                "background": "#ede9fe",
                                                "color": "#312e81",
                                                "fontWeight": "bold",
                                                "fontSize": "0.92rem",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Registro da etapa"),
                                                dcc.Textarea(
                                                    id="exercise-answer",
                                                    value="",
                                                    placeholder="Escreva aqui uma resposta curta sobre a etapa atual: o que você ajustou, o que observou e como interpreta o resultado.",
                                                    style={
                                                        "width": "100%",
                                                        "minHeight": "180px",
                                                        "marginTop": "8px",
                                                        "padding": "12px",
                                                        "borderRadius": "12px",
                                                        "border": "1px solid #cbd5e1",
                                                        "lineHeight": "1.7",
                                                    },
                                                ),
                                            ],
                                            id="exercise-answer-section",
                                            style={"marginTop": "18px"},
                                        ),
                                        html.Div(
                                            [
                                                html.Button("Nova sessão de exercícios", id="new-exercise-btn", n_clicks=0),
                                                html.Button(
                                                    "Verificar etapa",
                                                    id="submit-exercise-btn",
                                                    n_clicks=0,
                                                ),
                                                html.Button(
                                                    "Avançar etapa",
                                                    id="next-exercise-btn",
                                                    n_clicks=0,
                                                ),
                                                html.Button(
                                                    "Pular etapa",
                                                    id="skip-exercise-btn",
                                                    n_clicks=0,
                                                ),
                                            ],
                                            id="exercise-step-actions",
                                            style={"marginTop": "18px", "display": "flex", "gap": "10px", "flexWrap": "wrap"},
                                        ),
                                        html.Div(
                                            [
                                                html.H4("Conclusão final da sessão", style={"marginTop": "0"}),
                                                html.P(
                                                    "Depois de concluir as etapas guiadas, escreva uma síntese mais ampla do que você aprendeu com a simulação.",
                                                    style={"lineHeight": "1.7"},
                                                ),
                                                dcc.Textarea(
                                                    id="session-conclusion-text",
                                                    value="",
                                                    placeholder="Explique aqui, com um pouco mais de detalhe, o que você aprendeu na sessão completa.",
                                                    style={
                                                        "width": "100%",
                                                        "minHeight": "180px",
                                                        "marginTop": "8px",
                                                        "padding": "12px",
                                                        "borderRadius": "12px",
                                                        "border": "1px solid #cbd5e1",
                                                        "lineHeight": "1.7",
                                                    },
                                                ),
                                                html.Button(
                                                    "Avançar para resultados",
                                                    id="submit-session-conclusion-btn",
                                                    n_clicks=0,
                                                    style={"marginTop": "14px"},
                                                ),
                                            ],
                                            id="exercise-conclusion-section",
                                            style={"display": "none"},
                                        ),
                                        html.Div(
                                            [
                                                html.H4("Resultados da sessão", style={"marginTop": "0"}),
                                                dcc.Store(id="student-access-store", storage_type="session", data={"authenticated": False}),
                                                html.Div(id="exercise-results-summary", children=build_session_results_summary(initial_exercise_session)),
                                                html.Div(
                                                    [
                                                        html.Label("Modo de envio"),
                                                        dcc.RadioItems(
                                                            id="submission-mode",
                                                            options=[
                                                                {"label": "Visitante", "value": "visitor"},
                                                                {"label": "Estudante", "value": "student"},
                                                            ],
                                                            value="visitor",
                                                            persistence=True,
                                                            persistence_type="session",
                                                            inline=True,
                                                            style={"marginTop": "8px"},
                                                        ),
                                                    ],
                                                    style={"marginTop": "12px"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Senha de estudante"),
                                                        html.Div(
                                                            [
                                                                dcc.Input(
                                                                    id="student-access-password",
                                                                    type="password",
                                                                    value="",
                                                                    placeholder="Digite a senha para liberar o modo estudante",
                                                                    style={
                                                                        "flex": "1 1 280px",
                                                                        "padding": "10px 12px",
                                                                        "borderRadius": "12px",
                                                                        "border": "1px solid #cbd5e1",
                                                                    },
                                                                ),
                                                                html.Button("Liberar acesso", id="student-unlock-btn", n_clicks=0),
                                                            ],
                                                            style={"display": "flex", "gap": "10px", "flexWrap": "wrap", "alignItems": "center", "marginTop": "8px"},
                                                        ),
                                                        html.Div(
                                                            id="student-access-status",
                                                            children="Modo visitante ativo. Para usar listas de estudantes, selecione Estudante e informe a senha.",
                                                            style={"marginTop": "8px", "fontWeight": "bold", "color": "#b45309"},
                                                        ),
                                                    ],
                                                    id="student-auth-section",
                                                    style={"marginTop": "12px", "display": "none"},
                                                ),
                                                html.Div(
                                                    [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.Label("Trilha"),
                                                                dcc.Dropdown(
                                                                    id="student-track",
                                                                    options=TRACK_OPTIONS,
                                                                    value="",
                                                                    persistence=True,
                                                                    persistence_type="local",
                                                                    clearable=False,
                                                                    style={
                                                                        "marginTop": "8px",
                                                                    },
                                                                ),
                                                            ],
                                                            style={"flex": "2 1 320px"},
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Label("Bimestre"),
                                                                dcc.Dropdown(
                                                                    id="student-bimester",
                                                                    options=BIMESTER_OPTIONS,
                                                                    value="",
                                                                    persistence=True,
                                                                    persistence_type="local",
                                                                    placeholder="Selecione o bimestre",
                                                                    clearable=False,
                                                                    style={
                                                                        "marginTop": "8px",
                                                                    },
                                                                ),
                                                            ],
                                                            style={"flex": "1 1 180px"},
                                                        ),
                                                    ],
                                                    style={"marginTop": "18px", "display": "flex", "gap": "12px", "flexWrap": "wrap"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.Label("Serie"),
                                                                dcc.Dropdown(
                                                                    id="student-grade",
                                                                    options=GRADE_OPTIONS,
                                                                    value="",
                                                                    persistence=True,
                                                                    persistence_type="local",
                                                                    placeholder="Selecione a serie",
                                                                    clearable=False,
                                                                    style={
                                                                        "marginTop": "8px",
                                                                    },
                                                                ),
                                                            ],
                                                            style={"flex": "1 1 180px"},
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Label("Turma"),
                                                                dcc.Dropdown(
                                                                    id="student-class",
                                                                    options=CLASS_OPTIONS,
                                                                    value="",
                                                                    persistence=True,
                                                                    persistence_type="local",
                                                                    placeholder="Selecione a turma",
                                                                    clearable=False,
                                                                    style={
                                                                        "marginTop": "8px",
                                                                    },
                                                                ),
                                                            ],
                                                            style={"flex": "1 1 160px"},
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Label("Nome do estudante"),
                                                                dcc.Dropdown(
                                                                    id="student-name",
                                                                    options=[],
                                                                    value="",
                                                                    persistence=True,
                                                                    persistence_type="local",
                                                                    placeholder="Selecione o nome do estudante",
                                                                    searchable=True,
                                                                    clearable=False,
                                                                    style={
                                                                        "marginTop": "8px",
                                                                    },
                                                                ),
                                                                html.Div(
                                                                    id="student-name-helper",
                                                                    children="Selecione trilha ou serie/turma para carregar a lista de estudantes.",
                                                                    style={"marginTop": "8px", "color": "#475569", "fontSize": "0.92rem", "lineHeight": "1.6"},
                                                                ),
                                                            ],
                                                            style={"flex": "2 1 320px"},
                                                        ),
                                                    ],
                                                    style={"marginTop": "18px", "display": "flex", "gap": "12px", "flexWrap": "wrap"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("E-mail para cópia"),
                                                        dcc.Input(
                                                            id="student-email",
                                                            type="email",
                                                            value="",
                                                            persistence=True,
                                                            persistence_type="local",
                                                            placeholder="seu@email.com",
                                                            style={
                                                                "width": "100%",
                                                                "marginTop": "8px",
                                                                "padding": "10px 12px",
                                                                "borderRadius": "12px",
                                                                "border": "1px solid #cbd5e1",
                                                            },
                                                        ),
                                                    ],
                                                    style={"marginTop": "18px"},
                                                ),
                                                    ],
                                                    id="student-fields-section",
                                                    style={"display": "none"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.Label("Nome do visitante"),
                                                                dcc.Input(
                                                                    id="visitor-name",
                                                                    type="text",
                                                                    value="",
                                                                    persistence=True,
                                                                    persistence_type="local",
                                                                    placeholder="Digite seu nome",
                                                                    style={
                                                                        "width": "100%",
                                                                        "marginTop": "8px",
                                                                        "padding": "10px 12px",
                                                                        "borderRadius": "12px",
                                                                        "border": "1px solid #cbd5e1",
                                                                    },
                                                                ),
                                                            ],
                                                            style={"flex": "1 1 280px"},
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Label("E-mail do visitante (opcional)"),
                                                                dcc.Input(
                                                                    id="visitor-email",
                                                                    type="email",
                                                                    value="",
                                                                    persistence=True,
                                                                    persistence_type="local",
                                                                    placeholder="seu@email.com",
                                                                    style={
                                                                        "width": "100%",
                                                                        "marginTop": "8px",
                                                                        "padding": "10px 12px",
                                                                        "borderRadius": "12px",
                                                                        "border": "1px solid #cbd5e1",
                                                                    },
                                                                ),
                                                            ],
                                                            style={"flex": "1 1 280px"},
                                                        ),
                                                    ],
                                                    id="visitor-fields-section",
                                                    style={"marginTop": "18px", "display": "flex", "gap": "12px", "flexWrap": "wrap"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Críticas"),
                                                        dcc.Textarea(
                                                            id="criticism-input",
                                                            value="",
                                                            placeholder="O que poderia ser melhorado na simulação ou na dinâmica dos exercícios?",
                                                            style={
                                                                "width": "100%",
                                                                "minHeight": "110px",
                                                                "marginTop": "8px",
                                                                "padding": "12px",
                                                                "borderRadius": "12px",
                                                                "border": "1px solid #cbd5e1",
                                                                "lineHeight": "1.7",
                                                            },
                                                        ),
                                                    ],
                                                    style={"marginTop": "18px"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Sugestões"),
                                                        dcc.Textarea(
                                                            id="suggestion-input",
                                                            value="",
                                                            placeholder="Tem alguma sugestão para melhorar a experiência de aprendizagem?",
                                                            style={
                                                                "width": "100%",
                                                                "minHeight": "110px",
                                                                "marginTop": "8px",
                                                                "padding": "12px",
                                                                "borderRadius": "12px",
                                                                "border": "1px solid #cbd5e1",
                                                                "lineHeight": "1.7",
                                                            },
                                                        ),
                                                    ],
                                                    style={"marginTop": "18px"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Conclusão final"),
                                                        dcc.Textarea(
                                                            id="final-conclusion-input",
                                                            value="",
                                                            placeholder="Escreva aqui sua conclusão final sobre a sessão completa.",
                                                            style={
                                                                "width": "100%",
                                                                "minHeight": "180px",
                                                                "marginTop": "8px",
                                                                "padding": "12px",
                                                                "borderRadius": "12px",
                                                                "border": "1px solid #cbd5e1",
                                                                "lineHeight": "1.7",
                                                            },
                                                        ),
                                                    ],
                                                    style={"marginTop": "18px"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Button("Enviar resultados", id="send-results-btn", n_clicks=0),
                                                        html.Div(id="send-results-status", style={"minHeight": "24px", "fontWeight": "bold"}),
                                                    ],
                                                    style={"marginTop": "18px", "display": "flex", "gap": "12px", "flexWrap": "wrap", "alignItems": "center"},
                                                ),
                                            ],
                                            id="exercise-results-section",
                                            style={"display": "none"},
                                        ),
                                        html.Div(id="exercise-feedback", children=build_exercise_feedback()),
                                    ],
                                    className="panel-card",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H3("Progresso salvo"),
                                                html.Div(id="exercise-progress-panel", children=build_exercise_progress_panel(initial_exercise_progress)),
                                            ],
                                            style={
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "padding": "16px",
                                                "background": "#ffffff",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.H3("Dinâmica da aba"),
                                                html.P(
                                                    "A aba agora segue uma sessão em etapas: resolver cada desafio com a simulação, escrever uma conclusão final e só então enviar o relatório completo, em fluxo mais próximo ao modelo das simulações HTML.",
                                                    style={"lineHeight": "1.8"},
                                                ),
                                                html.P(
                                                    "Cada etapa ainda usa os critérios automáticos da própria simulação, mas o envio para planilha e e-mails passou a acontecer no fim da sessão, junto com o resumo final do estudante.",
                                                    style={"lineHeight": "1.8"},
                                                ),
                                            ],
                                            style={
                                                "marginTop": "18px",
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "padding": "16px",
                                                "background": "#ffffff",
                                            },
                                        ),
                                    ],
                                    className="panel-card",
                                ),
                            ],
                            className="exercise-grid",
                        )
                    ],
                ),
            ]
        ),
        html.Footer(
            html.P(
                [
                    "Simulacao parte do repositorio ",
                    html.Strong("Simulacoes Interativas de Fisica"),
                    " | DOI: ",
                    html.A(
                        SIMULATION_DOI,
                        href=f"https://doi.org/{SIMULATION_DOI}",
                        target="_blank",
                        style={"color": "#1d4ed8"},
                    ),
                    " | Licenca MIT | Prof. Flavio Ambrosio - CEAN",
                ]
            ),
            className="simulation-footer",
        ),
    ],
    className="app-shell",
)


@app.callback(
    Output("amp-table", "data"),
    Output("history-store", "data"),
    Output("status-message", "children"),
    Output("smoothing-slider", "value"),
    Output("freq-delta-slider", "value"),
    Output("max-iter-slider", "value"),
    Input("optimize-btn", "n_clicks"),
    Input("reset-btn", "n_clicks"),
    Input("mobile-apply-btn", "n_clicks"),
    State("amp-table", "data"),
    State("max-iter-slider", "value"),
    State("smoothing-slider", "value"),
    State("freq-delta-slider", "value"),
    State("mobile-frequency-picker", "value"),
    State("mobile-amp1-input", "value"),
    State("mobile-amp2-input", "value"),
    State("history-store", "data"),
    prevent_initial_call=True,
    running=[
        (Output("optimization-indicator", "children"), "Otimização em andamento...", ""),
        (Output("optimize-btn", "disabled"), True, False),
        (Output("reset-btn", "disabled"), True, False),
        (Output("mobile-apply-btn", "disabled"), True, False),
    ],
)
def handle_actions(
    optimize_clicks,
    reset_clicks,
    mobile_apply_clicks,
    table_data,
    max_iterations,
    smoothing_window,
    freq_delta,
    mobile_frequency,
    mobile_amp1,
    mobile_amp2,
    history_data,
):
    trigger = ctx.triggered_id
    if table_data is None:
        table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
    if history_data is None:
        history_data = initial_history
    amps1, amps2 = table_data_to_amps(table_data)

    if trigger == "mobile-apply-btn":
        # No celular, a edição acontece frequência por frequência para manter a interface legível.
        current_frequency = int(mobile_frequency or FREQS[0])
        updated_table = [dict(row) for row in table_data]
        selected_index = int(np.where(FREQS == current_frequency)[0][0])
        updated_table[selected_index]["onda1"] = round(clamp_amp(mobile_amp1), TABLE_DECIMALS)
        updated_table[selected_index]["onda2"] = round(clamp_amp(mobile_amp2), TABLE_DECIMALS)
        status = f"Frequência {current_frequency} THz atualizada pelo editor móvel."
        return updated_table, history_data, status, no_update, no_update, no_update

    if trigger == "reset-btn":
        zero_table = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
        history = {
            "before1": ZERO_AMPS.tolist(),
            "before2": ZERO_AMPS.tolist(),
            "after1": ZERO_AMPS.tolist(),
            "after2": ZERO_AMPS.tolist(),
            "after_diff": None,
            "has_optimization": False,
        }
        return (
            zero_table,
            history,
            "Tudo zerado. Ajuste as amplitudes novamente.",
            DEFAULT_SMOOTHING,
            DEFAULT_FREQ_DELTA,
            2000,
        )

    # Quando não é edição móvel nem reset, a ação restante é a otimização automática do espectro.
    optimized1, optimized2, final_diff, reason = optimize_amplitudes(
        amps1,
        amps2,
        int(max_iterations),
        smoothing_window=smoothing_window,
        freq_delta=freq_delta,
    )
    optimized_table = amps_to_table_data(optimized1, optimized2)
    displayed1, displayed2 = table_data_to_amps(optimized_table)
    displayed_diff = max_envelope_difference(displayed1, displayed2, smoothing_window)
    history = {
        "before1": amps1.tolist(),
        "before2": amps2.tolist(),
        "after1": displayed1.tolist(),
        "after2": displayed2.tolist(),
        "after_diff": float(displayed_diff),
        "has_optimization": True,
    }

    if reason == "blocked":
        status = "Nenhuma frequência ficou disponível para variar na janela escolhida."
    elif displayed_diff <= TARGET_DIFF:
        status = f"Concluído: diferença máxima entre envelopes = {displayed_diff:.4f}"
    elif reason == "limit":
        status = f"Parada pelo limite de {int(max_iterations)} iterações. Diferença = {displayed_diff:.4f}"
    else:
        status = f"Otimização parcial: diferença máxima = {displayed_diff:.4f}"

    return optimized_table, history, status, no_update, no_update, no_update


@app.callback(
    Output("rgb-refresh-message", "children"),
    Input("rgb-refresh-btn", "n_clicks"),
    prevent_initial_call=True,
)
def refresh_lab_rgb(refresh_clicks):
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"Laboratório RGB atualizado às {timestamp}."


@app.callback(
    Output("intensity-graph", "figure"),
    Output("main-graph", "figure"),
    Output("summary-box", "children"),
    Output("control-note-box", "children"),
    Output("fourier-before", "children"),
    Output("fourier-after", "children"),
    Output("hilbert-smoothing-note", "children"),
    Output("hilbert-delta-note", "children"),
    Output("rgb-scale-graph", "figure"),
    Output("rgb-cards-container", "children"),
    Output("mobile-visual-content", "children"),
    Input("amp-table", "data"),
    Input("history-store", "data"),
    Input("rgb-mode", "value"),
    Input("rgb-refresh-btn", "n_clicks"),
    Input("smoothing-slider", "value"),
    Input("freq-delta-slider", "value"),
    Input("mobile-visual-view", "value"),
    Input("time-window-selector", "value"),
)
def refresh_outputs(
    table_data,
    history_data,
    rgb_mode,
    rgb_refresh_clicks,
    smoothing_window,
    freq_delta,
    mobile_visual_view,
    time_window_fs,
):
    if table_data is None:
        table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
    if history_data is None:
        history_data = initial_history
    if rgb_mode is None:
        rgb_mode = "visual"
    if smoothing_window is None:
        smoothing_window = DEFAULT_SMOOTHING
    if freq_delta is None:
        freq_delta = DEFAULT_FREQ_DELTA
    if mobile_visual_view is None:
        mobile_visual_view = "main"
    if time_window_fs is None:
        time_window_fs = DEFAULT_TIME_WINDOW_FS

    # Este callback reconstrói praticamente toda a página a partir do estado atual da tabela e do histórico.
    current1, current2 = table_data_to_amps(table_data)

    before1 = np.array(history_data.get("before1", current1.tolist()), dtype=float)
    before2 = np.array(history_data.get("before2", current2.tolist()), dtype=float)
    after1 = np.array(history_data.get("after1", current1.tolist()), dtype=float)
    after2 = np.array(history_data.get("after2", current2.tolist()), dtype=float)
    has_optimization = has_valid_optimization_result(current1, current2, history_data)
    control_smoothing = sanitize_smoothing_window(smoothing_window, len(T))
    hilbert_smoothing_note, hilbert_delta_note = build_hilbert_notes(smoothing_window, freq_delta)

    fourier_before = generate_fourier_equation(before1, "Onda 1") + "\n\n" + generate_fourier_equation(before2, "Onda 2")
    fourier_after = generate_fourier_equation(after1, "Onda 1") + "\n\n" + generate_fourier_equation(after2, "Onda 2")
    control_note = html.Div(
        [
            html.Div(f"Janela de tempo exibida: {int(time_window_fs)} fs."),
            html.Div(f"Suavização atual dos envelopes: {control_smoothing} ponto(s)."),
            html.Div(f"Janela atual da otimização em delta f: {format_frequency_delta(freq_delta)}."),
        ]
    )

    if not has_optimization:
        before1 = current1.copy()
        before2 = current2.copy()
        after1 = ZERO_AMPS.copy()
        after2 = ZERO_AMPS.copy()

    # Os cartões RGB comparam o que havia antes da otimização com o que foi obtido depois.
    cards = [
        build_rgb_card(before1, "Onda 1", "Antes da otimização", rgb_mode),
        build_rgb_card(after1, "Onda 1", "Depois da otimização", rgb_mode) if has_optimization else build_pending_rgb_card("Onda 1", "Depois da otimização"),
        build_rgb_card(before2, "Onda 2", "Antes da otimização", rgb_mode),
        build_rgb_card(after2, "Onda 2", "Depois da otimização", rgb_mode) if has_optimization else build_pending_rgb_card("Onda 2", "Depois da otimização"),
    ]

    intensity_figure = build_intensity_figure(current1, current2)
    main_figure = build_main_figure(current1, current2, smoothing_window, time_window_fs)
    summary_box = build_summary(current1, current2, smoothing_window, freq_delta)
    mobile_visual_content = build_mobile_visual_content(
        mobile_visual_view,
        intensity_figure,
        main_figure,
        build_color_scale_figure(rgb_mode),
        cards,
        summary_box,
        control_note,
    )
    scale_figure = build_color_scale_figure(rgb_mode)

    return (
        intensity_figure,
        main_figure,
        summary_box,
        control_note,
        fourier_before,
        fourier_after,
        hilbert_smoothing_note,
        hilbert_delta_note,
        scale_figure,
        cards,
        mobile_visual_content,
    )


@app.callback(
    Output("mobile-frequency-picker", "value"),
    Input("mobile-prev-freq-btn", "n_clicks"),
    Input("mobile-next-freq-btn", "n_clicks"),
    State("mobile-frequency-picker", "value"),
    prevent_initial_call=True,
)
def browse_mobile_frequency(prev_clicks, next_clicks, current_frequency):
    trigger = ctx.triggered_id
    current_frequency = int(current_frequency or FREQS[0])
    current_index = int(np.where(FREQS == current_frequency)[0][0])

    if trigger == "mobile-prev-freq-btn":
        return int(FREQS[(current_index - 1) % N_FREQS])
    return int(FREQS[(current_index + 1) % N_FREQS])


@app.callback(
    Output("mobile-amp1-input", "value"),
    Output("mobile-amp2-input", "value"),
    Output("mobile-frequency-position", "children"),
    Output("mobile-active-summary", "children"),
    Input("amp-table", "data"),
    Input("mobile-frequency-picker", "value"),
)
def sync_mobile_editor(table_data, mobile_frequency):
    if table_data is None:
        table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)

    current_frequency = int(mobile_frequency or FREQS[0])
    row_lookup = {int(row["frequencia"]): row for row in table_data}
    current_row = row_lookup.get(current_frequency, {"onda1": 0, "onda2": 0})
    current_index = int(np.where(FREQS == current_frequency)[0][0])
    position_text = f"Editando {current_frequency} THz ({current_index + 1} de {N_FREQS})."

    return (
        current_row.get("onda1", 0),
        current_row.get("onda2", 0),
        position_text,
        build_mobile_active_summary(table_data),
    )


@app.callback(
    Output("exercise-store", "data"),
    Output("exercise-progress-store", "data"),
    Output("exercise-title", "children"),
    Output("exercise-difficulty", "children"),
    Output("exercise-prompt", "children"),
    Output("exercise-rubric", "children"),
    Output("exercise-feedback", "children"),
    Output("exercise-progress-panel", "children"),
    Output("exercise-answer", "value"),
    Output("exercise-stage-indicator", "children"),
    Output("exercise-answer-section", "style"),
    Output("exercise-step-actions", "style"),
    Output("exercise-conclusion-section", "style"),
    Output("exercise-results-section", "style"),
    Output("exercise-results-summary", "children"),
    Output("session-conclusion-text", "value"),
    Output("final-conclusion-input", "value"),
    Input("new-exercise-btn", "n_clicks"),
    Input("submit-exercise-btn", "n_clicks"),
    Input("next-exercise-btn", "n_clicks"),
    Input("skip-exercise-btn", "n_clicks"),
    Input("submit-session-conclusion-btn", "n_clicks"),
    State("exercise-store", "data"),
    State("exercise-progress-store", "data"),
    State("amp-table", "data"),
    State("exercise-answer", "value"),
    State("session-conclusion-text", "value"),
    State("smoothing-slider", "value"),
    State("freq-delta-slider", "value"),
    State("history-store", "data"),
    prevent_initial_call=True,
)
def handle_exercises(
    new_exercise_clicks,
    submit_exercise_clicks,
    next_exercise_clicks,
    skip_exercise_clicks,
    submit_session_conclusion_clicks,
    exercise_data,
    progress_data,
    table_data,
    answer_text,
    session_conclusion_text,
    smoothing_window,
    freq_delta,
    history_data,
):
    trigger = ctx.triggered_id
    session_data = normalize_exercise_session(exercise_data)
    progress_data = progress_data or initial_exercise_progress.copy()

    if trigger == "new-exercise-btn":
        # Uma sessão nova sorteia as etapas, mas mantém o histórico global salvo no navegador.
        session_data = create_exercise_session()
        feedback = {
            "title": "Nova sessão sorteada",
            "message": "Um novo conjunto de etapas foi preparado. O progresso histórico do navegador foi mantido.",
            "details": ["Resolva as etapas na ordem e escreva a conclusão final antes do envio."],
            "accent": "#2563eb",
            "background": "#eff6ff",
        }
        return build_exercise_stage_outputs(
            session_data,
            progress_data,
            feedback,
            answer_value="",
            session_conclusion_value="",
            final_conclusion_value="",
        )

    if trigger == "submit-session-conclusion-btn":
        # Depois das etapas, a sessão só avança para resultados quando existe uma conclusão final escrita.
        if session_data.get("stage") != "conclusion":
            feedback = {
                "title": "Conclusão fora de etapa",
                "message": "A conclusão final só pode ser enviada depois que todas as etapas forem resolvidas ou puladas.",
                "details": [],
                "accent": "#b45309",
                "background": "#fffbeb",
            }
            return build_exercise_stage_outputs(session_data, progress_data, feedback, answer_value=answer_text or "", session_conclusion_value=session_conclusion_text or "")

        final_text = (session_conclusion_text or "").strip()
        if not final_text:
            feedback = {
                "title": "Conclusão obrigatória",
                "message": "Escreva a conclusão final da sessão antes de avançar para os resultados.",
                "details": ["Use algumas linhas para relacionar os ajustes feitos na simulação e o que você observou nos envelopes e nas cores."],
                "accent": "#b91c1c",
                "background": "#fef2f2",
            }
            return build_exercise_stage_outputs(session_data, progress_data, feedback, answer_value=answer_text or "", session_conclusion_value=session_conclusion_text or "")

        session_data["stage"] = "results"
        session_data["final_conclusion"] = final_text
        feedback = {
            "title": "Resultados prontos",
            "message": "A sessão foi consolidada. Agora complete os dados finais e envie o relatório.",
            "details": ["Revise o resumo da sessão antes de clicar em Enviar resultados."],
            "accent": "#15803d",
            "background": "#ecfdf5",
        }
        return build_exercise_stage_outputs(
            session_data,
            progress_data,
            feedback,
            answer_value="",
            session_conclusion_value=final_text,
            final_conclusion_value=final_text,
        )

    if session_data.get("stage") != "exercise":
        if session_data.get("stage") == "conclusion":
            feedback = {
                "title": "Conclusão final pendente",
                "message": "As etapas guiadas já terminaram. Agora escreva a conclusão final da sessão e avance para os resultados.",
                "details": ["Depois disso, o envio do relatório completo será liberado."],
                "accent": "#2563eb",
                "background": "#eff6ff",
            }
        else:
            feedback = {
                "title": "Resultados prontos para envio",
                "message": "A sessão já foi consolidada. Complete os dados finais e envie o relatório para a planilha e para os e-mails.",
                "details": ["Se os campos finais já estiverem preenchidos, basta clicar em Enviar resultados."],
                "accent": "#15803d",
                "background": "#ecfdf5",
            }
        return build_exercise_stage_outputs(session_data, progress_data, feedback, answer_value=answer_text or "", session_conclusion_value=session_conclusion_text or "")

    if trigger == "skip-exercise-btn":
        # Pular registra a etapa como não resolvida, mas mantém o fluxo didático avançando para a próxima.
        current_exercise = get_current_session_exercise(session_data)
        stage_statuses, correct_count, partial_count, incorrect_count = update_stage_statuses(
            progress_data,
            current_exercise["title"],
            "pulado",
            0,
        )
        completed_count = len(session_data.get("results", [])) + 1
        session_data["results"] = list(session_data.get("results", [])) + [{
            "correct": False,
            "skipped": True,
            "attempts": int(session_data.get("current_attempts", 0)),
            "score": 0,
            "result": "pulado",
        }]
        session_data["skipped_questions"] = int(session_data.get("skipped_questions", 0)) + 1
        session_data["current_attempts"] = 0
        if completed_count >= len(session_data.get("exercises", [])):
            session_data["stage"] = "conclusion"
        else:
            session_data["current_index"] = int(session_data.get("current_index", 0)) + 1

        updated_progress = {
            "attempts": int(progress_data.get("attempts", 0)) + 1,
            "correct": correct_count,
            "partial": partial_count,
            "incorrect": incorrect_count,
            "streak": 0,
            "best_streak": int(progress_data.get("best_streak", 0)),
            "last_score": 0,
            "best_score": int(progress_data.get("best_score", 0)),
            "stage_statuses": stage_statuses,
            "history": list(progress_data.get("history", [])) + [{
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "title": current_exercise["title"],
                "result": "pulado",
                "score": 0,
                "metric": "etapa pulada pelo estudante",
            }],
        }
        updated_progress["history"] = updated_progress["history"][-12:]
        feedback = {
            "title": "Etapa pulada",
            "message": "A etapa foi registrada como pulada e a sessão seguiu para a próxima atividade.",
            "details": ["No relatório final, esta etapa contará como não resolvida."],
            "accent": "#b45309",
            "background": "#fffbeb",
        }
        return build_exercise_stage_outputs(session_data, updated_progress, feedback, answer_value="", session_conclusion_value=session_conclusion_text or "")

    if not (answer_text or "").strip():
        feedback = {
            "title": "Resposta curta obrigatória",
            "message": "Escreva uma resposta curta para registrar o que você observou nesta etapa antes de verificar.",
            "details": ["A ideia é manter uma justificativa rápida, não uma conclusão longa."],
            "accent": "#b91c1c",
            "background": "#fef2f2",
        }
        return build_exercise_stage_outputs(session_data, progress_data, feedback, answer_value=answer_text or "", session_conclusion_value=session_conclusion_text or "")

    # A avaliação cruza o estado numérico da simulação com a justificativa curta escrita pelo estudante.
    metrics = collect_simulation_metrics(table_data, history_data, smoothing_window, freq_delta)
    current_exercise = get_current_session_exercise(session_data)
    passed, partial, total_score, feedback_data, metric_summary, result_label = evaluate_exercise(current_exercise, metrics, answer_text)
    stage_statuses, correct_count, partial_count, incorrect_count = update_stage_statuses(
        progress_data,
        current_exercise["title"],
        result_label,
        total_score,
    )
    advance_requested = trigger == "next-exercise-btn"
    submitted_at = datetime.now()
    timestamp = submitted_at.strftime("%H:%M:%S")
    next_streak = int(progress_data.get("streak", 0)) + 1 if passed else 0
    updated_progress = {
        "attempts": int(progress_data.get("attempts", 0)) + 1,
        "correct": correct_count,
        "partial": partial_count,
        "incorrect": incorrect_count,
        "streak": next_streak,
        "best_streak": max(int(progress_data.get("best_streak", 0)), next_streak),
        "last_score": total_score,
        "best_score": max(int(progress_data.get("best_score", 0)), total_score),
        "stage_statuses": stage_statuses,
        "history": list(progress_data.get("history", [])) + [
            {
                "timestamp": timestamp,
                "title": current_exercise["title"],
                "result": result_label,
                "score": total_score,
                "metric": metric_summary,
            }
        ],
    }
    updated_progress["history"] = updated_progress["history"][-12:]

    session_data["current_attempts"] = int(session_data.get("current_attempts", 0)) + 1

    if passed or advance_requested:
        # Uma etapa pode avançar por acerto pleno ou por decisão explícita de seguir adiante.
        completed_count = len(session_data.get("results", [])) + 1
        session_data["results"] = list(session_data.get("results", [])) + [{
            "correct": passed,
            "skipped": False,
            "attempts": int(session_data.get("current_attempts", 0)),
            "score": total_score,
            "result": result_label,
        }]
        session_data["current_attempts"] = 0
        if completed_count >= len(session_data.get("exercises", [])):
            session_data["stage"] = "conclusion"
            feedback_data = append_feedback_detail(feedback_data, "Todas as etapas guiadas foram concluídas. Agora escreva a conclusão final da sessão.")
        else:
            session_data["current_index"] = int(session_data.get("current_index", 0)) + 1
            if passed:
                feedback_data = append_feedback_detail(feedback_data, "Etapa concluída. A próxima atividade já está disponível.")
            else:
                feedback_data = append_feedback_detail(feedback_data, "A etapa foi registrada e a sessão avançou para a próxima atividade, mesmo sem atingir totalmente a meta.")
        return build_exercise_stage_outputs(session_data, updated_progress, feedback_data, answer_value="", session_conclusion_value=session_conclusion_text or "")

    feedback_data = append_feedback_detail(
        feedback_data,
        "Você pode ajustar novamente a simulação e reenviar esta mesma etapa ou usar o botão de pular.",
    )
    return build_exercise_stage_outputs(session_data, updated_progress, feedback_data, answer_value=answer_text, session_conclusion_value=session_conclusion_text or "")


@app.callback(
    Output("student-grade", "value"),
    Output("student-class", "value"),
    Input("student-track", "value"),
    State("student-grade", "value"),
    State("student-class", "value"),
    prevent_initial_call=False,
)
def sync_student_group_with_track(student_track, current_grade, current_class):
    # Se a trilha já carrega a informação da turma, o formulário final pode ser parcialmente preenchido sozinho.
    if not student_track:
        return current_grade or "", current_class or ""

    inferred_grade, inferred_class = infer_grade_class_from_track(student_track)
    return inferred_grade or current_grade or "", inferred_class or current_class or ""


@app.callback(
    Output("student-name", "options"),
    Output("student-name", "value"),
    Output("student-name-helper", "children"),
    Input("student-track", "value"),
    Input("student-grade", "value"),
    Input("student-class", "value"),
    State("student-name", "value"),
)
def sync_student_name_options(student_track, student_grade, student_class, current_name):
    # A lista de nomes depende da combinação atual de trilha, série e turma.
    options = build_student_name_options(student_track, student_grade, student_class)
    option_values = {option["value"] for option in options}
    selected_name = current_name if current_name in option_values else ""

    if options:
        helper_text = f"{len(options)} estudante(s) disponivel(is) para a selecao atual."
    elif student_track or (student_grade and student_class):
        helper_text = "Nenhum estudante encontrado para essa combinacao. Confira trilha, serie e turma."
    else:
        helper_text = "Selecione trilha ou serie/turma para carregar a lista de estudantes."

    return options, selected_name, helper_text


@app.callback(
    Output("student-access-store", "data"),
    Output("student-access-status", "children"),
    Output("student-access-status", "style"),
    Input("student-unlock-btn", "n_clicks"),
    State("student-access-password", "value"),
    State("student-access-store", "data"),
    prevent_initial_call=True,
)
def unlock_student_mode(unlock_clicks, raw_password, access_state):
    _ = unlock_clicks
    base_style = {"marginTop": "8px", "fontWeight": "bold"}
    state = access_state if isinstance(access_state, dict) else {"authenticated": False}

    if is_student_access_granted(state):
        return state, "Acesso de estudante liberado para esta sessao.", dict(base_style, color="#15803d")

    if hash_student_access_password(raw_password) == STUDENT_ACCESS_PASSWORD_HASH:
        new_state = {
            "authenticated": True,
            "authenticated_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }
        return new_state, "Acesso de estudante liberado para esta sessao.", dict(base_style, color="#15803d")

    return state, "Senha incorreta. Modo visitante continua ativo.", dict(base_style, color="#b91c1c")


@app.callback(
    Output("student-auth-section", "style"),
    Output("student-fields-section", "style"),
    Output("visitor-fields-section", "style"),
    Output("submission-mode", "value"),
    Output("student-access-status", "children", allow_duplicate=True),
    Output("student-access-status", "style", allow_duplicate=True),
    Input("submission-mode", "value"),
    Input("student-access-store", "data"),
    prevent_initial_call=False,
)
def sync_submission_mode_sections(submission_mode, access_state):
    mode = (submission_mode or "visitor").strip().lower()
    authenticated = is_student_access_granted(access_state)
    base_status_style = {"marginTop": "8px", "fontWeight": "bold"}

    if mode == "student":
        if authenticated:
            return (
                {"marginTop": "12px", "display": "none"},
                {"display": "block"},
                {"display": "none"},
                "student",
                "Acesso de estudante liberado para esta sessao.",
                dict(base_status_style, color="#15803d"),
            )

        return (
            {"marginTop": "12px", "display": "block"},
            {"display": "none"},
            {"marginTop": "18px", "display": "flex", "gap": "12px", "flexWrap": "wrap"},
            "visitor",
            "Para proteger os dados da turma, o modo estudante exige senha. Modo visitante ativo.",
            dict(base_status_style, color="#b45309"),
        )

    return (
        {"marginTop": "12px", "display": "none"},
        {"display": "none"},
        {"marginTop": "18px", "display": "flex", "gap": "12px", "flexWrap": "wrap"},
        "visitor",
        "Modo visitante ativo. Para usar listas de estudantes, selecione Estudante e informe a senha.",
        dict(base_status_style, color="#b45309"),
    )


@app.callback(
    Output("send-results-status", "children"),
    Output("send-results-status", "style"),
    Input("send-results-btn", "n_clicks"),
    State("exercise-store", "data"),
    State("submission-mode", "value"),
    State("student-access-store", "data"),
    State("student-name", "value"),
    State("student-track", "value"),
    State("student-grade", "value"),
    State("student-class", "value"),
    State("student-bimester", "value"),
    State("student-email", "value"),
    State("visitor-name", "value"),
    State("visitor-email", "value"),
    State("criticism-input", "value"),
    State("suggestion-input", "value"),
    State("final-conclusion-input", "value"),
    prevent_initial_call=True,
)
def handle_final_results_send(
    send_results_clicks,
    exercise_data,
    submission_mode,
    access_state,
    student_name,
    student_track,
    student_grade,
    student_class,
    student_bimester,
    student_email,
    visitor_name,
    visitor_email,
    criticism,
    suggestion,
    final_conclusion,
):
    _ = send_results_clicks
    session_data = normalize_exercise_session(exercise_data)
    status_style = {"minHeight": "24px", "fontWeight": "bold"}

    # O envio final só faz sentido quando a sessão já passou da etapa de exercícios para a etapa de resultados.
    if session_data.get("stage") != "results":
        return "Finalize primeiro a sessão de exercícios para liberar o envio.", dict(status_style, color="#b91c1c")

    mode = (submission_mode or "visitor").strip().lower()
    is_student_mode = mode == "student" and is_student_access_granted(access_state)

    if mode == "student" and not is_student_mode:
        return "Modo estudante exige senha válida. Libere o acesso ou envie como visitante.", dict(status_style, color="#b91c1c")

    final_name = (student_name or "").strip() if is_student_mode else (visitor_name or "").strip()
    final_email = (student_email or "").strip() if is_student_mode else (visitor_email or "").strip()
    final_track = (student_track or "").strip() if is_student_mode else "Visitante"
    final_grade = (student_grade or "").strip() if is_student_mode else "Visitante"
    final_class = (student_class or "").strip() if is_student_mode else "Visitante"
    final_bimester = (student_bimester or "").strip() if is_student_mode else "Visitante"

    if not (final_conclusion or "").strip():
        return "Preencha a conclusao final antes de enviar.", dict(status_style, color="#b91c1c")

    if not final_name:
        if is_student_mode:
            return "Preencha nome do estudante antes de enviar.", dict(status_style, color="#b91c1c")
        return "Preencha nome do visitante antes de enviar.", dict(status_style, color="#b91c1c")

    if is_student_mode and (not final_grade or not final_class or not final_bimester):
        return "No modo estudante, preencha serie, turma e bimestre antes de enviar.", dict(status_style, color="#b91c1c")

    payload = build_final_session_payload(
        session_data,
        final_name,
        final_track,
        final_grade,
        final_class,
        final_bimester,
        final_email,
        criticism,
        suggestion,
        final_conclusion,
    )
    # Este é o fechamento do fluxo pedagógico: consolida a sessão e dispara gravação + comunicações.
    success, message = send_final_session_results(payload, final_email)

    if success:
        return "✅ Resultados enviados com sucesso para a planilha e para os e-mails.", dict(status_style, color="#15803d")

    return f"❌ O envio não foi concluído por completo: {message}", dict(status_style, color="#b91c1c")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8050"))
    app.run(host="0.0.0.0", port=port, debug=False)