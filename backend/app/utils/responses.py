from flask import jsonify


def ok(data, status: int = 200):
    return jsonify(data), status


def error(mensaje: str, status: int = 400):
    return jsonify({'error': mensaje}), status


def paginado(items: list, total: int, pagina: int, por_pagina: int):
    return jsonify({
        'items': items,
        'total': total,
        'pagina': pagina,
        'por_pagina': por_pagina,
        'paginas': (total + por_pagina - 1) // por_pagina,
    })
