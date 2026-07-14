# Guía de Evidencias y Entrega

## Recomendación clave

Crea el repositorio como **público** durante la evaluación. Code scanning con CodeQL está disponible en repositorios públicos de GitHub.com; un repositorio privado normalmente requiere GitHub Code Security habilitado por una organización.

## 1. Crear el repositorio vacío

En GitHub crea un repositorio llamado, por ejemplo, `defensa-de-hierro-reto2`.

- Visibilidad: Public.
- No agregar README, `.gitignore` ni licencia desde GitHub.

## 2. Conectar y subir la rama vulnerable

Desde la carpeta descomprimida:

```bash
git remote add origin https://github.com/TU_USUARIO/defensa-de-hierro-reto2.git
git checkout main
git push -u origin main
```

Luego abre **Actions** y espera a que terminen:

- `CodeQL Security Scan`
- `Unit and Security Regression Tests`

## 3. Capturar los hallazgos iniciales

En **Security > Code scanning**, captura la lista y el detalle de cada alerta. Los nombres esperados son:

1. Uncontrolled command line.
2. Deserialization of user-controlled data.
3. SQL query built from user-controlled sources.
4. Uncontrolled data used in path expression.
5. Reflected server-side cross-site scripting.

La cantidad exacta puede variar si una consulta reporta más de una ruta. Para el documento, agrupa duplicados por causa raíz y conserva exactamente cinco hallazgos de trabajo.

## 4. Subir la rama corregida y abrir el PR

```bash
git checkout fix/security-hardening
git push -u origin fix/security-hardening
```

En GitHub selecciona **Compare & pull request** y crea el PR hacia `main`.

Título sugerido:

```text
fix(security): mitigate five CodeQL findings in Iron Defense API
```

## 5. Evidencias mínimas

Guarda las capturas dentro de `evidence/screenshots/` con los nombres indicados en su README. Incluye como mínimo:

- Alertas CodeQL en `main`.
- Detalle de cada uno de los cinco hallazgos.
- PR con archivos cambiados.
- Checks verdes del PR.
- CodeQL en la rama corregida o alertas cerradas después del merge.
- Resultado de `pytest -q`.

## 6. Completar el documento Word

Abre `docs/Reporte_del_Arbitro.docx` y reemplaza los campos `[PEGAR ...]` con:

- URL del repositorio.
- URL del Pull Request.
- Capturas o enlaces de alertas.
- Nombre del equipo y capitán.

## 7. Entrega final

Entrega el enlace del repositorio y, si el formulario permite archivo, adjunta también una copia ZIP sin modificar. No cierres ni borres las alertas antes de tomar las capturas iniciales.
