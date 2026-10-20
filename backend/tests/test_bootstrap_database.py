import importlib.util
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import psycopg

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "bootstrap_database.py"
spec = importlib.util.spec_from_file_location("bootstrap_database", SCRIPT)
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)

SERVER_URL = "postgres://admin:pw@srv.n1.db.nineapis.ch/myapp_staging?sslmode=require"


def test_admin_url_swaps_db_name_and_keeps_query():
    assert bootstrap.admin_url(SERVER_URL) == (
        "postgres://admin:pw@srv.n1.db.nineapis.ch/postgres?sslmode=require"
    )


def test_admin_url_without_query():
    assert bootstrap.admin_url("postgres://u:p@h:5432/db") == "postgres://u:p@h:5432/postgres"


def test_sqlite_is_a_noop(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:////tmp/build.db")
    with mock.patch.object(bootstrap.psycopg, "connect") as connect:
        assert bootstrap.main() == 0
    connect.assert_not_called()


def test_reachable_target_skips_admin_connection(monkeypatch):
    # Shared DBs (postgresdatabase): the target exists and the user may not
    # reach "postgres" at all — so the script must stop after the first connect.
    monkeypatch.setenv("DATABASE_URL", SERVER_URL)

    @contextmanager
    def ok(*args, **kwargs):
        yield mock.MagicMock()

    with mock.patch.object(bootstrap.psycopg, "connect", side_effect=ok) as connect:
        assert bootstrap.main() == 0
    connect.assert_called_once_with(SERVER_URL)


def test_missing_target_is_created_via_admin_db(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", SERVER_URL)
    admin = mock.MagicMock()
    admin.execute.return_value.fetchone.return_value = None

    @contextmanager
    def admin_conn():
        yield admin

    calls = []

    def connect(url, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            raise psycopg.OperationalError('database "myapp_staging" does not exist')
        return admin_conn()

    with mock.patch.object(bootstrap.psycopg, "connect", side_effect=connect):
        assert bootstrap.main() == 0
    assert calls[1].endswith("/postgres?sslmode=require")
    admin.execute.assert_any_call('CREATE DATABASE "myapp_staging" OWNER "admin"')
