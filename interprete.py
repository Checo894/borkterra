"""Ejecuta las instrucciones de Terra y administra los recursos."""

import math


# ----- FUNCIONES -----

def comparar(simbolo, izquierda, derecha):
    if simbolo == ">":
        return izquierda > derecha
    elif simbolo == "<":
        return izquierda < derecha
    elif simbolo == ">=":
        return izquierda >= derecha
    elif simbolo == "<=":
        return izquierda <= derecha
    elif simbolo == "==":
        return izquierda == derecha
    elif simbolo == "!=":
        return izquierda != derecha


def formato(valor):
    return f"{valor:g}" if isinstance(valor, (int, float)) else valor


# ----- ESTADO Y EJECUCIÓN DEL INVERNADERO -----

class Invernadero:
    def __init__(self):
        self.variables = {"agua": 0, "energia": 0}
        self.riegos = 0
        self.iluminaciones = 0
        self.pasos = 0

    def evaluar(self, expresion):
        tipo = expresion[0]
        if tipo in ("numero", "texto"):
            resultado = expresion[1]
        elif tipo == "variable":
            nombre = expresion[1]
            if nombre not in self.variables:
                raise ValueError(f"La variable '{nombre}' no ha sido definida.")
            resultado = self.variables[nombre]
        elif tipo == "negativo":
            resultado = -self.evaluar(expresion[1])
        else:
            simbolo, izquierda, derecha = expresion[1:]
            a, b = self.evaluar(izquierda), self.evaluar(derecha)
            if simbolo == "/" and b == 0:
                raise ValueError("No se puede dividir entre cero.")
            if simbolo == "+":
                resultado = a + b
            elif simbolo == "-":
                resultado = a - b
            elif simbolo == "*":
                resultado = a * b
            elif simbolo == "/":
                resultado = a / b
        if isinstance(resultado, (int, float)):
            try:
                finito = math.isfinite(resultado)
            except OverflowError:
                finito = False
            if not finito:
                raise ValueError("El resultado numérico es demasiado grande.")
        return resultado

    def ejecutar(self, instrucciones):
        for instruccion in instrucciones:
            try:
                self.ejecutar_instruccion(instruccion)
            except ValueError as error:
                # Conservamos la línea de la instrucción interior en bloques anidados.
                if str(error).startswith("Línea "):
                    raise
                raise ValueError(f"Línea {instruccion[1]}: {error}") from None

    def ejecutar_instruccion(self, instruccion):
        self.pasos += 1
        if self.pasos > 10000:
            raise ValueError("El programa superó el límite de 10000 instrucciones ejecutadas.")
        tipo = instruccion[0]

        if tipo == "asignar":
            nombre, expresion = instruccion[2:]
            valor = self.evaluar(expresion)
            if nombre in ("agua", "energia") and valor < 0:
                raise ValueError(f"El recurso '{nombre}' no puede ser negativo.")
            self.variables[nombre] = valor

        elif tipo in ("regar", "iluminar"):
            cantidad = self.evaluar(instruccion[2])
            recurso = "agua" if tipo == "regar" else "energia"
            unidad = "L" if tipo == "regar" else "unidades de energía"
            if cantidad <= 0:
                raise ValueError(f"La cantidad para '{tipo}' debe ser mayor que cero.")
            if cantidad > self.variables[recurso]:
                raise ValueError(f"No hay suficiente {recurso}: se requieren {formato(cantidad)} y quedan {formato(self.variables[recurso])}.")
            self.variables[recurso] -= cantidad
            if tipo == "regar":
                self.riegos += 1
            else:
                self.iluminaciones += 1
            print(f"{tipo.capitalize()}: consumo de {formato(cantidad)} {unidad}.")

        elif tipo == "mostrar":
            print(formato(self.evaluar(instruccion[2])))

        elif tipo == "reporte":
            print("\n>> REPORTE DEL INVERNADERO")
            print(f"Agua disponible: {formato(self.variables['agua'])} L")
            print(f"Energía disponible: {formato(self.variables['energia'])} unidades")
            print(f"Riegos realizados: {self.riegos}")
            print(f"Iluminaciones realizadas: {self.iluminaciones}\n")

        elif tipo == "repetir":
            veces = self.evaluar(instruccion[2])
            if veces < 0 or veces > 1000 or int(veces) != veces:
                raise ValueError("'repetir' requiere un entero entre 0 y 1000.")
            for _ in range(int(veces)):
                self.ejecutar(instruccion[3])

        elif tipo == "si":
            simbolo, izquierda, derecha = instruccion[2]
            cumple = comparar(simbolo, self.evaluar(izquierda), self.evaluar(derecha))
            if cumple:
                self.ejecutar(instruccion[3])
            else:
                self.ejecutar(instruccion[4])
