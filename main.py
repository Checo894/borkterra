"""Terra: intérprete de un pequeño lenguaje para un invernadero.

Uso: python main.py [archivo.terra]
Sin argumentos ejecuta la demostración incluida.
"""

from pathlib import Path
import sys

from gramatica import analizar
from interprete import Invernadero


# ----- FUNCIONES -----

def main():
    if len(sys.argv) > 2:
        print("Uso: python main.py [archivo.terra]", file=sys.stderr)
        return 1

    if len(sys.argv) == 2:
        archivo = Path(sys.argv[1])
    else:
        carpeta = Path(__file__).resolve().parent
        archivo = carpeta / "ejemplos" / "invernadero.terra"
    try:
        codigo = archivo.read_text(encoding="utf-8-sig")
        instrucciones = analizar(codigo)
        print("TERRA - Simulación de un invernadero")
        print(f"Programa: {archivo.name}\n")
        Invernadero().ejecutar(instrucciones)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


# ----- MAIN -----

if __name__ == "__main__":
    sys.exit(main())
