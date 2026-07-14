## Resumen

Mitiga cinco vulnerabilidades detectables con CodeQL en la API Defensa de Hierro sin eliminar sus capacidades funcionales.

## Hallazgos corregidos

- [x] `py/command-line-injection` / CWE-78
- [x] `py/unsafe-deserialization` / CWE-502
- [x] `py/sql-injection` / CWE-89
- [x] `py/path-injection` / CWE-22
- [x] `py/reflective-xss` / CWE-79

## Validación

- [ ] `pytest -q` exitoso
- [ ] CodeQL exitoso en el PR
- [ ] Se conservaron casos funcionales válidos
- [ ] Se agregaron pruebas negativas para los cinco hallazgos
- [ ] Se adjuntaron capturas en `evidence/screenshots/`

## Evidencias

- Reporte: `docs/Reporte_del_Arbitro.docx`
- Antes/después: `docs/Antes_Despues_Parche.md`
- Bitácora IA: `docs/Bitacora_de_Prompts.md`
