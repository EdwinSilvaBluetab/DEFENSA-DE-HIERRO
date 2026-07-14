# Tarjeta Roja a las Malas Prácticas

## Inventario

| Mala práctica | Evidencia en `main` | Riesgo | Corrección aplicada |
|---|---|---|---|
| Construir comandos con texto controlado por el usuario | `subprocess.run("ping -c 1 " + target, shell=True)` | Ejecución remota de comandos | Validación con `ipaddress`, lista de argumentos y `shell=False` |
| Concatenar entradas en SQL | Construcción manual de `WHERE name LIKE ...` | Lectura o alteración no autorizada de datos | Placeholder `?` y parámetros separados |
| Confiar en rutas entregadas por el cliente | Unión directa de `REPORT_DIR` con `file` | Acceso a archivos fuera del directorio | `resolve()` y verificación de pertenencia al directorio base |
| Deserializar objetos arbitrarios | `pickle.loads(request.get_data())` | Ejecución de código al reconstruir objetos | JSON y validación explícita de esquema |
| Insertar texto no confiable en HTML | Concatenación directa en la respuesta | Ejecución de scripts en el navegador | Escape con `markupsafe.escape` |
| Ausencia de límites y validación estructural | Cuerpos y cadenas sin tamaño máximo | Abuso de recursos y entradas inesperadas | `MAX_CONTENT_LENGTH`, límites de longitud y allowlists |
| Pruebas enfocadas solo en el camino feliz | No existían casos de abuso | Regresiones de seguridad no detectadas | Pruebas negativas para los cinco hallazgos |

## Criterio de calidad del parche

El parche evita sanitizaciones genéricas o expresiones regulares frágiles. Cada control se coloca en el punto de confianza correspondiente y utiliza mecanismos nativos del lenguaje o del framework.
