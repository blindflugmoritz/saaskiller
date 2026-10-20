"""
Legt die in DATABASE_URL genannte Postgres-Datenbank an, falls sie fehlt.

Übernommen aus albula-nair-game (dort aus albula-bernina-shop, 21.08.2026).
Ergänzt: zuerst wird die Ziel-DB direkt probiert. Existiert sie, passiert
nichts — so ist das Skript auch bei geteilten DBs (deploy-init.sh
DB_MODE=shared) und SQLite ein No-op und darf immer vor migrate stehen.

Warum das existiert (gemessen auf deplo.io, 19.08.2026): Auf einem eigenen
Postgres-Server (DB_MODE=server / dedicated) zeigt der Connection-String auf
die Default-DB «postgres». Dort darf der App-User kein DDL — seit
PostgreSQL 15 gehört das public-Schema dem Owner der Datenbank. migrate stirbt
mit «permission denied for schema public».

Deshalb steht ein eigener DB-Name im URL (…/<projekt>_<umgebung>?sslmode=require).
Dieses Skript legt die DB an, mit dem App-User als Owner — als Owner darf er
darin Tabellen bauen. Idempotent.

Läuft bewusst ohne Django (kein settings-Import), damit es im Deploy-Job vor
jedem migrate stehen kann:

    python scripts/bootstrap_database.py && python manage.py migrate …
"""
import os
import sys
from urllib.parse import urlsplit, urlunsplit

import dj_database_url
import psycopg


def admin_url(url: str) -> str:
    """Derselbe Server und User, aber Default-DB «postgres»; Query (sslmode) bleibt."""
    return urlunsplit(urlsplit(url)._replace(path="/postgres"))


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url or not url.startswith("postgres"):
        # SQLite/leer: nichts zu bootstrappen — Django legt die Datei selbst an.
        print("bootstrap: kein Postgres-URL, nichts zu tun")
        return 0

    config = dj_database_url.parse(url)
    target, user = config["NAME"], config["USER"]

    try:
        with psycopg.connect(url):
            print(f"bootstrap: datenbank {target} erreichbar")
            return 0
    except psycopg.OperationalError:
        pass  # fehlt (oder Server nicht erreichbar — dann scheitert auch der Weg unten)

    with psycopg.connect(admin_url(url), autocommit=True) as conn:
        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", [target]
        ).fetchone()
        if exists:
            print(f"bootstrap: datenbank {target} existiert")
        else:
            conn.execute(f'CREATE DATABASE "{target}" OWNER "{user}"')
            print(f"bootstrap: datenbank {target} angelegt (owner {user})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
