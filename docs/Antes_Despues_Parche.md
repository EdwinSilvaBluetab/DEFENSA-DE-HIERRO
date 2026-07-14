# El Parche de la Victoria - Antes y Después

## 1. Inyección SQL

**Antes**

```python
query = "SELECT ... WHERE name LIKE '%" + name + "%'"
rows = connection.execute(query).fetchall()
```

**Después**

```python
rows = connection.execute(
    "SELECT ... WHERE name LIKE ?",
    (f"%{name}%",),
).fetchall()
```

La entrada deja de ser parte de la sintaxis SQL y se procesa como un valor.

## 2. Inyección de comandos

**Antes**

```python
subprocess.run("ping -c 1 " + target, shell=True, ...)
```

**Después**

```python
validated_ip = str(ipaddress.ip_address(target))
subprocess.run(["ping", "-c", "1", validated_ip], shell=False, ...)
```

No se invoca un intérprete de comandos y el dato se restringe a una dirección IP válida.

## 3. Path traversal

**Antes**

```python
report_path = Path(app.config["REPORT_DIR"]) / filename
return report_path.read_text()
```

**Después**

```python
base_dir = Path(app.config["REPORT_DIR"]).resolve()
report_path = (base_dir / filename).resolve()
if report_path != base_dir and base_dir not in report_path.parents:
    return jsonify(error="invalid report path"), 400
```

La ruta canónica debe permanecer dentro del directorio autorizado.

## 4. Deserialización insegura

**Antes**

```python
tactics = pickle.loads(request.get_data())
```

**Después**

```python
tactics = request.get_json(silent=True)
validation_error = _validate_tactics(tactics)
```

JSON no instancia clases arbitrarias y el esquema aceptado es explícito.

## 5. XSS reflejado

**Antes**

```python
return make_response("<h1>Bienvenido " + fan_name + "</h1>")
```

**Después**

```python
return make_response(f"<h1>Bienvenido {escape(fan_name)}</h1>")
```

Los caracteres especiales se codifican antes de incorporarse al contexto HTML.

## Evidencia funcional

La rama corregida mantiene los cinco casos válidos y añade pruebas negativas. El comando esperado es:

```bash
pytest -q
```

El Pull Request debe mostrar:

- Workflow de pruebas exitoso.
- Workflow CodeQL exitoso.
- Diff entre `main` y `fix/security-hardening`.
- Alertas iniciales de `main` y estado corregido tras el merge o análisis de la rama.
