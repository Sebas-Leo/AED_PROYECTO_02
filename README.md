# Articulaciones

Proyecto educativo para el curso **CS2023 Algoritmos y Estructuras de Datos (2026-2)** de la **Universidad de Ingeniería y Tecnología (UTEC)**.

Este proyecto implementa y anima un algoritmo de **detección de articulaciones en grafos no dirigidos** mediante una implementación real en **C++17** y una animación programática generada con **Python, Pillow y FFmpeg**.

La animación se alimenta de una traza de ejecución (`trazas.json`) emitida por el programa C++. Los tiempos de descubrimiento, valores `low`, recorridos y marcas de articulación que se muestran corresponden a estados calculados por ese motor.

---

## Integrantes e Información Institucional

| Información | Detalle |
| :--- | :--- |
| **Institución** | Universidad de Ingeniería y Tecnología (UTEC) |
| **Curso** | CS2023 Algoritmos y Estructuras de Datos |
| **Docente** | Prof. Víctor Racsó Galván Oyola (`vgalvan@utec.edu.pe`) |
| **Integrantes** | Huertos Ochoa, Rodrigo Franco • Ramos Vargas, Royer Sebastián • Rosario Palomino, Diego Antonio |
| **Tema** | Articulaciones en grafos no dirigidos |

---

## ¿Qué es una Articulación?

Una **articulación**, también llamada **vértice de corte**, es un vértice cuya eliminación, junto con todas sus aristas incidentes, aumenta el número de componentes conexas de un grafo.

Si `c(G)` representa el número de componentes conexas, el vértice `v` es articulación cuando:

```math
c(G - v) > c(G)
```

Esta definición también funciona cuando el grafo original está desconectado. La detección de articulaciones permite identificar puntos de falla en redes de comunicación y sistemas de conexiones.

### Ejemplo utilizado

El ejemplo principal contiene los triángulos `0-1-2-0` y `3-4-5-3`, unidos mediante la arista `1-3`, y una hoja `6` conectada a `5`.

```text
       0 ----- 1 ----- 3 ----- 4
        \     /        \     /
         \   /          \   /
           2              5 ----- 6
```

El dibujo es esquemático: las aristas exactas están en `implementacion_cpp/examples/principal.txt`. El algoritmo obtiene las articulaciones **1, 3 y 5**. Por ejemplo, eliminar `1` separa `{0,2}` del resto de la red.

---

## Funcionamiento Interno del Algoritmo

Se realiza una **búsqueda en profundidad (DFS)** y se mantiene la siguiente información:

| Campo | Función |
| :--- | :--- |
| `adj[v]` | Lista de vecinos y números de identificación de las aristas. |
| `tin[v]` | Tiempo en que DFS descubre el vértice `v`; `-1` significa no visitado. |
| `low[v]` | Menor tiempo de descubrimiento alcanzable desde su subárbol usando, como máximo, una arista de retorno. |
| `parent[v]` | Padre de `v` en el árbol DFS. |
| `cut[v]` | Indica si `v` fue identificado como articulación. |

### 1. Descubrimiento

Al visitar un vértice por primera vez se asigna un tiempo único y se inicializa:

```text
tin[v] = low[v] = timer++
```

### 2. Arista hacia un vértice ya visitado

Se actualiza el menor tiempo alcanzable con el tiempo de descubrimiento del destino:

```text
low[v] = min(low[v], tin[to])
```

Se ignora únicamente la **arista específica** por la que se llegó desde el padre. Cada arista tiene identificador propio para manejar correctamente las aristas paralelas.

### 3. Regreso desde un hijo DFS

Una vez completado el subárbol del hijo, se propaga su información:

```text
low[v] = min(low[v], low[hijo])
```

Si `v` no es raíz y algún hijo cumple `low[hijo] >= tin[v]`, entonces `v` es articulación. El subárbol del hijo no tiene una salida hacia un ancestro estricto de `v` sin atravesarlo. La igualdad también cuenta: regresar a `v` no permite evitarlo.

### 4. Regla especial de la raíz

La raíz es articulación si tiene **más de un hijo en el árbol DFS**. No basta con contar sus vecinos en el grafo. En el triángulo `0-1-2-0`, la raíz `0` tiene dos vecinos pero un solo hijo DFS y no es articulación.

El ciclo exterior de `run()` inicia una búsqueda en cada componente pendiente para cubrir grafos desconectados.

---

## Arquitectura del Sistema

```text
              IMPLEMENTACIÓN REAL
                        │
      Motor C++17: DFS + tin + low
                        │
                        │ emite eventos JSON
                        ▼
       animacion_python/output/trazas.json
                        │
                        │ leído por Python
                        ▼
          Pillow: dibujo de fotogramas
                        │
                        │ imágenes RGB hacia FFmpeg
                        ▼
         Video MP4 / H.264 / 1920 × 1080
```

Las posiciones, colores y tiempos de las escenas se diseñan en Python. Los pasos del algoritmo y sus resultados provienen del C++. Los efectos de eliminación utilizan un conteo independiente de componentes.

## Estructura del Repositorio

```text
proyecto_02/
├── implementacion_cpp/
│   ├── articulaciones.cpp       # algoritmo propio y serialización de eventos
│   ├── CMakeLists.txt          # compilación para CMake / CLion
│   ├── examples/               # entradas principal, raíz, aislado, desconectado y vacío
│   ├── tests/
│   │   └── test_articulaciones.py
│   └── build/                  # ejecutable del pipeline, generado e ignorado
├── animacion_python/
│   ├── proyecto.py             # compila, genera trazas y renderiza
│   ├── verify_trace.py         # verifica los estados contra el ejecutable
│   ├── agregar_voz.py          # mezcla una pista ya sincronizada
│   ├── config.json             # nombres para los créditos
│   ├── requirements.txt        # Pillow
│   └── output/
│       ├── trazas.json         # registro real generado por C++
│       ├── validacion.txt      # resultado de las pruebas
│       ├── frames/             # capturas generadas, ignoradas
│       └── articulaciones_sin_voz.mp4
├── ejecutar.ps1                # acceso al pipeline desde PowerShell
├── empaquetar.py                # ZIP del código y recursos del video
├── .gitignore
├── .gitattributes
└── README.md
```

---

## Requisitos del Sistema

- **Compilador C++:** g++ o clang++ con soporte C++17 para el pipeline automático.
- **CMake 3.20+ (opcional):** alternativa de compilación, compatible también con MSVC y CLion.
- **Python 3.10+**, con pip.
- **Pillow**, instalado desde `animacion_python/requirements.txt`.
- **FFmpeg** con `libx264`; **ffprobe** para incorporar una grabación.
- **Fuentes:** Segoe UI en Windows o DejaVu Sans en Linux. Si faltan se utiliza la fuente de respaldo de Pillow, con una apariencia diferente.

Los ejecutables del compilador, FFmpeg y ffprobe deben estar disponibles en `PATH`. Comprobarlos con `g++ --version`, `ffmpeg -version` y `ffprobe -version`.

---

## Instrucciones de Compilación y Ejecución

Los comandos siguientes se ejecutan desde la **raíz del repositorio**, salvo indicación expresa.

### 1. Configurar el entorno Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r animacion_python/requirements.txt
```

En Linux, activar con `source .venv/bin/activate`. Si PowerShell no permite activar el entorno, usar `.\.venv\Scripts\python.exe` en lugar de `python`. En Windows, `py -3` también puede sustituir al comando `python` del sistema.

### 2. Compilar el motor y generar las trazas

```powershell
python animacion_python/proyecto.py --prepare
```

Compila `implementacion_cpp/articulaciones.cpp`, ejecuta los cinco ejemplos y guarda los estados en `animacion_python/output/trazas.json`. También genera capturas de las escenas.

### 3. Verificar el algoritmo y las trazas

```powershell
python implementacion_cpp/tests/test_articulaciones.py
python animacion_python/verify_trace.py
```

La primera prueba compara el resultado con un oráculo independiente en **301 grafos** y verifica las cinco trazas. La segunda comprueba que el archivo de estados coincide con una nueva ejecución del C++ y que sus componentes y eliminaciones son correctas.

### 4. Renderizar el video

```powershell
python animacion_python/proyecto.py --video
```

Para recompilar, regenerar trazas y renderizar en una sola ejecución:

```powershell
python animacion_python/proyecto.py --all
```

El render muestra su avance cada 15 segundos de video y puede tardar varios minutos según el equipo. No usa servicios externos ni credenciales.

**Salida:** `animacion_python/output/articulaciones_sin_voz.mp4`.

| Propiedad | Valor |
| :--- | :--- |
| Duración | 180 segundos |
| Resolución | 1920 × 1080 |
| Formato | MP4 / H.264 / yuv420p |
| Fotogramas del archivo | 24 fps |
| Dibujo | 12 imágenes por segundo; FFmpeg duplica cuadros hasta 24 fps |
| Audio base | Sin pista de audio |

Después de cambiar el C++ o los ejemplos, ejecutar `--prepare` o `--all`. `--video` usa el archivo de trazas existente y solo lo genera automáticamente si falta.

### Alternativa: CMake y CLion

```powershell
cmake -S implementacion_cpp -B cmake-build-local
cmake --build cmake-build-local
ctest --test-dir cmake-build-local --output-on-failure
```

CTest necesita el Python con Pillow instalado. Si CMake selecciona otro intérprete, configurar `-DPython3_EXECUTABLE="ruta/al/python"`. En generadores con varias configuraciones, usar `cmake --build cmake-build-local --config Debug` y `ctest --test-dir cmake-build-local -C Debug --output-on-failure`.

Para CLion, abrir `implementacion_cpp` como proyecto CMake y seleccionar el objetivo `articulaciones`. Configurar la redirección de entrada hacia `examples/principal.txt`; agregar `--trace` a los argumentos si se desean eventos JSON. El ejecutable lee de la entrada estándar y escribe en la salida estándar. El comando Python `--prepare` sigue usando g++/clang++ y su propio directorio `implementacion_cpp/build/`.

### Alternativa: ejecutar solo el motor C++

En PowerShell:

```powershell
New-Item -ItemType Directory -Force implementacion_cpp/build
g++ -std=c++17 -O2 -Wall -Wextra -pedantic implementacion_cpp/articulaciones.cpp -o implementacion_cpp/build/articulaciones.exe
Get-Content implementacion_cpp/examples/principal.txt | .\implementacion_cpp\build\articulaciones.exe
Get-Content implementacion_cpp/examples/principal.txt | .\implementacion_cpp\build\articulaciones.exe --trace
```

En Linux:

```bash
mkdir -p implementacion_cpp/build
g++ -std=c++17 -O2 -Wall -Wextra -pedantic implementacion_cpp/articulaciones.cpp -o implementacion_cpp/build/articulaciones
./implementacion_cpp/build/articulaciones < implementacion_cpp/examples/principal.txt
```

En PowerShell también se ofrece `./ejecutar.ps1 -Accion prepare`, `video`, `all` o `test`. Detecta primero el entorno virtual activo, después el runtime local disponible de Codex y finalmente Python/py del sistema. La ejecución directa con Python funciona sin Codex.

---

## Formato de Entrada y de la Traza

La entrada comienza con `n m`, seguida de `m` pares `u v`. Los índices van de **0 a n-1**. Las aristas son no dirigidas.

```text
7 8
0 1
1 2
2 0
1 3
3 4
4 5
5 3
5 6
```

El modo normal imprime `1 3 5`. Si no hay articulaciones, imprime una línea vacía. Se rechazan cantidades negativas, entradas incompletas y extremos fuera de rango.

El modo `--trace` emite un objeto JSON por línea. Por ejemplo, el descubrimiento de `0`:

```json
{
  "kind": "discover",
  "v": 0,
  "to": -1,
  "tin": [0, -1, -1, -1, -1, -1, -1],
  "low": [0, -1, -1, -1, -1, -1, -1],
  "parent": [-1, -1, -1, -1, -1, -1, -1],
  "cut": [0, 0, 0, 0, 0, 0, 0]
}
```

| Evento `kind` | Significado |
| :--- | :--- |
| `discover` | Descubrimiento e inicialización. |
| `tree` | Avance hacia un hijo nuevo. |
| `back` | Procesamiento de una arista hacia un vértice visitado. |
| `return` | Regreso desde el hijo y actualización de `low`. |
| `cut` | Detección de una articulación que no es raíz. |
| `root` | Comprobación de la raíz; `to` representa su cantidad de hijos DFS. |
| `finish` | Finalización del DFS del vértice. |
| `result` | Estado final de las marcas de corte. |

Python reúne los eventos y los datos de cada ejemplo en `trazas.json`, que incluye también las componentes originales y las obtenidas al eliminar cada vértice.

---

## Casos de Prueba

| Entrada | Caso | Articulaciones |
| :--- | :--- | :--- |
| `principal.txt` | Dos triángulos conectados y una hoja. | `1 3 5` |
| `raiz.txt` | Raíz con dos hijos DFS. | `0` |
| `aislado.txt` | Un solo vértice. | Ninguna |
| `desconectado.txt` | Camino, arista separada y vértice aislado. | `1` |
| `vacio.txt` | Cero vértices. | Ninguna |

El oráculo elimina cada vértice y vuelve a contar componentes, sin reutilizar la condición `low`. Se prueban todos los grafos simples de hasta cuatro vértices, 220 casos aleatorios con semilla `2026` y los cinco ejemplos: **301 grafos** en total. Los casos aleatorios también contemplan lazos y aristas paralelas. El registro se guarda en `animacion_python/output/validacion.txt`.

## Análisis de Complejidad Temporal y Espacial

Las cotas del algoritmo se consideran **sin serializar estados ni renderizar fotogramas**.

| Etapa | Complejidad | Justificación |
| :--- | :--- | :--- |
| Recorrido DFS | **O(\|V\| + \|E\|)** | Cada vértice se descubre una vez y cada arista se examina en ambos sentidos. |
| Arreglos y pila DFS | **O(\|V\|)** | Un valor por vértice y una profundidad recursiva de hasta \|V\|. |
| Adyacencia y espacio total | **O(\|V\| + \|E\|)** | Se almacenan vértices y dos entradas por arista. |
| Salida del modo de traza | **O(\|V\|(\|V\| + \|E\|))** | Cada evento serializa arreglos de tamaño \|V\|. |

El render agrega el costo de dibujar y codificar las imágenes. El archivo final tiene 24 fps, pero se dibujan 12 imágenes por segundo y se duplican cuadros durante la codificación.

## Gestión de Memoria y Límites

Los arreglos y las listas de adyacencia usan `std::vector`, cuya memoria se libera automáticamente al destruirse el objeto `Solver`. No se emplean `new` y `delete` explícitos ni una biblioteca que implemente el algoritmo asignado.

El DFS es recursivo y grafos muy profundos pueden agotar la pila. El render utiliza posiciones y selecciones de eventos diseñadas para los ejemplos incluidos: cambiar arbitrariamente el grafo requiere adaptar `graph()` y `paint()`. Cambiar el orden de las aristas puede modificar `tin` y el árbol DFS, aunque no cambia el conjunto de articulaciones.

---

## Escenas y Personalización

| Tiempo | Contenido |
| :--- | :--- |
| 00:00–00:12 | Presentación del problema. |
| 00:12–00:30 | Definición y eliminación de un vértice. |
| 00:30–00:50 | Tiempos `tin` y valores `low`. |
| 00:50–01:10 | Condición para vértices que no son raíz. |
| 01:10–02:05 | Ejecución completa del ejemplo principal. |
| 02:05–02:25 | Raíz con dos hijos y vértice aislado. |
| 02:25–02:43 | Complejidad y utilidad. |
| 02:43–03:00 | Resultado y créditos. |

- Editar `animacion_python/config.json` para cambiar los nombres de los créditos.
- Cambiar entradas en `CASES` y tiempos en `SCENES`, dentro de `proyecto.py`.
- Ajustar colores, fuentes y posiciones en ese mismo archivo.
- La duración de 180 segundos se utiliza también en el render y en `agregar_voz.py`: al cambiarla hay que mantener esos valores coherentes.

### Incorporar una grabación

```powershell
python animacion_python/agregar_voz.py "C:\ruta\voz.wav"
```

Genera `animacion_python/output/articulaciones_con_voz.mp4`. La grabación debe comenzar en 00:00 e incluir sus pausas sincronizadas. El script copia el video sin recodificarlo, convierte el audio a AAC, rellena el silencio final y mantiene los 180 segundos. No alinea frases automáticamente y rechaza una pista de más de 180,1 segundos.

### Empaquetar

```powershell
python empaquetar.py
```

Produce `animacion_python/output/Proyecto_Video_Articulaciones.zip` con las dos carpetas de código, los ejemplos, las pruebas, el README y los videos disponibles. Excluye binarios de compilación, cachés, grabaciones originales y capturas temporales.

## Solución de Problemas

| Problema | Acción |
| :--- | :--- |
| No encuentra el compilador. | Agregar g++ o clang++ al `PATH`. |
| No encuentra Pillow. | Instalar los requisitos con el mismo Python usado para ejecutar. |
| FFmpeg no reconoce libx264. | Comprobar `ffmpeg -encoders` e instalar una distribución compatible. |
| El video usa estados anteriores. | Ejecutar `python animacion_python/proyecto.py --all`. |
| No puede acceder al ejecutable. | Evitar compilar y ejecutar pruebas simultáneamente. |
| Cambia la apariencia de las letras. | Instalar Segoe UI o DejaVu Sans según el sistema. |
| CTest no encuentra Pillow. | Configurar CMake con el intérprete del entorno virtual. |

## Referencias

1. [CP-Algorithms — Finding articulation points](https://cp-algorithms.com/graph/cutpoints.html). Referencia conceptual de DFS, `low` y regla de la raíz.
2. [Documentación de Pillow](https://pillow.readthedocs.io/). Dibujo de fotogramas.
3. [Documentación de FFmpeg](https://ffmpeg.org/documentation.html). Codificación y mezcla de audio.

El código y los visuales se elaboraron para este proyecto con asistencia de IA y se verifican con las pruebas incluidas.
