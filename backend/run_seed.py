"""
Corre un script SQL contra la base de datos de Railway.
Uso:
    python run_seed.py <mysql_url> [archivo.sql]

Ejemplos:
    python run_seed.py mysql://root:pass@host:3306/railway "../scrip creacion BD.txt"
    python run_seed.py mysql://root:pass@host:3306/railway "../scrip poblacion.txt"
"""
import sys
from pathlib import Path
import pymysql
from urllib.parse import urlparse

import os

url_str = sys.argv[1] if len(sys.argv) > 1 else os.getenv('MYSQL_URL', '')
if not url_str:
    print("Uso: python run_seed.py <mysql_url> [archivo.sql]")
    print("O define la variable de entorno MYSQL_URL")
    sys.exit(1)

sql_path = sys.argv[2] if len(sys.argv) > 2 else str(Path(__file__).parent.parent / 'scrip poblacion.txt')

parsed = urlparse(url_str)
conn = pymysql.connect(
    host=parsed.hostname,
    port=parsed.port or 3306,
    user=parsed.username,
    password=parsed.password,
    database=parsed.path.lstrip('/'),
    charset='utf8mb4',
    autocommit=False,
)

sql = Path(sql_path).read_text(encoding='utf-8')

# Separar por ; y filtrar statements problemáticos para Railway
skip_prefixes = ('create database', 'drop database', 'use ', 'set foreign_key_checks', 'set names')

statements = []
for s in sql.split(';'):
    s = s.strip()
    if not s:
        continue
    lower = s.lower().lstrip()
    if any(lower.startswith(p) for p in skip_prefixes):
        continue
    # Convertir CREATE TABLE a CREATE TABLE IF NOT EXISTS
    if lower.startswith('create table') and 'if not exists' not in lower:
        s = s.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS', 1)
        s = s.replace('create table', 'CREATE TABLE IF NOT EXISTS', 1)
    statements.append(s)

cursor = conn.cursor()
ok = errors = 0
for stmt in statements:
    try:
        cursor.execute(stmt)
        ok += 1
    except Exception as e:
        print(f"  WARN: {e}")
        errors += 1

conn.commit()
cursor.close()
conn.close()
print(f"\nFinalizado: {ok} OK, {errors} advertencias.")
