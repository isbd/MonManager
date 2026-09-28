import sys
from sqlalchemy import select, create_engine, insert, MetaData
import json


def seed_species(engine):
    print("Populate species")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    species_table = metadata.tables["species"]
    moves_table = metadata.tables["moves"]

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
            if "moves" in entry:
                move_ids = []
                for move_name in entry["moves"]:
                    move = conn.execute(
                        select(moves_table).where(moves_table.c.name == move_name)
                    ).fetchone()
                    move_ids.append(move.id)
                row["starter_moves"] = move_ids
            if "texture" in entry:
                row["texture"] = read_texture(f"data/textures/{entry['texture']}")

            conn.execute(insert(species_table), [row])
        conn.commit()


def seed_moves(engine):
    print("Populate moves")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    moves_table = metadata.tables["moves"]

    with engine.connect() as conn:
        data = read_json("data/moves.json")
        for entry in data:
            row = {
                "name": entry.get("name"),
                "description": entry.get("description"),
            }
            if "power" in entry:
                row["power"] = entry["power"]
            if "accuracy" in entry:
                row["accuracy"] = entry["accuracy"]
            if "speed" in entry:
                row["speed"] = entry["speed"]
            else:
                row["speed"] = 50

            conn.execute(insert(moves_table), [row])
        conn.commit()


def seed_shop(engine):
    print("Populate shops")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    shop_table = metadata.tables["shop_instances"]

    with engine.connect() as conn:
        data = read_json("data/shops.json")
        for entry in data:
            row = {
                "x_coord": entry.get("x_coord"),
                "z_coord": entry.get("z_coord"),
                "radius": entry.get("radius")
            }

            conn.execute(insert(shop_table), [row])
        conn.commit()


def read_texture(texture_location: str):
    try:
        with open(texture_location) as texture_file:
            return texture_file.read().rstrip("\n")
    except OSError:
        return ""


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

    engine = create_engine("postgresql+psycopg2://monuser:monpass@localhost:5432/mondb")

    if command == "species":
        seed_species(engine)
    elif command == "moves":
        seed_moves(engine)
    elif command == "shops":
        seed_shop(engine)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
