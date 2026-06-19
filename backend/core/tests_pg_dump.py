import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings

from core.operations import run_db_backup
from core.pg_dump import (
    PgDumpNotFoundError,
    check_pg_dump,
    resolve_pg_dump_path,
)


class PgDumpResolverTests(TestCase):
    def test_resolve_from_pg_dump_path_env(self):
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
            path = tmp.name
        try:
            with override_settings(PG_DUMP_PATH=path):
                self.assertEqual(resolve_pg_dump_path(), path)
        finally:
            os.unlink(path)

    @patch('core.pg_dump.shutil.which', return_value='/usr/bin/pg_dump')
    @patch.dict(os.environ, {}, clear=True)
    def test_resolve_from_path(self, _which):
        with override_settings(PG_DUMP_PATH=''):
            self.assertEqual(resolve_pg_dump_path(), '/usr/bin/pg_dump')

    @patch('core.pg_dump.shutil.which', return_value=None)
    @patch('core.pg_dump._windows_pg_roots', return_value=[])
    @patch.dict(os.environ, {}, clear=True)
    def test_resolve_missing(self, _roots, _which):
        with override_settings(PG_DUMP_PATH=''):
            self.assertIsNone(resolve_pg_dump_path())
            result = check_pg_dump()
            self.assertFalse(result['ok'])
            self.assertIn('PG_DUMP_PATH', result['error'])

    @override_settings(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'test',
                'USER': 'u',
                'PASSWORD': 'p',
                'HOST': 'localhost',
                'PORT': 5432,
            },
        },
        BACKUP_DIR=tempfile.gettempdir(),
    )
    @patch('core.operations.resolve_pg_dump_path', return_value=None)
    def test_run_db_backup_raises_clear_error(self, _resolve):
        with self.assertRaises(PgDumpNotFoundError) as ctx:
            run_db_backup()
        self.assertIn('PG_DUMP_PATH', str(ctx.exception))

    @override_settings(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'test',
            },
        },
    )
    @patch('core.operations.check_pg_dump', return_value={'ok': False, 'error': 'missing'})
    def test_operations_snapshot_reports_pg_dump(self, _check):
        from core.operations import operations_snapshot

        snap = operations_snapshot()
        self.assertIn('pg_dump', snap)
        self.assertFalse(snap['pg_dump']['ok'])
        self.assertIn('pg_dump_missing', snap['alerts'])
