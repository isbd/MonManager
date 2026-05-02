import sys
from sqlalchemy import create_engine, insert, MetaData
import json


def seed_species():
    print("Populated species")
    engine = create_engine("postgresql+psycopg2://monuser:monpass@localhost:5432/mondb")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    species_table = metadata.tables["species"]

    with engine.connect() as conn:
        data = read_json("data/species.json")
        for entry in data:
            row = {
                "name": entry.get("name"),
                "description": entry.get("description"),
            }
            if "weight" in entry:
                row["spawn_weight"] = entry["weight"]
            if "spawn_time" in entry:
                row["spawn_time"] = entry["spawn_time"]

            conn.execute(insert(species_table), [row])
        conn.commit()


def read_json(file_location: str):
    with open(file_location) as json_file:
        data = json.load(json_file)
        return data
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python seed.py <command>")
        print("Commands: species")
        sys.exit(1)

    command = sys.argv[1]

    if command == "species":
        seed_species()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
