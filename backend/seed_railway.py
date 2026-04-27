"""
Script de inicializacion de BD para Railway.
Se ejecuta como build step (NIXPACKS_BUILD_CMD o railway.json buildCommand).

Orden:
  1) crear tablas SQL (idempotente: CREATE TABLE IF NOT EXISTS)
  2) poblar datos (solo si la BD esta vacia)
  3) actualizar contrasenas con hash werkzeug

Si MYSQL_URL no esta definida, el script termina con codigo 0
(para que el build no falle cuando no hay plugin MySQL conectado).
"""
import os
import sys
from pathlib import Path
import pymysql
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash

MYSQL_URL = os.getenv('MYSQL_URL', '')
if not MYSQL_URL:
    print("[seed] MYSQL_URL no definida, omitiendo seed.")
    sys.exit(0)

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
            msg = str(e)
            if 'Duplicate entry' not in msg and 'already exists' not in msg:
                print(f"  WARN: {msg[:200]}")
    conn.commit()
    cursor.close()
    conn.close()
    print(f"    {ok} OK, {errors} advertencias")


def seed_passwords():
    print("\n>>> Actualizando contrasenas...")
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
            print(f"  OK {username}")
        else:
            print(f"  -- {username} no encontrado")
    conn.commit()
    cursor.close()
    conn.close()
    print(f"    {actualizados} contrasenas actualizadas")


def aplicar_migraciones_pendientes():
    """ALTER TABLE idempotentes para BDs creadas con DDL anterior.
    Si la columna ya existe, se omite (consulta information_schema)."""
    columnas_a_agregar = [
        ('usuario', 'intentos_fallidos', 'SMALLINT NOT NULL DEFAULT 0'),
        ('usuario', 'bloqueado_hasta',   'DATETIME NULL'),
        ('usuario', 'veces_bloqueado',   'SMALLINT NOT NULL DEFAULT 0'),
        ('usuario', 'ultima_salida',     'DATETIME NULL'),
    ]
    db_name = parsed.path.lstrip('/')
    conn = get_conn()
    cursor = conn.cursor()
    agregadas = 0
    for tabla, columna, definicion in columnas_a_agregar:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema=%s AND table_name=%s AND column_name=%s",
            (db_name, tabla, columna),
        )
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")
            agregadas += 1
            print(f"  + {tabla}.{columna}")
    conn.commit()
    cursor.close()
    conn.close()
    if agregadas:
        print(f">>> {agregadas} columnas agregadas")


def bd_ya_poblada():
    """Devuelve True si la tabla usuario existe y tiene >= 1 registro."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'usuario'")
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False
        cursor.execute("SELECT COUNT(*) FROM usuario")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count > 0
    except Exception as e:
        print(f"[seed] No se pudo verificar estado de BD: {e}")
        return False


def main():
    try:
        get_conn().close()
    except Exception as e:
        print(f"ERROR conectando a MySQL: {e}")
        sys.exit(1)

    if bd_ya_poblada():
        print("[seed] BD ya poblada, aplicando migraciones y refrescando contrasenas.")
        aplicar_migraciones_pendientes()
        seed_passwords()
        print("\n[seed] OK")
        return

    run_sql_file(base_dir / 'scrip creacion BD.txt')
    run_sql_file(base_dir / 'scrip poblacion.txt')
    aplicar_migraciones_pendientes()
    seed_passwords()
    print("\n[seed] OK")


if __name__ == '__main__':
    main()
