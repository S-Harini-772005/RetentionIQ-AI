import logging
import joblib
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    StratifiedKFold
)
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

from app.ml.churn.evaluate import ModelEvaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChurnModelTrainer:
    """
    Enterprise-grade Training Pipeline for Customer Churn Prediction.
    Implements Random Forest with Hyperparameter Optimization and SMOTE.
    """

    def __init__(self, model_path: str = "models/churn_rf_model.pkl"):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.feature_columns: List[str] = []
        self.best_params: Dict[str, Any] = {}

    def train(
        self,
        df: pd.DataFrame,
        target_col: str = "Churn"
    ) -> Dict[str, Any]:
        """
        Executes the full training lifecycle:
        Split -> Scale -> SMOTE -> GridSearch -> Persist
        """

        logger.info("Starting churn model training pipeline...")

        # 1. Prepare Data
        X = df.drop(
            columns=[
                target_col,
                "Customer",
                "Customer ID",
                "LastPurchase",
                "First Purchase Month"
                ],
                errors="ignore"
                )
        # Remove datetime columns
        X = X.select_dtypes(
            exclude=["datetime64[ns]"]
        )

        # One-hot encoding
        X = pd.get_dummies(
            X,
            drop_first=True
        )

        y = df[target_col]

        self.feature_columns = X.columns.tolist()

        # 2. Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            stratify=y,
            random_state=42
        )

        # 3. Feature Scaling
        X_train_scaled = self.scaler.fit_transform(
            X_train
        )

        X_test_scaled = self.scaler.transform(
            X_test
        )

        # 4. Handle Imbalance
        logger.info(
            "Applying SMOTE for class imbalance..."
        )

        smote = SMOTE(random_state=42)

        X_res, y_res = smote.fit_resample(
            X_train_scaled,
            y_train
        )

        # 5. Hyperparameter Optimization
        param_grid = {
            "n_estimators": [100, 200, 300],
            "max_depth": [10, 20,30, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "bootstrap": [True, False],
            "criterion": ["gini", "entropy"],
            "class_weight": [
                "balanced",
                "balanced_subsample",
                None
            ]
        }

        rf = RandomForestClassifier(
            random_state=42
        )

        cv = StratifiedKFold(
            n_splits=5,
            shuffle=True,
            random_state=42
        )

        logger.info(
            "Starting GridSearchCV..."
        )

        grid_search = GridSearchCV(
            estimator=rf,
            param_grid=param_grid,
            cv=cv,
            scoring="f1",
            n_jobs=-1,
            verbose=1
        )

        grid_search.fit(X_res, y_res)

        self.best_params = grid_search.best_params_

        best_model = grid_search.best_estimator_

        # 6. Evaluation
        evaluator = ModelEvaluator()

        metrics = evaluator.calculate_metrics(
            best_model,
            X_test_scaled,
            y_test
        )

        # 7. Save Model
        self._save_artifacts(
            best_model
        )

        return {
            "metrics": metrics,
            "best_params": self.best_params,
            "feature_importance": dict(
                zip(
                    self.feature_columns,
                    best_model.feature_importances_
                )
            )
        }

    def _save_artifacts(self, model):
        """
        Persists model artifacts and metadata to disk.
        Automatically handles directory creation.
        """

        model_file = Path(self.model_path)
        model_dir = model_file.parent

        try:
            # Create directory if missing
            model_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            artifacts = {
                "model": model,
                "scaler": self.scaler,
                "feature_columns": self.feature_columns,
                "metadata": {
                    "trained_at": pd.Timestamp.utcnow().isoformat(),
                    "best_params": self.best_params,
                    "model_version": "1.0.0"
                }
            }

            joblib.dump(
                artifacts,
                model_file
            )

            logger.info(
                f"Model artifacts persisted to {model_file}"
            )

            print(
                f"INFO: Model artifacts persisted to {model_file}"
            )

        except Exception as e:
            logger.error(
                f"Failed to persist model artifacts: {str(e)}"
            )
            raise