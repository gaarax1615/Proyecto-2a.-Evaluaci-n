# Bitácora del Proyecto 2a — BDAutos MongoDB

Índice de avances. Cada entrada resume **qué** se hizo, **cómo** y **por qué**.

| Fecha | Fase | Documento detallado |
|-------|------|---------------------|
| 2026-11-02 | Esqueleto del proyecto y copia del SQL | este archivo |
| 2026-11-02 | Modelo documental + migración | [01_modelo_y_migracion.md](01_modelo_y_migracion.md) |
| 2026-11-02 | 25 consultas Aggregation | [02_consultas.md](02_consultas.md) |
| 2026-11-02 | Aplicación Python | [03_aplicacion_python.md](03_aplicacion_python.md) |
| 2026-11-02 | Entrega / checklist | [04_entrega.md](04_entrega.md) |

---

## 2026-11-02 — Arranque

### Qué
Se creó la estructura del proyecto y se copió `BDAutosU2.sql` a `data/`.

### Cómo
```
Proyecto-2a.-Evaluaci-n/
  data/          # SQL fuente
  scripts/       # migración y consultas mongosh
  app/           # Aplicación Python con GUI
  docs/          # bitácora y decisiones
  reporte/       # PDF final
```

### Por qué
El proyecto reúne datos, scripts, aplicación y evidencia en un mismo repositorio. La bitácora en `.md` documenta decisiones mientras se construye, no solo al final.

---

## 2026-11-02 — Modelo y migración

### Qué
Cuatro colecciones en `bdautos` + `scripts/migrate.py` con verificación de conteos.

### Cómo / por qué
Ver [01_modelo_y_migracion.md](01_modelo_y_migracion.md). MongoDB se ejecuta mediante Docker Compose y se valida `ping` + insert.

---

## 2026-11-02 — Consultas y app

### Qué
25 pipelines en `app/queries.py` y export JS para `mongosh`. La fuente de verdad queda compartida por la GUI y el script JavaScript.

### Cómo / por qué
Ver [02_consultas.md](02_consultas.md) y [03_aplicacion_python.md](03_aplicacion_python.md).

---

## 2026-11-02 — Interfaz gráfica

### Qué
Se reemplazó el menú de terminal por una GUI CustomTkinter (`app/gui.py`).

### Cómo
Lista lateral de las 25 consultas; panel de pipeline; botón Ejecutar; panel de resultados JSON.

### Por qué
El requisito pide aplicación Python con visualización de código + datos; la interfaz gráfica deja eso explícito.

---

## 2026-11-03 — MongoDB reproducible con Docker

### Qué
Se agregó `docker-compose.yml` con MongoDB 7, healthcheck, reinicio automático y volumen persistente.

### Cómo / por qué
`iniciar.sh` levanta el contenedor, espera a que MongoDB responda, sincroniza la migración de forma idempotente y abre la GUI. Así el proyecto no depende de una instalación local de MongoDB.

---

## 2026-11-03 — Reversión de Liquid Glass

### Qué
Se descartaron los rediseños Liquid Glass y se restauró la GUI original (CustomTkinter clara, sidebar oscuro, acento terracota).

### Por qué
Pedido explícito de dejarla como al inicio, antes de esas modificaciones.

---

## 2026-11-03 — Fix ventana invisible en macOS

### Qué
La GUI con `/usr/bin/python3` entraba a `mainloop` pero **no mostraba ventana**.

### Cómo
Se recreó `.venv` con `/opt/homebrew/bin/python3.12` + `python-tk@3.12` (Tk 9.1). Script `iniciar.sh` y activación vía `osascript`.

### Por qué
El Tk del sistema en macOS está deprecado y en la práctica no mapea la ventana; Homebrew sí.

---

## 2026-11-03 — Presentación educativa de resultados

### Qué
Se agregó una explicación visual del pipeline y una presentación enriquecida de
los resultados en la GUI.

### Cómo
El panel verde explica las etapas y operadores (`$match`, `$gte`, `$project`,
`$sort`, `$group`, `$lookup`, entre otros). El resultado se muestra en un panel
JSON azul y un resumen lila con contador, descripción y tabla desplazable de
campos y valores.

### Por qué
La aplicación no solo ejecuta las consultas: también permite explicar
visualmente cómo se construyen y cómo interpretar sus respuestas.

---

## 2026-11-03 — Reporte y cierre

### Qué
HTML + PDF en `reporte/`, README y [04_entrega.md](04_entrega.md) con checklist.

### Cómo
`scripts/generate_report.py` embebe pipelines y resultados; PDF vía Chrome headless sobre el HTML.
