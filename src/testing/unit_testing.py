import unittest
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from preprocessor import PreProcessor


class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = PreProcessor()

    def test_ohe(self):
        df = pd.DataFrame({"country": ["DE", "UK", "US", "UK"]})
        expected = np.array(
            [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
                [0, 1, 0],
            ]
        )
        encoded = self.preprocessor.ohe.fit_transform(df[["country"]]).toarray()
        np.testing.assert_array_equal(encoded, expected)

    def test_imputation(self):
        df = pd.DataFrame({"ratings": [10.0, None, None]})
        expected = np.array([[10.0, 0.0, 0.0]]).reshape(3, 1)
        imputed = self.preprocessor.fill_nulls(df, ["ratings"])
        np.testing.assert_array_equal(imputed, expected)

    def test_mlbinarizer(self):
        df = pd.DataFrame(
            {"styles": [["techno", "house", "electro"], ["tech-house", "techno"]]}
        )
        encoded = self.preprocessor.mlb.fit_transform(df["styles"])
        expected = np.array(
            [
                [1, 1, 0, 1],
                [0, 0, 1, 1],
            ]
        )
        np.testing.assert_array_equal(encoded, expected)

    def test_scaler(self):
        df = pd.DataFrame({"median": [12.99, 25.0, 58.99]})
        scaled = self.preprocessor.scaler.fit_transform(df[["median"]])
        expected = StandardScaler().fit_transform(df[["median"]])
        np.testing.assert_array_equal(scaled, expected)


if __name__ == "__main__":
    unittest.main()
