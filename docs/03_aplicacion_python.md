# 03 — Aplicación Python (interfaz gráfica)

## Qué

Aplicación con **interfaz gráfica** (CustomTkinter) que conecta a MongoDB `bdautos` y permite:

1. Elegir cualquiera de las 25 consultas en un menú lateral
2. Ver el **código del pipeline** (JSON)
3. Leer una explicación educativa de cómo se construye cada etapa y operador
   (`$match`, `$gte`, `$project`, `$sort`, etc.)
4. Pulsar **Ejecutar consulta** y ver los **datos resultantes** en JSON
5. Consultar un resumen visual con el número de documentos y una tabla rápida
   de los campos devueltos

## Cómo está armada

| Archivo | Rol |
|---------|-----|
| `app/gui.py` | Ventana CustomTkinter (lista + código + resultado) |
| `app/main.py` | Punto de entrada → lanza la GUI |
| `app/queries.py` | Definición de las 25 consultas |
| `app/db.py` | Conexión MongoDB |
| `app/requirements.txt` | `pymongo`, `customtkinter` |
| `docker-compose.yml` | MongoDB 7 con healthcheck y volumen persistente |

### Uso

```bash
cd Proyecto-2a.-Evaluaci-n
/opt/homebrew/bin/python3.12 -m venv .venv
.venv/bin/pip install -r app/requirements.txt
./iniciar.sh
# o: .venv/bin/python app/main.py
```

En macOS usar Python 3.12 de Homebrew + `python-tk@3.12` (el Python del sistema no muestra bien la ventana).

## Por qué GUI

El enunciado pide una aplicación Python que muestre código + resultado. CustomTkinter cumple eso con una ventana simple (sidebar + paneles). El panel verde explica paso a paso las etapas y operadores del pipeline, incluyendo filtros, comparadores, proyecciones, ordenamientos, agrupaciones y cálculos. El resultado se presenta en JSON completo y en un resumen visual con contador y tabla de vista rápida.

MongoDB puede ejecutarse sin instalarlo directamente en macOS mediante Docker Compose:

```bash
docker compose up -d --wait mongodb
```

El script `iniciar.sh` ejecuta este paso automáticamente, sincroniza los datos y después abre la aplicación.
El panel verde explica el pipeline por etapas y el panel lila resume la respuesta
con el número de documentos y una tabla de campos; el panel azul conserva el JSON
completo para revisar el resultado técnico.
