from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parent
APP_JS_PATH = ROOT / 'app.js'
ALUNOS_JS_PATH = ROOT / 'alunos.js'


def extract_apps_script_url(app_js_path: Path) -> str:
    content = app_js_path.read_text(encoding='utf-8')
    match = re.search(r"const\s+APPS_SCRIPT_URL\s*=\s*'([^']+)'", content)
    if not match:
        raise ValueError('Nao foi possivel localizar APPS_SCRIPT_URL em app.js.')
    return match.group(1)


def fetch_student_database(base_url: str) -> dict:
    response = requests.get(base_url, params={'action': 'students'}, timeout=30)
    response.raise_for_status()
    data = response.json()

    if data.get('status') != 'ok':
        raise ValueError(f"Resposta inesperada do Apps Script: {data}")

    database = data.get('studentDatabase')
    if not isinstance(database, dict):
        raise ValueError('O Apps Script nao retornou studentDatabase em formato valido.')

    return database


def write_alunos_js(database: dict, output_path: Path) -> None:
    serialized = json.dumps(database, ensure_ascii=False, indent=4)
    output_path.write_text(f'const STUDENT_DATABASE = {serialized};\n', encoding='utf-8')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Atualiza o arquivo alunos.js a partir da base publicada pelo Apps Script.'
    )
    parser.add_argument(
        '--url',
        help='URL do Apps Script. Se omitida, a URL sera lida de app.js.'
    )
    parser.add_argument(
        '--output',
        default=str(ALUNOS_JS_PATH),
        help='Caminho de saida para o arquivo alunos.js.'
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    base_url = args.url or extract_apps_script_url(APP_JS_PATH)
    output_path = Path(args.output).resolve()

    database = fetch_student_database(base_url)
    write_alunos_js(database, output_path)

    print(f'alunos.js atualizado com sucesso em: {output_path}')


if __name__ == '__main__':
    main()