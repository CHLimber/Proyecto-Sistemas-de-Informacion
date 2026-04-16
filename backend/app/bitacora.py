from datetime import datetime


def log(accion: str, detalle: str, usuario: str = None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    quien = f"'{usuario}'" if usuario else 'sistema'
    print(f"[BITÁCORA] {accion} | {detalle} | por {quien} | {timestamp}")
