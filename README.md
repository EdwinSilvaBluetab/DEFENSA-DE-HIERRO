# Octavos - Reto 2 - Defensa de Hierro

Repositorio de evidencia para auditar y corregir una API Flask mediante GitHub CodeQL / GitHub Advanced Security.

## Resultado

Se identificaron y mitigaron cinco vulnerabilidades sin eliminar las capacidades funcionales del componente:

| # | Hallazgo | CWE | CodeQL | Riesgo | Estado |
|---|---|---|---|---|---|
| 1 | Inyección de comandos | CWE-78 | `py/command-line-injection` | Crítica | Mitigada |
| 2 | Deserialización insegura | CWE-502 | `py/unsafe-deserialization` | Crítica | Mitigada |
| 3 | Inyección SQL | CWE-89 | `py/sql-injection` | Alta | Mitigada |
| 4 | Path traversal | CWE-22 | `py/path-injection` | Alta | Mitigada |
| 5 | XSS reflejado | CWE-79 | `py/reflective-xss` | Alta | Mitigada |

## Entregables

- `docs/Reporte_del_Arbitro.docx`: análisis y clasificación OWASP.
- `docs/Tarjeta_Roja_Malas_Practicas.md`: inventario de malas prácticas.
- `docs/Bitacora_de_Prompts.md`: trazabilidad de uso del asistente de IA.
- `docs/Antes_Despues_Parche.md`: evidencia técnica del parche.
- `docs/Guia_Evidencias_y_Entrega.md`: pasos para completar capturas y entrega.
- `evidence/screenshots/README.md`: nombres y contenido esperado de las capturas.

## Flujo recomendado para demostrar el PR

```bash
git checkout main
git push -u origin main
# Esperar a que terminen CodeQL y los tests.

git checkout fix/security-hardening
git push -u origin fix/security-hardening
# Abrir PR desde fix/security-hardening hacia main.
```

En el PR deben verse los tests verdes y el análisis CodeQL sin introducir nuevas alertas.

## Ejecución local

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m src.app
```

## Principios aplicados

- Consultas SQL parametrizadas.
- Ejecución de procesos sin shell y con validación estricta.
- Normalización de rutas y confinamiento al directorio permitido.
- JSON con esquema limitado en lugar de deserialización de objetos arbitrarios.
- Escape contextual de contenido HTML.
- Límite de tamaño del cuerpo y pruebas de regresión de seguridad.
