import os
import shutil
from pathlib import Path

from django.conf import settings


class PgDumpNotFoundError(Exception):
    """pg_dump executable could not be located."""

    def __init__(self):
        super().__init__(
            'pg_dump not found. Install PostgreSQL client tools or set '
            'PG_DUMP_PATH to the full path (e.g. '
            r'C:\Program Files\PostgreSQL\16\bin\pg_dump.exe).'
        )


def resolve_pg_dump_path():
    override = os.getenv('PG_DUMP_PATH') or getattr(settings, 'PG_DUMP_PATH', '')
    if override:
        path = Path(override)
        if path.is_file():
            return str(path)

    found = shutil.which('pg_dump')
    if found:
        return found

    if os.name == 'nt':
        for base in _windows_pg_roots():
            if not base.is_dir():
                continue
            for version_dir in sorted(base.iterdir(), reverse=True):
                candidate = version_dir / 'bin' / 'pg_dump.exe'
                if candidate.is_file():
                    return str(candidate)

    return None


def _windows_pg_roots():
    roots = []
    for env_key in ('ProgramFiles', 'ProgramFiles(x86)'):
        root = os.environ.get(env_key)
        if root:
            roots.append(Path(root) / 'PostgreSQL')
    roots.append(Path(r'C:\Program Files\PostgreSQL'))
    roots.append(Path(r'C:\Program Files (x86)\PostgreSQL'))
    return roots


def check_pg_dump():
    path = resolve_pg_dump_path()
    if path:
        return {'ok': True, 'path': path}
    return {
        'ok': False,
        'error': (
            'pg_dump not found. Install PostgreSQL client tools or set '
            'PG_DUMP_PATH environment variable.'
        ),
    }


def uses_postgresql():
    engine = settings.DATABASES.get('default', {}).get('ENGINE', '')
    return 'postgresql' in engine
