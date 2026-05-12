import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "svm_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "scaler.pkl")


def load_model():
    return joblib.load(MODEL_PATH)


def load_scaler():
    return joblib.load(SCALER_PATH)