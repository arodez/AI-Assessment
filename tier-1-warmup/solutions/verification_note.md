# Verification Note

**1. What the AI got wrong (or almost wrong):**
Dado que no se cuenta con la version pro el path base espera solo el nombre de `engineers.csv` pero no sabe que se encuentra en data o en otro folder. 

**2. How I caught it:**
Intente correr el comando manual para hacer validaciones con el csv base y con otros 4 que cree para hacer validaciones del manejo de encoding y edge cases de la solucion y al no poner el path completo no podia encontrar el archivo porque el default no busca en el folder padre.

**3. How I confirmed the final result is correct** (tests run, manual checks, sample data used):
- Corrí `solution.py` contra `engineers.csv` real: los conteos (completed:3, pending:3, in_progress:2, missing:2) suman 10, que coincide con las 10 filas de datos del archivo, y `pending.txt` contiene exactamente los 3 emails con status "pending" verificados a mano contra el CSV original.
- Probe edge cases construidos con otra AI: archivo inexistente (falla con mensaje claro, exit code 1, sin traceback), CSV con solo header (no crashea, reporta "sin filas de datos"), fila con email inválido en estado "pending" (se cuenta en el status pero se excluye correctamente de `pending.txt`, con nota en consola), y un CSV codificado en latin-1 con acentos/ñ más una fila completamente vacía (decodificó correctamente y descartó la fila vacía sin afectar el conteo), entre otros.
- Revisé el contenido de `pending.txt` línea por línea en cada corrida para confirmar que no incluyera emails de otros estados ni emails inválidos.
- No se menciona en el readme pero para este problema se considero que `pending` y `PENDING` son dos estados distintos y por lo tanto no se contaron para `pending.txt`.
