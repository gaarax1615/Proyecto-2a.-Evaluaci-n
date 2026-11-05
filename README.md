# Proyecto 2a. Evaluación — BDAutos en MongoDB

Universidad Autónoma de Chihuahua · Bases de Datos Avanzado  
Aplicación del **Aggregation Framework** sobre la base **Autos**.

## Requisitos cubiertos

1. Diseño documental con **embedding** y **linking**
2. Migración desde `data/BDAutosU2.sql`
3. **25 consultas** Aggregation
4. **App Python con interfaz gráfica** que muestra código de consulta + resultado
5. Evidencia: scripts, código, docs y PDF en este directorio

Documentación de decisiones (qué / cómo / por qué): carpeta [`docs/`](docs/).

## Estructura

```
Proyecto-2a.-Evaluaci-n/
  data/BDAutosU2.sql
  scripts/migrate.py
  scripts/02_consultas.js
  scripts/export_consultas_js.py
  scripts/generate_report.py
  app/main.py · gui.py · queries.py · db.py · requirements.txt
  docker-compose.yml
  docs/00_bitacora.md … 04_entrega.md
  reporte/reporte_proyecto2a.pdf
  reporte/reporte_proyecto2a.html
  README.md
```

## Requisitos de entorno

- **Python 3.12 de Homebrew** (con Tk): `brew install python@3.12 python-tk@3.12`  
  No uses el Python del sistema (`/usr/bin/python3`): en macOS la ventana Tk no aparece.
- Docker Desktop con soporte para `docker compose`

## Puesta en marcha

```bash
cd Proyecto-2a.-Evaluaci-n
/opt/homebrew/bin/python3.12 -m venv .venv
.venv/bin/pip install -r app/requirements.txt

# Iniciar MongoDB y migrar datos (persistente en un volumen Docker)
docker compose up -d --wait mongodb
.venv/bin/python scripts/migrate.py

# App con interfaz gráfica
# Este script también inicia MongoDB y sincroniza los datos automáticamente.
./iniciar.sh
# o: .venv/bin/python app/main.py

# Consultas en mongosh (opcional)
mongosh scripts/02_consultas.js

# Detener MongoDB (los datos permanecen en el volumen)
docker compose down

# Eliminar también los datos persistidos, si se desea empezar de cero
docker compose down -v

# Regenerar reporte HTML/PDF (Mongo debe estar iniciado y migrado)
.venv/bin/python scripts/generate_report.py
```

## Modelo rápido

| Colección | Embedding | Linking |
|-----------|-----------|---------|
| `continents` | — | target |
| `countries` | snapshot continente | `continentId` |
| `makers` | `models[]` + geo | `countryId` |
| `cars` | specs + snapshots | `makerId`, `modelId` |

Detalle: [docs/01_modelo_y_migracion.md](docs/01_modelo_y_migracion.md).
