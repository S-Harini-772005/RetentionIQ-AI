import logging
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from pyparsing import col
import shap
from typing import List, Dict, Any, Optional
from uuid import UUID

logger = logging.getLogger(__name__)

class SHAPExplainabilityEngine:
    """
    Enterprise Explainable AI (XAI) Engine.
    Uses SHAP (SHapley Additive exPlanations) to interpret model predictions
    at both global and individual customer levels.
    """

    def __init__(self, model_path: str = "models/churn_rf_model.pkl"):
        try:
            artifacts = joblib.load(model_path)
            self.model = artifacts["model"]
            self.scaler = artifacts["scaler"]
            self.feature_names = artifacts["feature_columns"]
            
            # Initialize SHAP TreeExplainer for Random Forest
            self.explainer = shap.TreeExplainer(self.model)
            logger.info("SHAP TreeExplainer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize SHAP engine: {str(e)}")
            raise RuntimeError("SHAP Engine initialization failure.")

    def get_global_importance(self, feature_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculates global feature importance based on mean absolute SHAP values.
        """
        # Feature importances from the model itself are a good proxy, 
        # but SHAP global importance is more consistent.
        X = feature_df[self.feature_names]
        X_scaled = self.scaler.transform(X)
        shap_values = self.explainer.shap_values(X_scaled)
        
        # For binary classification with RandomForest, shap_values[1] is the churn class
        if isinstance(shap_values, list):
            shap_val_array = shap_values[1]
        else:
            shap_val_array = shap_values
        
        importances = np.mean(np.abs(shap_val_array), axis=0)
        global_importance = dict(zip(self.feature_names, importances))
        return dict(sorted(global_importance.items(), key=lambda x: x[1], reverse=True))

    def explain_customers(self, feature_df: pd.DataFrame, customer_ids: List[Any]) -> List[Dict[str, Any]]:
        """
        Generates local explanations for a batch of customers.
        
        Outputs: 
        CustomerID, TopReason1, TopReason2, TopReason3, ExplanationSummary
        """
        # Ensure data is aligned with training features
        X = feature_df
        feature_df = pd.get_dummies(feature_df,drop_first=True)
        for col in self.feature_names:
             if col not in feature_df.columns:
                  feature_df[col] = 0
                  feature_df = feature_df.reindex(
                      columns=self.feature_names,
                      fill_value=0
                      )
                  X_scaled = self.scaler.transform(feature_df)
        
        # Calculate SHAP values for the positive class (Churn)
        # Random Forest in sklearn outputs list of arrays for multi-class [class_0, class_1]
        shap_values = self.explainer.shap_values(X_scaled)
        if isinstance(shap_values, list):
            shap_val_array = shap_values[1]
        elif len(shap_values.shape) == 3: # New SHAP format: (samples, features, classes)
            shap_val_array = shap_values[:, :, 1]
        else:
            shap_val_array = shap_values
        explanations = []
        
        for i in range(len(X)):
            # Get SHAP values for this specific customer
            cust_shap = shap_val_array[i]
            cust_shap = np.ravel(cust_shap)
            
            # Create a series to map feature names to SHAP values
            feature_impact = pd.Series(cust_shap, index=self.feature_names)
            
            # Sort by absolute impact to find top drivers
            top_drivers = feature_impact.reindex(feature_impact.abs().sort_values(ascending=False).index)
            
            # Extract top 3 features (positive values increase churn risk, negative decrease it)
            reasons = []
            for feat, val in top_drivers.items():
                direction = "increasing" if val > 0 else "decreasing"
                reasons.append(f"{feat} is {direction} risk")
                if len(reasons) >= 3:
                    break

            # Padding if less than 3 features
            while len(reasons) < 3:
                reasons.append("N/A")

            # Generate Human-Readable Summary
            summary = self._generate_summary(top_drivers.head(3).to_dict())

            explanations.append({
                "CustomerID": customer_ids[i],
                "TopReason1": reasons[0],
                "TopReason2": reasons[1],
                "TopReason3": reasons[2],
                "ExplanationSummary": summary,
                "RawShapValues": top_drivers.to_dict()
            })

        return explanations

    def _generate_summary(self, top_drivers: Dict[str, float]) -> str:
        """
        Translates SHAP values into a concise business summary.
        """
        primary_feat = list(top_drivers.keys())[0]
        primary_val = list(top_drivers.values())[0]
        
        sentiment = "primary churn driver" if primary_val > 0 else "strongest retention factor"
        
        return f"Prediction driven mostly by {primary_feat.replace('_', ' ')}, which is the {sentiment} for this customer."

    def export_explanation_report(self, explanations: List[Dict[str, Any]], format: str = "csv") -> str:
        """
        Exports the explanation results to a structured report format.
        """
        df = pd.DataFrame(explanations)
        # Remove raw values for the report
        report_df = df.drop(columns=["RawShapValues"], errors="ignore")
        Path("reports").mkdir(exist_ok=True)
        filename = f"reports/churn_explanations_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        if format == "csv":
            report_df.to_csv(filename, index=False)
        elif format == "json":
            report_df.to_json(filename, orient="records")
            
        logger.info(f"Explanation report exported to {filename}")
        return filename