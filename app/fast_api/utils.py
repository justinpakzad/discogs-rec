from pathlib import Path
import pickle
import os


def load_mappings():
    mappings_path = Path(__file__).resolve().parents[1] / "mappings"
    mappings = {}

    for full_file_name in os.listdir(mappings_path):
        file_name = full_file_name.split(".")[0]
        with open(f"{mappings_path}/{full_file_name}", "rb") as fp:
            mappings[file_name] = pickle.load(fp)
    return mappings


