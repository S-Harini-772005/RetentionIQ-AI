import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report
)

class ModelEvaluator:
    """
    Comprehensive Evaluation Suite for Churn Prediction Models.
    """

    def calculate_metrics(self, model: Any, X_test: np.ndarray, y_test: pd.Series) -> Dict[str, Any]:
        """
        Generates standard classification metrics.
        """
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        # Standard Metrics
        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "f1_score": float(f1_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_prob)),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(y_test, y_pred, output_dict=True)
        }

        return metrics