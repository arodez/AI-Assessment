# Prompt Log

## Tool & Workflow Note

**Tool used:** Claude (claude.ai, chat interface)
**Mode(s) used:** Chat, con ejecución de código en un contenedor sandbox provisto por la herramienta (permitió correr el script contra el CSV real y contra casos edge antes de entregarlo).
**Notable limitations or surprises:**
- Sin este ida y vuelta de preguntas, la IA por defecto hubiera asumido criterios propios (p. ej. qué hacer con emails inválidos o filas sin `course_status`) que no necesariamente coinciden con lo que el usuario quería — el plan previo evitó tener que rehacer el script después.
- La IA no detectó por sí sola que "Isabel Vargas" tiene una fila más corta (le falta la columna `course_status` por completo, no solo vacía) hasta inspeccionar el CSV en crudo con `cat -A`; una lectura superficial del archivo pudo pasar por alto ese caso.
- Sí ejecutó pruebas reales (no solo generó código y asumió que funcionaba), lo cual permitió detectar que el manejo de encoding funcionaba correctamente en la primera pasada.

---

### Prompt 1
**Mode:** chat
```
Lee el archivo README.md, entiende lo que se solicita como entregable y planea los siguientes pasos

Ignora la instrucción sobre crear el folder llamado solutions,

Vas a producir 3 archivos, solutions.py, prompt_log.md y verification_note.md

Haz las preguntas que necesites para generar el plan completo, no generes el archivo de solución sin primero generar el plan y validarlo conmigo

Cómo se trabajara con un CSV ten en cuenta pruebas de formato, encoding, entre otros. Maneja un estilo de formato de PEP8 para la solución en python
```
**Outcome:** accepted — la IA inspeccionó el CSV real (encoding, filas imperfectas presentes) y devolvió 3 preguntas de clarificación en vez de asumir criterios, tal como se pidió.

### Prompt 2
**Mode:** chat
```
UTF-8 y Latin-1 como fallback (por si hay tildes/ñ mal codificadas)
Ambas: contarla como 'missing' en el conteo Y loguear que fue una fila imperfecta
Validación básica con regex simple (contiene @ y dominio)
```
**Outcome:** accepted — respuestas usadas directamente para fijar las reglas de negocio del plan (encoding fallback, clasificación de status faltante, validación de email).

### Prompt 3
**Mode:** chat
```
el plan se ve bien, prosigue
```
**Outcome:** accepted — se generó `solution.py` siguiendo el plan validado, se probó contra el CSV de muestra y contra 5 casos edge (archivo inexistente, solo header, archivo vacío, email inválido en pending, encoding latin-1 con fila vacía) antes de continuar con la documentación.

### Prompt in GPT-5.5
**Mode:** chat
```
tengo un script en python que hace esto A tool that reads a CSV of engineers (name,email,course_status) and outputs: (a) the count per status, and (b) a list of emails with status "pending", written to pending.txt. Genera otro file csv con alrededor de 100 registros para validar que el script maneja edge cases cómo empty rows, missing columns, email invalido en pending, problemas de encoding etf 8 o latin 1
```
**Outcome:** accepted - se genero `engineers_edge_cases_utf8.csv` y `engineers_edge_cases_latin1.csv` la versión UTF-8 contiene emoji y caracteres chinos. La versión Latin-1 contiene caracteres como ñ, ç, ü y acentos, por lo que permite validar qué ocurre cuando el script intenta abrirla incorrectamente como UTF-8.

### Prompt in GPT-5.5 2
**Mode:** chat
```
que otros problemas comunes suele haber al trabajar con csv y sus codificaciones que no hemos cubierto en los csv de prueba. Si hay faltantes genera otro csv con 30 registros si ya esta cubierto no generes nada 
```
**Outcome:** accepted - se genero `engineers_additional_edge_cases_30_utf8_bom.csv` 