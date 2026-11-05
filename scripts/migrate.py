#!/usr/bin/env python3
"""
Migra BDAutosU2.sql (modelo relacional) hacia MongoDB bdautos
usando embedding + linking según el diseño del proyecto.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SQL = ROOT / "data" / "BDAutosU2.sql"
DEFAULT_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGODB_DB", "bdautos")

INSERT_RE = re.compile(
    r"INSERT\s+INTO\s+(\w+)\s+VALUES\s*\((.+)\);",
    re.IGNORECASE,
)


def parse_value(raw: str):
    raw = raw.strip()
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1].replace("''", "'")
    if "." in raw:
        return float(raw)
    return int(raw)


def parse_values(payload: str) -> list:
    parts: list[str] = []
    current: list[str] = []
    in_str = False
    for ch in payload:
        if ch == "'" and not in_str:
            in_str = True
            current.append(ch)
        elif ch == "'" and in_str:
            in_str = False
            current.append(ch)
        elif ch == "," and not in_str:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return [parse_value(p) for p in parts]


def load_sql_tables(sql_path: Path) -> dict[str, list[list]]:
    tables: dict[str, list[list]] = {
        "CONTINENTS": [],
        "COUNTRIES": [],
        "CAR_MAKERS": [],
        "MODEL_DETAILS": [],
        "CAR_NAMES": [],
        "CAR_DETAILS": [],
    }
    text = sql_path.read_text(encoding="utf-8")
    for match in INSERT_RE.finditer(text):
        table = match.group(1).upper()
        if table not in tables:
            continue
        tables[table].append(parse_values(match.group(2)))
    return tables


def build_documents(tables: dict[str, list[list]]):
    continents = [
        {"_id": row[0], "contId": row[0], "name": row[1]}
        for row in tables["CONTINENTS"]
    ]
    continent_by_id = {c["_id"]: c for c in continents}

    countries = []
    for row in tables["COUNTRIES"]:
        cont = continent_by_id[row[2]]
        countries.append(
            {
                "_id": row[0],
                "countryId": row[0],
                "name": row[1],
                "continentId": row[2],  # linking
                "continent": {"id": cont["_id"], "name": cont["name"]},  # embedding snapshot
            }
        )
    country_by_id = {c["_id"]: c for c in countries}

    models_by_maker: dict[int, list[dict]] = {}
    model_by_id: dict[int, dict] = {}
    for row in tables["MODEL_DETAILS"]:
        model = {"modelId": row[0], "name": row[2], "makerId": row[1]}
        model_by_id[row[0]] = model
        models_by_maker.setdefault(row[1], []).append(
            {"modelId": row[0], "name": row[2]}
        )

    makers = []
    maker_by_id: dict[int, dict] = {}
    for row in tables["CAR_MAKERS"]:
        country = country_by_id[row[3]]
        doc = {
            "_id": row[0],
            "makerId": row[0],
            "name": row[1],
            "fullName": row[2],
            "countryId": row[3],  # linking
            "country": {
                "id": country["_id"],
                "name": country["name"],
            },
            "continent": {
                "id": country["continent"]["id"],
                "name": country["continent"]["name"],
            },
            "models": models_by_maker.get(row[0], []),  # embedding
        }
        makers.append(doc)
        maker_by_id[row[0]] = doc

    details_by_id = {row[0]: row for row in tables["CAR_DETAILS"]}
    cars = []
    for row in tables["CAR_NAMES"]:
        id_car, model_id, descr = row
        detail = details_by_id[id_car]
        model = model_by_id[model_id]
        maker = maker_by_id[model["makerId"]]
        cars.append(
            {
                "_id": id_car,
                "idCar": id_car,
                "descr": descr,
                "mpg": detail[1],
                "cylinders": detail[2],
                "edispl": detail[3],
                "horsepower": detail[4],
                "weight": detail[5],
                "accel": detail[6],
                "year": detail[7],
                # embedding de catálogos frecuentes en consultas
                "model": {"id": model["modelId"], "name": model["name"]},
                "maker": {
                    "id": maker["makerId"],
                    "name": maker["name"],
                    "fullName": maker["fullName"],
                },
                "country": {
                    "id": maker["country"]["id"],
                    "name": maker["country"]["name"],
                },
                "continent": {
                    "id": maker["continent"]["id"],
                    "name": maker["continent"]["name"],
                },
                # linking explícito
                "modelId": model["modelId"],
                "makerId": maker["makerId"],
            }
        )

    return continents, countries, makers, cars


def migrate(sql_path: Path, uri: str, drop: bool = True) -> dict[str, int]:
    tables = load_sql_tables(sql_path)
    continents, countries, makers, cars = build_documents(tables)

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[DB_NAME]

    documents = {
        "continents": continents,
        "countries": countries,
        "makers": makers,
        "cars": cars,
    }
    for name, items in documents.items():
        collection = db[name]
        if drop:
            collection.drop()
            if items:
                collection.insert_many(items)
        else:
            for item in items:
                collection.replace_one({"_id": item["_id"]}, item, upsert=True)

    db.countries.create_index("continentId")
    db.makers.create_index("countryId")
    db.makers.create_index("models.modelId")
    db.cars.create_index("makerId")
    db.cars.create_index("modelId")
    db.cars.create_index("country.name")
    db.cars.create_index("continent.name")
    db.cars.create_index([("year", 1), ("mpg", 1)])

    counts = {
        "continents": db.continents.count_documents({}),
        "countries": db.countries.count_documents({}),
        "makers": db.makers.count_documents({}),
        "models_embedded": sum(len(m["models"]) for m in db.makers.find({}, {"models": 1})),
        "cars": db.cars.count_documents({}),
    }
    client.close()
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Migrar BDAutosU2.sql a MongoDB")
    parser.add_argument("--sql", type=Path, default=DEFAULT_SQL)
    parser.add_argument("--uri", default=DEFAULT_URI)
    parser.add_argument("--no-drop", action="store_true")
    args = parser.parse_args(argv)

    if not args.sql.exists():
        print(f"No se encontró el SQL: {args.sql}", file=sys.stderr)
        return 1

    try:
        counts = migrate(args.sql, args.uri, drop=not args.no_drop)
    except Exception as exc:  # noqa: BLE001
        print(f"Error de migración: {exc}", file=sys.stderr)
        return 1

    print("Migración completada en base 'bdautos':")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    expected = {
        "continents": 5,
        "countries": 17,
        "makers": 20,
        "models_embedded": 42,
        "cars": 138,
    }
    ok = all(counts[k] == expected[k] for k in expected)
    if not ok:
        print("ADVERTENCIA: conteos distintos a los esperados", expected, file=sys.stderr)
        return 2
    print("Conteos verificados OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
