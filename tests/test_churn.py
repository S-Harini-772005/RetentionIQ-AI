import pytest
import pandas as pd
from unittest.mock import MagicMock
from app.ml.churn.predict import ChurnPredictor

@pytest.fixture
def mock_predictor():
    predictor = ChurnPredictor.__new__(ChurnPredictor)
    predictor.model = MagicMock()
    predictor.scaler = MagicMock()
    predictor.feature_columns = ['f1', 'f2']
    return predictor

def test_churn_prediction_logic(mock_predictor):
    # Mock model output: [prob_class_0, prob_class_1]
    mock_predictor.model.predict_proba.return_value = [[0.2, 0.8]]
    mock_predictor.model.predict.return_value = [1]
    mock_predictor.scaler.transform.return_value = [[1, 2]]
    
    test_df = pd.DataFrame([{'f1': 1, 'f2': 2}])
    results = mock_predictor.predict(test_df)
    
    assert len(results) == 1
    assert results[0]["risk_level"] == "High"
    assert results[0]["churn_probability"] == 0.8