# 01 — Modelo documental y migración

## Qué se hizo

Se diseñó la base MongoDB `bdautos` a partir del SQL relacional `data/BDAutosU2.sql` y se implementó el script `scripts/migrate.py` que:

1. Parsea los `INSERT` del SQL.
2. Construye documentos con **embedding** y **linking**.
3. Inserta (tras `drop` opcional) en cuatro colecciones.
4. Verifica conteos esperados: 5 continentes, 17 países, 20 makers, 42 modelos embebidos, 138 autos.

## Cómo se construyó el modelo

### Colecciones

| Colección | Origen relacional | Técnica |
|-----------|-------------------|---------|
| `continents` | Continents | Documento plano (catálogo) |
| `countries` | Countries | **Linking** `continentId` + snapshot `continent` embebido |
| `makers` | Car_Makers + Model_Details | **Embedding** de `models[]` + **linking** `countryId` + snapshots geo |
| `cars` | Car_Names ⋈ Car_Details (1:1) | Specs embebidas + snapshots `model`/`maker`/`country`/`continent` + **linking** `makerId`/`modelId` |

### Ejemplo `cars`

```js
{
  idCar: 3,
  descr: "chevrolet equinox lt 1.5t",
  mpg: 26, cylinders: 4, horsepower: 175, weight: 3600, accel: 8.5, year: 2025,
  model: { id: 1, name: "chevrolet" },
  maker: { id: 1, name: "gm", fullName: "General Motors" },
  country: { id: 1, name: "usa" },
  continent: { id: 1, name: "america" },
  makerId: 1,
  modelId: 1
}
```

### Ejemplo `makers` (catálogo)

Incluye marcas aunque no tengan autos (necesario para Q13 y Q14). Ejemplo: Renault embebe `renault` y `dacia`.

## Por qué se decidió así

1. El enunciado exige **embedding y linking** juntos; no basta clonar 6 tablas 1:1.
2. Varias consultas (Q13 “desde makers”, Q14 modelos sin autos) necesitan el **catálogo** separado de `cars`.
3. Denormalizar geo/marca en `cars` evita `$lookup` en casi todas las consultas analíticas (Q1–Q12, Q15–Q21, Q23–Q25) y mantiene el código legible.
4. Los ids `makerId`/`modelId`/`continentId` preservan el linking explícito cuando hace falta (`$lookup` en Q13/Q14).

## Cómo ejecutar la migración

```bash
cd Proyecto-2a.-Evaluaci-n
# Iniciar MongoDB reproducible mediante Docker Compose
docker compose up -d --wait mongodb
.venv/bin/python scripts/migrate.py
```

También puede ejecutarse `./iniciar.sh`, que inicia MongoDB y llama a la
migración con `--no-drop` antes de abrir la aplicación. Variables opcionales:
`MONGODB_URI`, `MONGODB_DB`, `--uri`, `--sql` y `--no-drop`.

La migración también crea índices para `makerId`, `modelId`, país, continente,
los filtros de año/rendimiento y las relaciones del catálogo. Con `--no-drop`
los documentos se actualizan mediante `upsert`, por lo que el arranque puede
repetirse sin duplicar información.
