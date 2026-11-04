"""Comprueba resultados del lenguaje, control de flujo y errores."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import unittest

from gramatica import analizar
from interprete import Invernadero


def ejecutar(codigo):
    invernadero = Invernadero()
    salida = StringIO()
    with redirect_stdout(salida):
        invernadero.ejecutar(analizar(codigo))
    return invernadero, salida.getvalue()


class PruebasTerra(unittest.TestCase):
    def test_demostracion_completa(self):
        archivo = Path(__file__).resolve().parents[1] / "ejemplos" / "invernadero.terra"
        estado, salida = ejecutar(archivo.read_text(encoding="utf-8"))
        self.assertEqual(estado.variables["agua"], 55)
        self.assertEqual(estado.variables["energia"], 50)
        self.assertEqual((estado.riegos, estado.iluminaciones), (3, 3))
        self.assertIn("Día de operación:", salida)
        self.assertIn("Agua disponible: 55 L", salida)

    def test_prioridad_parentesis_y_decimales(self):
        estado, _ = ejecutar("x = 2 + 3 * 4; y = (2 + 3) * 4; z = -5 / 2;")
        self.assertEqual([estado.variables[n] for n in ("x", "y", "z")], [14, 20, -2.5])

    def test_condicion_cambia_entre_vueltas(self):
        estado, salida = ejecutar('agua = 20; repetir 2 { si agua >= 15 { regar 15; } sino { mostrar "Sin agua"; } }')
        self.assertEqual(estado.variables["agua"], 5)
        self.assertEqual(estado.riegos, 1)
        self.assertIn("Sin agua", salida)

    def test_rama_no_elegida_no_se_ejecuta(self):
        estado, _ = ejecutar("si 1 == 1 { x = 5; } sino { x = desconocida / 0; }")
        self.assertEqual(estado.variables["x"], 5)

    def test_anidacion_y_cero_repeticiones(self):
        estado, _ = ejecutar("x = 0; repetir 2 { repetir 3 { si x < 6 { x = x + 1; } } } repetir 0 { regar 10; }")
        self.assertEqual(estado.variables["x"], 6)
        self.assertEqual(estado.riegos, 0)

    def test_comparadores(self):
        for condicion in ("2 > 1", "1 < 2", "2 >= 2", "2 <= 2", "2 == 2", "2 != 1"):
            with self.subTest(condicion=condicion):
                estado, _ = ejecutar(f"x = 0; si {condicion} {{ x = 1; }}")
                self.assertEqual(estado.variables["x"], 1)

    def test_recursos_insuficientes_no_se_descuentan(self):
        estado = Invernadero()
        with self.assertRaisesRegex(ValueError, "Línea 2.*suficiente agua"):
            estado.ejecutar(analizar("agua = 10;\nregar 15;"))
        self.assertEqual(estado.variables["agua"], 10)
        self.assertEqual(estado.riegos, 0)

    def test_errores_de_ejecucion(self):
        casos = (
            ("mostrar no_existe;", "no ha sido definida"),
            ("x = 1 / 0;", "dividir entre cero"),
            ("agua = -1;", "no puede ser negativo"),
            ("regar -1;", "mayor que cero"),
            ("iluminar 0;", "mayor que cero"),
            ("repetir 1.5 { reporte; }", "entero"),
            ("repetir -1 { reporte; }", "entero"),
            ("repetir 1001 { reporte; }", "entero"),
        )
        for codigo, mensaje in casos:
            with self.subTest(codigo=codigo), self.assertRaisesRegex(ValueError, mensaje):
                ejecutar(codigo)

    def test_errores_de_lexico_y_sintaxis(self):
        for codigo in ("agua = 20", "repetir 2 { reporte;", "agua = @;", 'mostrar "sin cierre;', "regar ;"):
            with self.subTest(codigo=codigo), self.assertRaises(ValueError):
                analizar(codigo)

    def test_error_de_sintaxis_impide_acciones_previas(self):
        salida = StringIO()
        with redirect_stdout(salida), self.assertRaises(ValueError):
            Invernadero().ejecutar(analizar('mostrar "No debe imprimirse"; regar ;'))
        self.assertEqual(salida.getvalue(), "")

    def test_linea_de_error_en_bloque_interior(self):
        with self.assertRaisesRegex(ValueError, "Línea 3:"):
            ejecutar("repetir 2 {\n si 1 == 1 {\n  mostrar desconocida;\n }\n}")

    def test_programas_independientes(self):
        ejecutar("agua = 50;")
        estado, _ = ejecutar("reporte;")
        self.assertEqual(estado.variables["agua"], 0)


if __name__ == "__main__":
    unittest.main()
