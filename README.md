# Terra

Intérprete de un lenguaje pequeño para simular las rutinas de un invernadero.
Tarea 1 de Diseño de Compiladores. Profesor: Adolfo Centeno Tellez.

| Integrante | Matrícula |
| --- | --- |
| Diego Alejandro Espejo López | A01638341 |
| Rodrigo Castellanos Rodríguez | A01643147 |
| Sergio Eduardo Gutiérrez Torres | A01068505 |
| Daniel Esparza Arizpe | A01637076 |

- Código (repositorio privado): https://github.com/Checo894/borkterra
- Imagen: https://hub.docker.com/r/checo034/borkterra
- Imagen y versión de entrega: `checo034/borkterra:1.0`

Terra usa Python y PLY (Python Lex-Yacc). Los programas `.terra` contienen las
instrucciones que el intérprete lee y ejecuta. El agua se expresa en litros y la
energía en unidades abstractas de la simulación. No controla dispositivos reales.

## Ejecutar en Python

Requiere Python 3.12 o posterior. Los comandos de Windows se ejecutan en
PowerShell, desde la carpeta del proyecto (la que contiene este README).
Preparar el entorno una sola vez:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Ejecutar los tres ejemplos por separado:

```powershell
# Rutina normal de tres días
.\.venv\Scripts\python.exe main.py

# Recurso insuficiente atendido mediante si/sino
.\.venv\Scripts\python.exe main.py ejemplos/poca_agua.terra

# Error intencional por intentar regar sin recursos suficientes
.\.venv\Scripts\python.exe main.py ejemplos/error_recursos.terra
$LASTEXITCODE
```

| Ejemplo | Resultado esperado | Código de salida |
| --- | --- | --- |
| `invernadero.terra` (predeterminado) | 55 L de agua, 50 unidades de energía, 3 riegos y 3 iluminaciones | 0 |
| `poca_agua.terra` | Un riego, mensaje de que se omite el segundo, 5 L de agua, 0 unidades de energía | 0 |
| `error_recursos.terra` | `Error: Línea 3: No hay suficiente agua: se requieren 15 y quedan 10.` | 1 (intencional) |

`$LASTEXITCODE` muestra el código del comando recién ejecutado en PowerShell.
El tercer ejemplo debe fallar: así se demuestra la validación de recursos.
Estos mismos resultados se esperan al ejecutar los ejemplos en Docker.

En Linux/macOS, preparar el entorno con `python3 -m venv .venv` e instalar
con `.venv/bin/python -m pip install -r requirements.txt`. Usar `.venv/bin/python`
en lugar de `.\.venv\Scripts\python.exe` en los comandos anteriores.
Para consultar el código de salida en esas terminales, ejecutar `echo $?`.

## Lenguaje

```text
agua = 100;
energia = 80;
dosis = 10 + 5;

repetir 3 {
    si agua >= dosis {
        regar dosis;
        iluminar 10;
    } sino {
        mostrar "Falta agua";
    }
}
reporte;
```

| Construcción | Significado |
| --- | --- |
| `nombre = expresion;` | Crea o actualiza una variable numérica |
| `regar expresion;` | Descuenta esa cantidad de litros de `agua` |
| `iluminar expresion;` | Descuenta esa cantidad de unidades de `energia` |
| `mostrar expresion;` | Imprime el resultado de un cálculo |
| `mostrar "texto";` | Imprime un mensaje |
| `reporte;` | Muestra los recursos y el número de acciones realizadas |
| `si condicion { ... } sino { ... }` | Ejecuta una de las dos alternativas; `sino` es opcional |
| `repetir expresion { ... }` | Ejecuta un bloque un número entero de veces |
| `# comentario` | Ignora el resto de la línea |

Los nombres distinguen mayúsculas de minúsculas, empiezan por letra sin acento
o `_` y pueden contener dígitos. Las palabras reservadas se escriben en minúsculas.
Los mensajes entre comillas sí pueden contener acentos. Cada instrucción simple
termina con `;`; los bloques terminan con `}`.

Se admiten números enteros y decimales con punto, operaciones `+ - * /`, negativos
y paréntesis. Multiplicación y división tienen prioridad sobre suma y resta.
La división puede producir decimales. Las condiciones admiten `> < >= <= == !=`.
Las variables guardan números; los textos se permiten en `mostrar`.

`agua` y `energia` son variables especiales, inicialmente en cero. Su asignación
establece el saldo actual: `agua = 100;` lo establece en 100 y `agua = agua + 20;`
agrega 20. No pueden ser negativas. Otras variables se deben definir antes de usarlas.
Las acciones consumen cantidades positivas y fallan si el recurso es insuficiente.
`repetir` admite de 0 a 1000 vueltas y calcula la cantidad una vez al entrar.
Cada ejecución completa admite hasta 10000 instrucciones para limitar bloques anidados.

## Cómo funciona

1. `lexer.py`: PLY Lex identifica números, nombres, mensajes y palabras reservadas.
2. `gramatica.py`: PLY Yacc reconoce las reglas y construye un árbol de instrucciones
   representado mediante tuplas y listas.
3. `interprete.py`: recorre esas instrucciones, calcula expresiones y actualiza recursos.
4. `main.py`: lee el archivo y comunica los resultados o errores.

Primero se analiza todo el programa y después se ejecuta. Un error de sintaxis
impide iniciar la simulación. Un error durante la ejecución detiene el programa;
las acciones anteriores ya pueden haberse mostrado. Los errores terminan con
código de salida 1 y una explicación; el éxito termina con 0.

## Pruebas

Los tres ejemplos anteriores son demostraciones. Además hay 12 pruebas
automáticas que verifican cálculos, comparaciones, bloques anidados, ramas que
no deben ejecutarse y errores de léxico, sintaxis y ejecución.
Desde la carpeta del proyecto, con el entorno preparado:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s pruebas -v
```

En Linux/macOS, sustituir el ejecutable por `.venv/bin/python`.
El resultado esperado es `Ran 12 tests` y `OK`, con código de salida 0.
Las pruebas que comprueban errores intencionales también deben aparecer como `ok`.

## Docker

Requiere Docker instalado y su motor encendido. En Windows/macOS, iniciar Docker
Desktop; en Windows usar contenedores Linux. No se necesita instalar Python ni
PLY en la computadora para ejecutar la imagen.

### Construir y probar desde el código fuente

Desde la carpeta del proyecto:

```powershell
docker build -t terra:local .
docker run --rm terra:local
docker run --rm terra:local ejemplos/poca_agua.terra
docker run --rm terra:local ejemplos/error_recursos.terra
```

Los resultados y códigos de salida son los de la tabla anterior. En PowerShell,
consultar `$LASTEXITCODE` inmediatamente después del comando que se quiera comprobar.

Para ejecutar las 12 pruebas automáticas dentro de la imagen:

```powershell
docker run --rm --entrypoint python terra:local -m unittest discover -s pruebas -v
```

Se espera `Ran 12 tests` y `OK`. `--entrypoint python` permite ejecutar las pruebas
en lugar del programa principal. `--rm` elimina el contenedor al terminar;
la imagen permanece disponible para volver a usarla.

La imagen incluye el intérprete, los tres ejemplos y el archivo de pruebas.
La ejecución predeterminada no necesita archivos externos ni interacción.
Si se modifica el código o un ejemplo incluido, repetir `docker build` antes de
volver a probar: la imagen conserva la copia de los archivos de su construcción.

### Descargar y ejecutar desde Docker Hub

Imagen de entrega: [checo034/borkterra:1.0](https://hub.docker.com/r/checo034/borkterra).

No hace falta descargar el repositorio ni estar en la carpeta del proyecto:

```powershell
docker pull checo034/borkterra:1.0
docker run --rm checo034/borkterra:1.0
docker run --rm checo034/borkterra:1.0 ejemplos/poca_agua.terra
docker run --rm checo034/borkterra:1.0 ejemplos/error_recursos.terra
docker run --rm --entrypoint python checo034/borkterra:1.0 -m unittest discover -s pruebas -v
```

Son los mismos ejemplos y pruebas: solo cambia el nombre de la imagen.
Los comandos de Docker anteriores también funcionan en Linux/macOS.
La versión `1.0` incluye Linux AMD64 (Intel/AMD) y ARM64 (por ejemplo, Apple
Silicon con Docker Desktop). Docker selecciona la variante correspondiente.
La imagen de Docker Hub es pública para que el profesor pueda descargarla
sin acceso privado. Eso es independiente del repositorio de código en GitHub,
que la rúbrica pide privado.

### Ejecutar un programa propio (opcional)

En Python, pasar la ruta de un archivo de texto UTF-8 con instrucciones Terra:

```powershell
.\.venv\Scripts\python.exe main.py ejemplos/mi_programa.terra
```

En Docker se puede reconstruir la imagen tras agregarlo a `ejemplos`, o montar
la carpeta local sin reconstruir. Con `mi_programa.terra` dentro de `ejemplos`,
desde la carpeta del proyecto en PowerShell:

```powershell
$ejemplos = (Resolve-Path .\ejemplos).Path
docker run --rm --mount "type=bind,source=$ejemplos,target=/entradas,readonly" terra:local /entradas/mi_programa.terra
```

Para la imagen descargada, sustituir `terra:local` por `checo034/borkterra:1.0`.
En Linux/macOS, desde la carpeta del proyecto:

```sh
docker run --rm --mount "type=bind,source=$(pwd)/ejemplos,target=/entradas,readonly" terra:local /entradas/mi_programa.terra
```

Los archivos externos requieren ese montaje para que Docker pueda leerlos.
Los ejemplos incluidos y las pruebas automáticas no requieren montajes.

Verificado: construcción de `terra:local`, ejecución de los tres ejemplos y
las 12 pruebas dentro de Docker (Python 3.12). El caso de recursos insuficientes
termina con código 1, como se espera. También pasan las pruebas en Python 3.14.
La imagen publicada `checo034/borkterra:1.0` se descargó de Docker Hub: pasan los
tres ejemplos y las 12 pruebas. Las pruebas también pasan en la variante ARM64
ejecutada mediante emulación en Docker Desktop.

El profesor debe tener acceso al repositorio privado para revisar el código.
La imagen pública de Docker Hub puede descargarse independientemente de ese acceso.

## Referencias

- PLY: https://ply.readthedocs.io/en/latest/ply.html
- Ejemplo de clase: https://github.com/adsoftsito/compilers/tree/master/yacc/interpreter

El ejemplo del profesor se utiliza como referencia conceptual. El código de
esta versión está escrito en Python con instrucciones específicas del invernadero.
PLY se instala como dependencia en su versión 3.11; su autor indica que el proyecto
ya no recibirá mantenimiento: https://github.com/dabeaz/ply
