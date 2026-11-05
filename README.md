# Terra

Tarea 1 de Diseño de Compiladores 

Profesor: Adolfo Centeno Tellez

"Intérprete de un lenguaje pequeño para simular las rutinas de un invernadero."


| Integrante | Matrícula |
| --- | --- |
| Diego Alejandro Espejo López | A01638341 |
| Rodrigo Castellanos Rodríguez | A01643147 |
| Sergio Eduardo Gutiérrez Torres | A01068505 |
| Daniel Esparza Arizpe | A01637076 |

- Docker HUB: https://hub.docker.com/r/checo034/borkterra
- Imagen y versión de entrega: `checo034/borkterra:1.0`

Terra usa Python y PLY (Python Lex-Yacc). Los programas `.terra` contienen las
instrucciones que el intérprete lee y ejecuta. El agua se expresa en litros y la
energía en unidades abstractas de la simulación. 

## Ejecutar en Python

### Windows

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
### Linux/macOS

En Linux/macOS, preparar el entorno con `python3 -m venv .venv` e instalar
con `.venv/bin/python -m pip install -r requirements.txt`. Usar `.venv/bin/python`
en lugar de `.\.venv\Scripts\python.exe` en los comandos anteriores.
Para consultar el código de salida en esas terminales, ejecutar `echo $?`.

## Docker

Requiere únicamente Docker instalado y su motor encendido. En Windows/macOS, iniciar Docker
Desktop; en Windows se usan contenedores Linux. 

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

Son los mismos ejemplos y pruebas: solo cambia el nombre de la imagen; funcionando para Windows, Linux y macOS.

## Resultados Esperados

| Ejemplo | Resultado esperado | Código de salida |
| --- | --- | --- |
| `invernadero.terra` | 55 L de agua, 50 unidades de energía, 3 riegos y 3 iluminaciones | 0 |
| `poca_agua.terra` | Un riego, mensaje de que se omite el segundo, 5 L de agua, 0 unidades de energía | 0 |
| `error_recursos.terra` | `Error: Línea 3: No hay suficiente agua: se requieren 15 y quedan 10.` | 1 (intencional) |

<!--`$LASTEXITCODE` muestra el código del comando recién ejecutado en PowerShell.-->
El tercer ejemplo debe fallar: así se demuestra la validación de recursos.
Estos mismos resultados se esperan al ejecutar los ejemplos en Docker.

## Lenguaje

### Generalidades
- Los nombres distinguen mayúsculas de minúsculas, empiezan por letra sin acento o `_` y pueden contener dígitos.
- Las palabras reservadas se escriben en minúsculas.
- Los mensajes entre comillas sí pueden contener acentos.
- Cada instrucción simple termina con `;`; los bloques terminan con `}`.
- Se admiten números enteros y decimales con punto, operaciones `+ - * /`, negativos y paréntesis.
- Multiplicación y división tienen prioridad sobre suma y resta.
- La división puede producir decimales. Las condiciones admiten `> < >= <= == !=`.
- Las variables guardan números; los textos se permiten en `mostrar`.

### Ejemplo

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

En este ejemplo, `agua` y `energia` son variables especiales, inicialmente en cero, donde su asignación
establece el saldo actual: `agua = 100;` lo establece en 100 y `agua = agua + 20;`
agrega 20; no pueden ser negativas.

Las acciones consumen cantidades positivas y fallan si el recurso es insuficiente.
`repetir` admite de 0 a 1000 vueltas y calcula la cantidad una vez al entrar, donde cada ejecución completa admite hasta 10000 instrucciones para limitar bloques anidados.

## Cómo funciona

1. `lexer.py`: PLY Lex identifica números, nombres, mensajes y palabras reservadas.
2. `gramatica.py`: PLY Yacc reconoce las reglas y construye un árbol de instrucciones
   representado mediante tuplas y listas.
3. `interprete.py`: recorre esas instrucciones, calcula expresiones y actualiza recursos.
4. `main.py`: lee el archivo y comunica los resultados o errores.

Primero se analiza todo el programa y después se ejecuta, si existe un error de sintaxis
impide iniciar la simulación; asimismo, un error durante la ejecución detiene el programa. Los errores terminan con
código de salida 1 y una explicación; el éxito termina con 0.

## Pruebas

Los tres ejemplos anteriores son demostraciones. Además se tienen 12 pruebas
automáticas que verifican cálculos, comparaciones, bloques anidados, ramas que
no deben ejecutarse y errores de léxico, sintaxis y ejecución.

Para ello sigue las siguientes instrucciones desde la carpeta del proyecto, con el entorno preparado:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s pruebas -v
```
(En Linux/macOS, sustituir el ejecutable por `.venv/bin/python`).

El resultado esperado es `Ran 12 tests` y `OK`, con código de salida 0.
Las pruebas que comprueban errores intencionales también deben aparecer como `ok`.

