from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from scipy.sparse import hstack, csr_matrix
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.decomposition import TruncatedSVD
from pathlib import Path


def scale_features(df):
    scaler = StandardScaler()
    scaled_features = {
        # giving less weight to specific feature matrices
        # (e.g., to not only get recs that have the same rating,wants,haves,etc)
        "want_to_have_ratio": scaler.fit_transform(df[["want_to_have_ratio"]]) * 0.4,
        "have": scaler.fit_transform(df[["have"]]) * 0.4,
        "want": scaler.fit_transform(df[["want"]]) * 0.4,
        "avg_rating": scaler.fit_transform(df[["avg_rating"]]) * 0.4,
        "low": scaler.fit_transform(df[["low"]]) * 0.4,
        "median": scaler.fit_transform(df[["median"]]) * 0.4,
        "high": scaler.fit_transform(df[["high"]]) * 0.4,
        "num_ratings": scaler.fit_transform(df[["ratings"]]) * 0.1,
        "video_count": scaler.fit_transform(df[["video_count"]]) * 0.1,
    }
    return scaled_features


def one_hot_encode_features(df):
    ohe = OneHotEncoder()
    encoded_features = {
        "countries": csr_matrix(ohe.fit_transform(df[["country"]])) * 0.5,
        "year": csr_matrix(ohe.fit_transform(df[["release_year"]])) * 0.8,
    }
    return encoded_features


def ml_encode_features(df):
    mlb = MultiLabelBinarizer()
    encoded_features = {"styles": csr_matrix(mlb.fit_transform(df["styles"]))}
    return encoded_features


def fill_nulls(df, columns):
    imputer = SimpleImputer(fill_value=0, strategy="constant")
    df[columns] = imputer.fit_transform(df[columns])
    return df


def process_all_features(df, columns, features=None):
    imputed_df = fill_nulls(df, columns)
    scaled_features = scale_features(imputed_df)
    ohe_features = one_hot_encode_features(imputed_df)
    multi_label_features = ml_encode_features(imputed_df)
    features_dict = {**scaled_features, **ohe_features, **multi_label_features}
    selected_features = (
        {k: v for k, v in features_dict.items() if k in features}
        if features
        else features_dict
    )
    features_stacked = hstack([val for val in selected_features.values()])
    return features_stacked


def reduce_dimensionality(feature_matrix, n_components=200):
    # make sure default n_components does not exceed the number of features
    # if it does, use the feature matrix shape
    max_components = min(n_components, feature_matrix.shape[1] - 1)
    svd = TruncatedSVD(n_components=max_components)
    reduced_features = svd.fit_transform(feature_matrix)
    return reduced_features


def write_n_components(n_components):
    # write the n_components to a txt file
    # so that the annoy f parameter can be dynamically updated instead of a fixed 150
    config_path = Path("/data/config")
    with open(f"{config_path}/n_components.txt", "w") as f:
        f.write(str(n_components))
