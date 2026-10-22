"""Reproducible tests for the simulated model training and inference pipeline."""
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from live_prediction import load_model_bundle, predict_reading
from simulate_transformer_data import FAULT_LABELS, generate_sensor_data
from train_fault_model import prepare_splits, train_model


class PipelineTests(unittest.TestCase):
    def test_simulator_is_reproducible_and_has_all_labels(self):
        first = generate_sensor_data(rows=500, seed=7)
        second = generate_sensor_data(rows=500, seed=7)
        pd.testing.assert_frame_equal(first, second)
        self.assertEqual(set(first["Fault_Status"]), set(FAULT_LABELS))

    def test_split_occurs_before_training_only_upsampling(self):
        data = generate_sensor_data(rows=500, seed=11)
        X_train, y_train, X_test, y_test = prepare_splits(data)
        self.assertEqual(len(X_test), 100)
        self.assertEqual(len(y_test), 100)
        self.assertTrue(set(X_train.index).isdisjoint(set(X_test.index)))
        # The training partition is balanced after the untouched holdout is created.
        self.assertEqual(y_train.value_counts().nunique(), 1)

    def test_model_bundle_inference_preserves_label_mapping(self):
        data = generate_sensor_data(rows=600, seed=42)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.pkl"
            train_model(data, path)
            bundle = load_model_bundle(path)
            code, label = predict_reading(bundle, 415, 75, 40)
        self.assertEqual(bundle["label_mapping"], FAULT_LABELS)
        self.assertEqual(FAULT_LABELS[label], code)


if __name__ == "__main__":
    unittest.main()
