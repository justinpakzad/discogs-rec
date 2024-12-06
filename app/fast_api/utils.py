from pathlib import Path
import pickle
import os


def load_mappings():
    mappings_path = Path(__file__).resolve().parents[1] / "mappings"
    mappings = {}

    for full_file_name in os.listdir(mappings_path):
        if full_file_name.startswith("."):
            continue
        file_name = full_file_name.split(".")[0]
        with open(f"{mappings_path}/{full_file_name}", "rb") as fp:
            mappings[file_name] = pickle.load(fp)
    return mappings


def get_n_components():
    config_path = Path("/config")
    with open(f"{config_path}/n_components.txt", "r") as f:
        n = int(f.read().strip())
    return n
