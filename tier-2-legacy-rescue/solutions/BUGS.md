# BUGS.md

Los 4 bugs listados abajo fueron reproducidos por mí ejecutando el script
original contra `sample_input.csv` (ver `PROMPT_LOG.md` y
`VERIFICATION_NOTE.md` para el proceso). Cada uno incluye el comando/output
real que lo confirma, no solo una afirmación de la IA.

---

## Bug 1 — El contador `SKIPPED` nunca se incrementa (código muerto + scope)

**Síntoma:** el reporte siempre dice `skipped rows: 0`, incluso cuando hay
filas malformadas que sí se descartan.

**Reproducción:** `sample_input.csv` tiene 9 filas de datos; la última
(`Renata Vega,...,Mobile`) solo tiene 3 columnas y provoca `IndexError` en
`row[3]`. Al correr el script contra ese archivo, `load_engineers` devuelve
8 ingenieros (Renata sí fue descartada), pero el output final reporta
`skipped rows: 0`.

**Causa raíz:** en `load_engineers`, dentro del bloque `except`, la línea
`SKIPPED += 1` está **después** de `continue`, por lo que es código
inalcanzable. Adicionalmente, aunque se reordenara, `SKIPPED` es una
variable global y la función nunca la declara con `global SKIPPED`, así
que Python la trataría como variable local no inicializada y lanzaría
`UnboundLocalError` en el primer error capturado.

**Fix:** eliminar la dependencia de estado global mutable. `load_engineers`
debe devolver tanto la lista de ingenieros válidos como el conteo de
filas omitidas (ej. una tupla o un pequeño objeto de resultado), e
incrementar el contador **antes** del `continue`.

---

## Bug 2 — `count_by_status` pierde registros por comparación exacta de string

**Síntoma:** la suma de los conteos por status no coincide con el total de
ingenieros cargados; algunos ingenieros desaparecen del reporte sin
explicación ni error.

**Reproducción:** con `sample_input.csv`, `load_engineers` carga 8
ingenieros, pero `count_by_status` solo suma 6 entre sus tres categorías.
Los 2 faltantes son Diego Fuentes (`status='Pending'`, con mayúscula) y
Valeria Nunez (`status='in_progress '`, con espacio al final).

**Causa raíz:** `count_by_status` compara `s == 'pending'` /
`s == 'in_progress'` etc. de forma exacta, sin normalizar mayúsculas ni
espacios en blanco. Cualquier variación de formato hace que la fila caiga
por ninguna de las tres ramas del `if/elif` y se pierda silenciosamente.

**Fix:** normalizar `status` (`.strip().lower()`) antes de compararlo, y
considerar registrar/reportar valores de `status` no reconocidos en vez
de descartarlos en silencio.

---

## Bug 3 — `overdue` compara fechas como strings, no como fechas reales

**Síntoma:** un ingeniero con deadline claramente vencido no aparece en la
lista de "overdue engineers".

**Reproducción:** Jorge Salinas tiene `deadline='2026-5-30'` (mes sin cero
a la izquierda) y `status='pending'`. Con `today='2026-07-14'`, la fecha
real (30 de mayo de 2026) sí está vencida, pero
`'2026-5-30' < '2026-07-14'` evalúa a `False` en Python (comparación
lexicográfica de caracteres: `'5' > '0'` en la posición del mes). Se
confirma en el output del script original: Jorge no aparece en
`overdue engineers`, mientras que Luis, Diego y Valeria sí.

**Causa raíz:** las fechas se comparan como strings (`e['deadline'] <
today`) en vez de parsearse a objetos `date` reales. Esto solo funciona
por casualidad cuando todas las fechas están en formato `YYYY-MM-DD` con
ceros a la izquierda de forma consistente.

**Fix:** parsear `deadline` con `datetime.strptime(..., '%Y-%m-%d')` (o
`date.fromisoformat`) antes de comparar, y manejar explícitamente fechas
con formato inválido en vez de dejar que la comparación de string dé un
resultado incorrecto sin avisar.

---

## Bug 4 — Default mutable (`rows=[]`) en `append_row` acumula estado entre llamadas

**Síntoma:** si `load_engineers` se invoca más de una vez en el mismo
proceso (por ejemplo, desde un test suite, un notebook, o si el script se
reutiliza como módulo importado en un servicio), cada llamada devuelve
**más** filas de las que tiene el CSV, arrastrando datos de llamadas
anteriores.

**Reproducción:**
```python
first = load_engineers('sample_input.csv')   # 8 filas
second = load_engineers('sample_input.csv')  # 16 filas (¡duplicado!)
first is second  # True — es literalmente el mismo objeto en memoria
```

**Causa raíz:** `def append_row(row, rows=[])` usa una lista como valor por
defecto. En Python, los defaults se evalúan **una sola vez** al definirse
la función, no en cada llamada, así que todas las invocaciones sin pasar
`rows` explícitamente comparten y mutan la misma lista para siempre.

**Fix:** usar `rows=None` y crear una lista nueva dentro de la función
(`if rows is None: rows = []`), o eliminar el helper por completo y
acumular directamente en `load_engineers` con una lista local.

---

## Nota sobre falsos positivos evitados

Durante el análisis, un asistente de IA sugirió inicialmente que el
nombre de columna `course_status` en el CSV (vs. `status` esperado por el
script) era un bug. Se descartó tras confirmar que el script lee las
columnas **por índice posicional**, no por nombre de header — el header
en sí nunca se usa para mapear campos, solo se salta con `next(reader)`.
No se reporta como bug real.
