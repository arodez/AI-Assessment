# ANALYSIS.md

## Qué hace el script

`report_generator.py` lee un CSV de ingenieros y su estado de capacitación
(compliance training) y escribe un reporte de texto plano con:
1. Conteo de ingenieros por estado (`completed`, `pending`, `in_progress`)
2. Número de filas omitidas por datos malformados
3. Lista de emails de ingenieros "overdue" (no completados y con deadline
   pasado respecto a una fecha `today` hardcodeada: `2026-07-14`)

## Entradas / Salidas

- **Input:** CSV con columnas posicionales (por índice, no por nombre de
  header): `row[0]=name`, `row[1]=email`, `row[2]=team`, `row[3]=status`,
  `row[4]=deadline` (formato esperado `YYYY-MM-DD`).
- **Output:** archivo de texto plano (`sys.argv[2]`) con el reporte.
- **CLI:** `python report_generator.py <input.csv> <output.txt>`

## Estructura

- `append_row(row, rows=[])` — helper para acumular filas (usa un
  **default mutable como acumulador**, ver `BUGS.md`).
- `load_engineers(path)` — parsea el CSV fila por fila, ignora filas que
  lancen excepción (ej. `IndexError` por columnas faltantes), y debería
  llevar la cuenta de filas omitidas en la variable global `SKIPPED`.
- `count_by_status(engineers)` — cuenta ingenieros por status exacto
  (comparación de string estricta, sensible a mayúsculas/espacios).
- `overdue(engineers, today=...)` — filtra ingenieros no completados cuyo
  `deadline` sea anterior a `today`, comparando **strings**, no fechas
  reales.
- `main()` — orquesta todo y escribe el reporte a disco.

## Supuestos sobre los datos

- El CSV siempre trae header (se salta con `next(reader)`).
- El orden de columnas es fijo; el nombre del header no se usa (por eso
  `course_status` en el CSV de ejemplo no rompe nada — el script lee por
  posición).
- Se asume `deadline` en formato `YYYY-MM-DD` con ceros a la izquierda;
  el CSV de ejemplo demuestra que esto no siempre se cumple
  (`2026-5-30`).
- Se asume `status` en minúsculas exactas y sin espacios extra; el CSV de
  ejemplo demuestra que esto tampoco siempre se cumple (`Pending`,
  `in_progress `).
