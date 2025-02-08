import ast
import pandas as pd
import pickle
import re
import argparse
from pathlib import Path
from annoy import AnnoyIndex
from preprocessing import *

import logging


def approx_nearest_neighbor(matrix, file_name, f=150, n_trees=350):
    logging.info("Generating Annoy Index...")
    # creating annoy index
    t = AnnoyIndex(f, "angular")
    for i in range(matrix.shape[0]):
        t.add_item(i, matrix[i])
    t.build(n_trees)
    t.save(f"/data/ann_files/{file_name}")


def create_mappings(df):
    logging.info("Creating mappings...")
    df["artist_name"] = (
        df["artist_name"]
        .astype(str)
        .apply(lambda x: ast.literal_eval(re.sub(r"'\s+'", "', '", x)))
    )
    # build mappings for displaying artist/release on web app
    release_id_to_idx = {
        release_id: idx for idx, release_id in enumerate(df["release_id"])
    }
    idx_to_release_id = {
        idx: release_id for release_id, idx in release_id_to_idx.items()
    }
    release_id_to_title = {
        idx: release_title for idx, release_title in enumerate(df["release_title"])
    }
    release_id_to_artist = {
        idx: " / ".join(artist) for idx, artist in enumerate(df["artist_name"])
    }
    mappings = {
        "release_id_to_idx": release_id_to_idx,
        "idx_to_release_id": idx_to_release_id,
        "idx_to_title": release_id_to_title,
        "idx_to_artist": release_id_to_artist,
    }
    return mappings


def write_mappings(mappings):
    # mounted path
    dirpath = Path("/data/mappings")
    dirpath.mkdir(exist_ok=True)
    for key, value in mappings.items():
        file_dest = dirpath / f"{key}.pkl"
        with open(file_dest, "wb") as fp:
            pickle.dump(value, fp)


def arg_parse():
    parser = argparse.ArgumentParser(
        description="Process feature selection for data transformation."
    )
    parser.add_argument(
        "--features",
        nargs="+",
        type=str,
        help="List of features to include in the processing",
    )
    args = parser.parse_args()
    return args


def main():
    data_path = Path("/data")  # mounted
    df = pd.read_parquet(f"{data_path}/training_data/discogs_dataset.parquet")
    df_cleaned = df.drop_duplicates(
        subset=["release_title", "label_name", "release_year", "catno"], keep="first"
    )
    df_cleaned["n_styles"] = df_cleaned["styles"].apply(len)
    args = arg_parse()

    cols_to_impute = [
        "have",
        "want",
        "avg_rating",
        "ratings",
        "low",
        "median",
        "high",
        "want_to_have_ratio",
    ]
    feature_matrix = process_all_features(
        df=df_cleaned, columns=cols_to_impute, features=args.features
    )
    reduced_features = reduce_dimensionality(feature_matrix=feature_matrix)
    n_components = reduced_features.shape[1]
    write_n_components(n_components=n_components)
    mappings = create_mappings(df_cleaned)
    write_mappings(mappings)
    approx_nearest_neighbor(
        reduced_features, f=n_components, file_name="discogs_rec.ann"
    )


if __name__ == "__main__":
    main()
