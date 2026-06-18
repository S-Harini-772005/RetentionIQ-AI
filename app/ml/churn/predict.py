import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any

from app.ml.retention.recommendation_engine import (
    RetentionRecommendationEngine
)


class ChurnPredictor:
    """
    Inference Engine for Churn Prediction.
    Loads persisted artifacts and provides probability-based risk assessment.
    """

    def __init__(
        self,
        model_path: str = "models/churn_rf_model.pkl"
    ):
        try:
            artifacts = joblib.load(model_path)

            self.model = artifacts["model"]
            self.scaler = artifacts["scaler"]
            self.feature_columns = artifacts["feature_columns"]

        except Exception as e:
            raise RuntimeError(
                f"Failed to load churn model artifacts: {str(e)}"
            )

    def predict_single(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:

        # Convert input to DataFrame
        df = pd.DataFrame([data])

        # Same preprocessing used during training
        df = pd.get_dummies(df)

        # Add missing columns
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0

        # Keep only model columns
        df = df[self.feature_columns]

        # Predict using existing method
        result = self.predict(df)

        # Revenue At Risk
        revenue = float(data.get("Revenue", 0))
        probability = result[0]["churn_probability"]

        revenue_at_risk = round(
            revenue * probability,
            2
        )

        result[0]["revenue_at_risk"] = revenue_at_risk

        # Retention Recommendation Engine
        retention_engine = RetentionRecommendationEngine()

        temp_df = pd.DataFrame([{
            "customer_id": "temp_customer",
            "churn_probability": probability,
            "clv": revenue,
            "frequency": data.get("Frequency", 0)
        }])

        recommendation = (
            retention_engine
            .generate_recommendations(temp_df)
            .iloc[0]
        )

        result[0]["recommended_action"] = (
            recommendation["RecommendedAction"]
        )

        result[0]["offer"] = (
            recommendation["Offer"]
        )

        result[0]["priority_level"] = (
            recommendation["PriorityLevel"]
        )

        result[0]["expected_revenue_saved"] = float(
            recommendation["ExpectedRevenueSaved"]
        )

        result[0]["retention_cost"] = float(
            recommendation["RetentionCost"]
        )

        result[0]["roi"] = float(
            recommendation["ROI"]
        )

        return result[0]

    def predict(
        self,
        feature_df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """
        Generates churn probabilities and risk levels.
        """

        # Ensure feature order
        X = feature_df[self.feature_columns]

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Predictions
        probabilities = self.model.predict_proba(
            X_scaled
        )[:, 1]

        classes = self.model.predict(
            X_scaled
        )

        results = []

        for i, prob in enumerate(probabilities):

            risk_level = "Low"

            if prob >= 0.9:
                risk_level = "Critical"
            elif prob >= 0.7:
                risk_level = "High"
            elif prob >= 0.4:
                risk_level = "Medium"

            results.append({
                "churn_probability": float(
                    np.round(prob, 4)
                ),
                "is_predicted_churn": bool(
                    classes[i]
                ),
                "risk_level": risk_level
            })

        return results