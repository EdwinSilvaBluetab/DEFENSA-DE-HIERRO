# Bitácora de Prompts - Fair Play

Esta bitácora documenta el uso de IA durante la construcción y revisión del reto. Las respuestas fueron verificadas mediante revisión humana, pruebas automatizadas y análisis estático.

## Prompt 1 - Definición del reto

**Prompt real del capitán:**

> Ayúdame con este reto de IA. No tengo repositorio. Debo auditar un componente con GHAS o herramientas equivalentes, trabajar entre 4 y 6 vulnerabilidades, clasificarlas bajo OWASP, corregirlas y entregar reporte, malas prácticas, PR y bitácora de prompts.

**Resultado usado:** diseño de un repositorio nuevo con dos ramas, cinco vulnerabilidades trazables y documentos de entrega.

**Validación humana:** se comprobó que el alcance coincide con las reglas y que no depende de un repositorio previo.

## Prompt 2 - Selección de hallazgos detectables

**Prompt:**

> Diseña una API Flask pequeña con exactamente cinco vulnerabilidades que estén cubiertas por consultas actuales de CodeQL para Python. Incluye los identificadores CodeQL y CWE, evitando alertas obsoletas o inventadas.

**Resultado usado:** `py/command-line-injection`, `py/unsafe-deserialization`, `py/sql-injection`, `py/path-injection` y `py/reflective-xss`.

**Validación humana:** se contrastó cada identificador con la documentación oficial de CodeQL.

## Prompt 3 - Configuración de CodeQL

**Prompt:**

> Genera un workflow mínimo de GitHub Actions para analizar Python con CodeQL, ejecutarlo en main, en la rama de corrección y en Pull Requests, usando la suite security-extended y permisos mínimos.

**Resultado usado:** `.github/workflows/codeql.yml`.

**Validación humana:** revisión de sintaxis YAML, triggers y permisos; el workflow debe confirmarse con una ejecución en GitHub.

## Prompt 4 - Parche para inyección SQL

**Prompt:**

> Refactoriza la búsqueda de jugadores para eliminar la inyección SQL mediante parámetros preparados. Conserva la búsqueda parcial por nombre y limita entradas excesivamente largas.

**Resultado usado:** consulta con `LIKE ?` y valor `%nombre%` enviado por separado.

**Validación humana:** prueba normal y prueba con una cadena similar a una inyección.

## Prompt 5 - Parche para inyección de comandos

**Prompt:**

> Corrige el endpoint de ping sin usar shell. Acepta únicamente direcciones IPv4 o IPv6 válidas, ejecuta el proceso con una lista de argumentos y evita que una entrada inválida alcance subprocess.

**Resultado usado:** `ipaddress.ip_address`, `shell=False` y argumentos separados.

**Validación humana:** mocks de `subprocess.run` verifican que el comando malicioso no se ejecute.

## Prompt 6 - Parche para path traversal

**Prompt:**

> Asegura la lectura de reportes para que el archivo resuelto permanezca dentro del directorio permitido. Diferencia ruta inválida de archivo inexistente y conserva la lectura de reportes válidos.

**Resultado usado:** normalización con `resolve()` y control del árbol de padres.

**Validación humana:** lectura válida y rechazo de `../../test.db`.

## Prompt 7 - Sustitución de pickle

**Prompt:**

> Reemplaza la deserialización de pickle por JSON con validación explícita. Permite solo formaciones conocidas, entre 1 y 23 jugadores y nombres de longitud controlada.

**Resultado usado:** `request.get_json(silent=True)` y función `_validate_tactics`.

**Validación humana:** prueba de importación válida y rechazo de carga binaria.

## Prompt 8 - Parche para XSS

**Prompt:**

> Corrige la respuesta HTML que refleja el nombre del hincha. Conserva el saludo, limita la longitud y usa escape contextual del framework.

**Resultado usado:** `markupsafe.escape`.

**Validación humana:** la respuesta contiene `&lt;script&gt;` y nunca una etiqueta `<script>` activa.

## Prompt 9 - Pruebas de regresión de seguridad

**Prompt:**

> Escribe pruebas pytest que demuestren que la funcionalidad válida se conserva y que cada una de las cinco entradas maliciosas es rechazada o tratada como datos.

**Resultado usado:** `tests/test_app.py` en la rama de corrección.

**Validación humana:** ejecución local y workflow de pruebas en GitHub.

## Prompt 10 - Revisión final anti-alucinación

**Prompt:**

> Revisa el diff completo como auditor de seguridad. Señala controles cosméticos, cambios que rompan funcionalidad, dependencias innecesarias y afirmaciones no demostradas. No des por mitigado un hallazgo sin prueba o análisis estático.

**Resultado usado:** clasificación final, tabla antes/después, criterios de evidencia y campos pendientes para capturas reales.

**Validación humana:** no se afirma que las capturas de GHAS existen antes de ejecutar el repositorio en GitHub.
