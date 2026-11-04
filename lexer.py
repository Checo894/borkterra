"""LEX de Terra: convierte las instrucciones en tokens."""

import json

import ply.lex as lex


# ----- PALABRAS RESERVADAS Y TOKENS -----

reservadas = {
    "regar": "REGAR",
    "iluminar": "ILUMINAR",
    "mostrar": "MOSTRAR",
    "reporte": "REPORTE",
    "si": "SI",
    "sino": "SINO",
    "repetir": "REPETIR",
}

tokens = ["NUMERO", "NOMBRE", "TEXTO", "COMPARADOR"] + list(reservadas.values())
literals = "+-*/=;{}()"
t_ignore = " \t\r"
t_ignore_COMENTARIO = r"\#[^\n]*"


# ----- REGLAS DEL LEXER -----

def t_COMPARADOR(t):
    r">=|<=|==|!=|>|<"
    return t


def t_NUMERO(t):
    r"\d+(\.\d+)?"
    if "." in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t


def t_TEXTO(t):
    r'"([^"\\\n]|\\["\\/bfnrt]|\\u[0-9a-fA-F]{4})*"'
    t.value = json.loads(t.value)
    return t


def t_NOMBRE(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    if t.value in reservadas:
        t.type = reservadas[t.value]
    else:
        t.type = "NOMBRE"
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    raise ValueError(f"Línea {t.lineno}: carácter no reconocido: {t.value[0]!r}.")


def crear_lexer():
    return lex.lex()
