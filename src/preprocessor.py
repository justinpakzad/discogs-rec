from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from scipy.sparse import hstack, csr_matrix
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.decomposition import TruncatedSVD


class PreProcessor:
    def __init__(self, features=None) -> None:
        # initialize pre-processing transformations
        self.ohe = OneHotEncoder()
        self.mlb = MultiLabelBinarizer()
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(fill_value=0, strategy="constant")
        self.features = features

    def fill_nulls(self, df, columns):
        # Impute missing values with (e.g., ratings,wants,haves,etc)
        df[columns] = self.imputer.fit_transform(df[columns])
        return df

    def transform(self, df):
        features = {
            "year": csr_matrix(self.ohe.fit_transform(df[["release_year"]])),
            # giving less weight to specific feature matrices
            # (e.g., to not only get recs that have the same rating,wants,haves,etc)
            "want_to_have_ratio": csr_matrix(
                self.scaler.fit_transform(df[["want_to_have_ratio"]])
            )
            * 0.4,
            "have": csr_matrix(self.scaler.fit_transform(df[["have"]])) * 0.4,
            "want": csr_matrix(self.scaler.fit_transform(df[["want"]])) * 0.4,
            "avg_ratings": csr_matrix(self.scaler.fit_transform(df[["avg_rating"]]))
            * 0.4,
            "low": csr_matrix(self.scaler.fit_transform(df[["low"]])) * 0.4,
            "median": csr_matrix(self.scaler.fit_transform(df[["median"]])) * 0.4,
            "high": csr_matrix(self.scaler.fit_transform(df[["high"]])) * 0.4,
            "num_ratings": csr_matrix(self.scaler.fit_transform(df[["ratings"]])) * 0.1,
            "video_count": csr_matrix(self.scaler.fit_transform(df[["video_count"]]))
            * 0.1,
            "styles": csr_matrix(self.mlb.fit_transform(df["styles"])),
            "countries": csr_matrix(self.ohe.fit_transform(df[["country"]])) * 0.4,
            "formats": csr_matrix(self.ohe.fit_transform(df[["format"]])),
            "genre": csr_matrix(self.mlb.fit_transform(df["genre"])),
        }
        if self.features is None:
            return features
        selected_features = {k: v for k, v in features.items() if k in self.features}
        return selected_features


class BuildFeatures:
    def __init__(self, features=None, n_components=150) -> None:
        # initialize preprocessor and svd to reduce dimensionality
        self.preprocessor = PreProcessor(features)
        self.svd = TruncatedSVD(n_components=n_components)

    def process_features(self, df, features=None):
        cols_to_impute = [
            "have",
            "want",
            "avg_rating",
            "ratings",
            "low",
            "median",
            "high",
            "ratings",
            "want_to_have_ratio",
        ]
        cleaned_df = self.preprocessor.fill_nulls(
            df,
            (
                [col for col in cols_to_impute if col in features]
                if features
                else cols_to_impute
            ),
        )

        features_dict = self.preprocessor.transform(cleaned_df)
        # horizontally stack feature matrices into a single sparse matrix
        features_stack = hstack([val for val in features_dict.values()])
        return features_stack

    def reduce_dimensionality(self, feature_matrix):
        reduced_features = self.svd.fit_transform(feature_matrix)
        return reduced_features
