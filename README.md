# Octavos - Reto 2 - Defensa de Hierro

API Flask deliberadamente vulnerable para una práctica controlada de auditoría SAST con GitHub CodeQL.

> **Uso exclusivamente educativo.** No desplegar esta rama en Internet ni reutilizar sus patrones en producción.

## Cinco vulnerabilidades sembradas

1. Inyección de comandos del sistema operativo.
2. Deserialización insegura con `pickle`.
3. Inyección SQL.
4. Path traversal / lectura arbitraria de archivos.
5. Cross-Site Scripting (XSS) reflejado.

La corrección completa está en la rama `fix/security-hardening`.

## Ejecución local

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m src.app
```

## Escaneo

El workflow `.github/workflows/codeql.yml` ejecuta CodeQL con la suite `security-extended` en cada push y Pull Request.
