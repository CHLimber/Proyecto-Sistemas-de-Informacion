"""
Script de inicializacion de BD para Railway.
Se ejecuta como pre-deploy step dentro de la red de Railway.
Orden: 1) crear tablas SQL  2) poblar datos  3) actualizar contraseñas
"""
import os
import sys
from pathlib import Path
import pymysql
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash

MYSQL_URL = os.getenv('MYSQL_URL', '')
if not MYSQL_URL:
    print("ERROR: MYSQL_URL no definida")
    sys.exit(1)

parsed = urlparse(MYSQL_URL)
base_dir = Path(__file__).parent


def get_conn():
    return pymysql.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/'),
        charset='utf8mb4',
        autocommit=False,
    )


def run_sql_file(filepath):
    print(f"\n>>> Ejecutando: {filepath.name}")
    sql = filepath.read_text(encoding='utf-8')
    skip_prefixes = ('create database', 'drop database', 'use ', 'set foreign_key_checks', 'set names')
    statements = []
    for s in sql.split(';'):
        s = s.strip()
        if not s:
            continue
        lower = s.lower()
        if any(lower.startswith(p) for p in skip_prefixes):
            continue
        if lower.startswith('create table') and 'if not exists' not in lower:
            s = s.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS', 1)
            s = s.replace('create table', 'CREATE TABLE IF NOT EXISTS', 1)
        statements.append(s)

    conn = get_conn()
    cursor = conn.cursor()
    ok = errors = 0
    for stmt in statements:
        try:
            cursor.execute(stmt)
            ok += 1
        except Exception as e:
            errors += 1
            if 'Duplicate entry' not in str(e):
                print(f"  WARN: {e}")
    conn.commit()
    cursor.close()
    conn.close()
    print(f"    {ok} OK, {errors} advertencias")


def seed_passwords():
    print("\n>>> Actualizando contraseñas...")
    PASSWORDS = {
        'admin.mendoza':   'Admin123!',
        'marco.ibanez':    'Tecnico123!',
        'luis.mamani':     'Tecnico123!',
        'ana.quispe':      'Atencion123!',
        'patricia.medina': 'Atencion123!',
        'roberto.flores':  'Campo123!',
        'miguel.torrez':   'Campo123!',
        'diego.rojas':     'Campo123!',
        'fernando.chavez': 'Campo123!',
        'sergio.pedraza':  'Campo123!',
    }
    conn = get_conn()
    cursor = conn.cursor()
    actualizados = 0
    for username, password in PASSWORDS.items():
        hashed = generate_password_hash(password)
        rows = cursor.execute(
            "UPDATE usuario SET password=%s WHERE username=%s",
            (hashed, username)
        )
        if rows:
            actualizados += 1
            print(f"  ✓ {username}")
        else:
            print(f"  ✗ {username} — no encontrado")
    conn.commit()
    cursor.close()
    conn.close()
    print(f"    {actualizados} contraseñas actualizadas")


# Verificar si ya hay datos (evitar re-seed innecesario)
try:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tablas = cursor.fetchall()
    cursor.close()
    conn.close()
except Exception as e:
    print(f"ERROR conectando a MySQL: {e}")
    sys.exit(1)

run_sql_file(base_dir / 'scrip creacion BD.txt')
run_sql_file(base_dir / 'scrip poblacion.txt')
seed_passwords()

print("\n✓ Seed completado.")
