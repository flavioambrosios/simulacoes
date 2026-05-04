from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass
class Settings:
    provider: str
    api_key: str
    model: str
    sqlite_path: Path
    request_timeout: int

    @classmethod
    def from_env(cls, base_dir: Path) -> 'Settings':
        load_env_file(base_dir / '.env')

        provider = os.getenv('AI_PROVIDER', 'openai').strip().lower()
        default_model = 'gpt-4o-mini' if provider == 'openai' else 'gemini-2.0-flash'
        sqlite_default = base_dir / 'notas.db'

        return cls(
            provider=provider,
            api_key=os.getenv('AI_API_KEY', '').strip(),
            model=os.getenv('AI_MODEL', default_model).strip(),
            sqlite_path=Path(os.getenv('SQLITE_PATH', str(sqlite_default))),
            request_timeout=int(os.getenv('AI_TIMEOUT_SECONDS', '60'))
        )