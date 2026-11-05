# 02 — Las 25 consultas Aggregation

## Qué

Se implementaron las 25 consultas del PDF `BDA_Py1_MongoDB` como pipelines en:

- `app/queries.py` — fuente de verdad (Python / pymongo)
- `scripts/02_consultas.js` — evidencia para mongosh (generado con `scripts/export_consultas_js.py`)

## Cómo

Cada consulta es un dict con `id`, `title`, `description`, `collection` y `pipeline`. La GUI las ejecuta con `collection.aggregate(pipeline)` y muestra el código junto con el resultado.

## Por qué Aggregation Framework

El objetivo del parcial es aplicar Aggregation. Se eligieron operadores según el enunciado:

| Consultas | Operadores clave | Justificación |
|-----------|------------------|---------------|
| 1–4, 6 | `$match`, `$project`, `$sort`, `$or`, `$regex` | Filtros y proyección directos sobre `cars` |
| 5, 22 | `$size`, `$filter` sobre `makers.models` | Catálogo embebido |
| 7–9, 11, 17–18, 20 | `$group`, `$avg`, `$round` | Estadísticas |
| 10 | `$bucket` | Rangos de mpg del enunciado |
| 12 | `$switch` | Categorías Alta/Media/Baja |
| 13–14 | `$lookup` desde `makers` | Incluye ceros / modelos sin autos |
| 15, 21, 24–25 | `$sort`+`$limit` / `$setWindowFields` / `$rank` | Top-N y ranking |
| 16 | `$push` + `$slice` | Top 3 por continente |
| 19 | `$setWindowFields` + `$avg` particionado | Promedio por cilindros |
| 23 | `$facet` | Tres vistas en una sola consulta |

## Detalle por consulta

### 1. Autos 2024+ con ≥ 35 mpg
`$match` year/mpg → `$project` descr/year/mpg → `$sort` mpg desc.

### 2. Europeos 4 cilindros ≥ 250 hp
Usa snapshot `continent.name` / `country.name` embebido (evita lookup).

### 3. Japoneses turbo
Regex `\d+(\.\d+)?t$` sobre `descr` + país japan → `$count`.

### 4. Condición OR
Ligero+rápido **o** 8+ cilindros con ≥ 19 mpg.

### 5. Fabricantes multi-marca
Desde `makers` donde `models.length > 1`.

### 6. model.name ≠ maker.name
`$expr` + `$ne` sobre snapshots embebidos.

### 7–8. Agregados por país / fabricante
`$group` + `$round` a 1 decimal.

### 9. Modelos por continente
`$unwind` de `makers.models` (catálogo completo, no solo autos).

### 10. Buckets de mpg
Boundaries `[0,20,25,30,35,40]` + default `40+`.

### 11. Top 5 makers por mpg (min 8 autos)
`$group` → `$match` numAutos ≥ 8 → `$sort` → `$limit` 5.

### 12. Categoría por continente
`$switch` Alta/Media/Baja → `$group` continente+categoría.

### 13. Conteo desde makers (incluye 0)
`$lookup` cars por `makerId` + `$size`.

### 14. Modelos sin autos
`$unwind` models → `$lookup` → `$match` size 0 (ej. esperado: dacia).

### 15. Top 5 potencia + fullName
Sort horsepower + project `maker.fullName`.

### 16. Top 3 mpg por continente
Sort → group push → `$slice` 3.

### 17. Modelo dominante por maker multi-marca
Doble `$group` + filtro `numModelos > 1` + top por sort.

### 18. % por continente
Group + total + `$round` 2 decimales.

### 19. Superan promedio por cilindros
`$setWindowFields` partitionBy cylinders → diferencia → top 5.

### 20. % con 8+ cilindros por continente
`$cond` + porcentaje 1 decimal.

### 21. hp / 1000 lb
Campo calculado → top 10 + país.

### 22. Modelos ≠ nombre fabricante
`$filter` en array embebido; descarta makers vacíos.

### 23. `$facet`
(a) por continente (b) por cilindros (c) min/max/avg mpg.

### 24. Ranking alemanes
`$match` germany → `$rank` por horsepower → top 5.

### 25. Más eficiente por maker europeo
Match europe → sort mpg → `$group` `$first` por maker.

## Cómo regenerar el .js

```bash
.venv/bin/python scripts/export_consultas_js.py
```
