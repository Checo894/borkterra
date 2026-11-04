"""YACC de Terra: reconoce la gramática y construye instrucciones.

Las tuplas guardan lo que debe hacerse. Se ejecutan después de analizar
todo el archivo para poder elegir ramas y repetir bloques correctamente.
"""

import ply.yacc as yacc

from lexer import crear_lexer, tokens


precedence = (
    ("left", "+", "-"),
    ("left", "*", "/"),
    ("right", "NEGATIVO"),
)

# ----- REGLAS DE LA GRAMÁTICA -----


def p_programa(p):
    "programa : instrucciones"
    p[0] = p[1]


def p_instrucciones(p):
    """instrucciones : instrucciones instruccion
                     | vacio"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_vacio(p):
    "vacio :"


def p_asignacion(p):
    "instruccion : NOMBRE '=' expresion ';'"
    p[0] = ("asignar", p.lineno(1), p[1], p[3])


def p_accion(p):
    """instruccion : REGAR expresion ';'
                   | ILUMINAR expresion ';'"""
    p[0] = (p[1], p.lineno(1), p[2])


def p_mostrar(p):
    """instruccion : MOSTRAR expresion ';'
                   | MOSTRAR TEXTO ';'"""
    if p.slice[2].type == "TEXTO":
        valor = ("texto", p[2])
    else:
        valor = p[2]
    p[0] = ("mostrar", p.lineno(1), valor)


def p_reporte(p):
    "instruccion : REPORTE ';'"
    p[0] = ("reporte", p.lineno(1))


def p_repetir(p):
    "instruccion : REPETIR expresion '{' instrucciones '}'"
    p[0] = ("repetir", p.lineno(1), p[2], p[4])


def p_si(p):
    """instruccion : SI condicion '{' instrucciones '}'
                   | SI condicion '{' instrucciones '}' SINO '{' instrucciones '}'"""
    if len(p) == 10:
        alternativa = p[8]
    else:
        alternativa = []
    p[0] = ("si", p.lineno(1), p[2], p[4], alternativa)


def p_condicion(p):
    "condicion : expresion COMPARADOR expresion"
    p[0] = (p[2], p[1], p[3])


def p_expresion_binaria(p):
    """expresion : expresion '+' expresion
                 | expresion '-' expresion
                 | expresion '*' expresion
                 | expresion '/' expresion"""
    p[0] = ("operacion", p[2], p[1], p[3])


def p_expresion_negativa(p):
    "expresion : '-' expresion %prec NEGATIVO"
    p[0] = ("negativo", p[2])


def p_expresion_parentesis(p):
    "expresion : '(' expresion ')'"
    p[0] = p[2]


def p_expresion_valor(p):
    """expresion : NUMERO
                 | NOMBRE"""
    if p.slice[1].type == "NUMERO":
        tipo = "numero"
    else:
        tipo = "variable"
    p[0] = (tipo, p[1])


def p_error(token):
    if token is None:
        raise ValueError("Final inesperado: revisa si falta ';' o cerrar un bloque con '}'.")
    raise ValueError(f"Línea {token.lineno}: instrucción inválida cerca de {token.value!r}.")


def analizar(codigo):
    # No generamos archivos de tablas junto al código del alumno.
    parser = yacc.yacc(write_tables=False, debug=False)
    return parser.parse(codigo, lexer=crear_lexer())
