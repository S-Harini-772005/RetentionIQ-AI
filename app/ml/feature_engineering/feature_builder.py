import logging
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import joblib

# Production Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureBuilder:
    """
    Enterprise-grade Feature Engineering Engine for E-Commerce Analytics.
    Calculates RFM, Behavioral, and Trend features for Churn Prediction.
    """
    
    def __init__(self, reference_date: Optional[datetime] = None):
        self.reference_date = reference_date or datetime.now()
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='median')
        self.is_fitted = False
        self.feature_columns: List[str] = [
            'recency', 'frequency', 'monetary', 'aov', 'purchase_gap',
            'tenure', 'product_diversity', 'category_count', 'return_rate',
            'discount_usage', 'revenue_trend', 'order_growth_rate'
        ]

    def validate_input(self, df: pd.DataFrame) -> None:
        """Ensures input DataFrame has required columns."""
        required = {'customer_id', 'order_id', 'order_date', 'amount', 'product_id', 'category', 'discount', 'status'}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def build_features(self, transactions: pd.DataFrame) -> pd.DataFrame:
        """
        Processes raw transactional data into a customer-level feature matrix.
        """
        self.validate_input(transactions)
        df = transactions.copy()
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # Aggregate Base Metrics
        snapshot = self.reference_date
        
        customers = df.groupby('customer_id').agg(
            first_purchase=('order_date', 'min'),
            last_purchase=('order_date', 'max'),
            frequency=('order_id', 'nunique'),
            monetary=('amount', lambda x: x[df['status'] == 'Completed'].sum()),
            refund_count=('status', lambda x: (x == 'Refunded').sum()),
            total_orders=('order_id', 'count'),
            product_diversity=('product_id', 'nunique'),
            category_count=('category', 'nunique'),
            avg_discount=('discount', 'mean')
        ).reset_index()

        # 1. Recency, Tenure, AOV
        customers['recency'] = (snapshot - customers['last_purchase']).dt.days
        customers['tenure'] = (snapshot - customers['first_purchase']).dt.days
        customers['aov'] = customers['monetary'] / customers['frequency'].replace(0, 1)

        # 2. Purchase Gap (Average days between orders)
        def calc_gap(dates):
            if len(dates) < 2: return 0
            return dates.sort_values().diff().dt.days.mean()
        
        gap_df = df.groupby('customer_id')['order_date'].apply(calc_gap).reset_index(name='purchase_gap')
        customers = customers.merge(gap_df, on='customer_id')

        # 3. Behavioral: Return Rate, Discount Usage
        customers['return_rate'] = customers['refund_count'] / customers['total_orders']
        customers['discount_usage'] = customers['avg_discount']

        # 4. Trends: Revenue Trend and Order Growth
        # Logic: Compare last 90 days vs previous 90 days
        limit_date = snapshot - pd.Timedelta(days=90)
        base_date = snapshot - pd.Timedelta(days=180)

        recent_period = df[df['order_date'] >= limit_date]
        prev_period = df[(df['order_date'] < limit_date) & (df['order_date'] >= base_date)]

        recent_metrics = recent_period.groupby('customer_id').agg(
            recent_rev=('amount', 'sum'),
            recent_orders=('order_id', 'nunique')
        )
        prev_metrics = prev_period.groupby('customer_id').agg(
            prev_rev=('amount', 'sum'),
            prev_orders=('order_id', 'nunique')
        )

        trends = recent_metrics.join(prev_metrics, how='outer').fillna(0)
        trends['revenue_trend'] = (trends['recent_rev'] - trends['prev_rev']) / trends['prev_rev'].replace(0, 1)
        trends['order_growth_rate'] = (trends['recent_orders'] - trends['prev_orders']) / trends['prev_orders'].replace(0, 1)
        
        customers = customers.merge(trends[['revenue_trend', 'order_growth_rate']], on='customer_id', how='left')

        # Final column cleanup and missing value handling for trends
        customers[['revenue_trend', 'order_growth_rate']] = customers[['revenue_trend', 'order_growth_rate']].fillna(0)
        
        return customers[['customer_id'] + self.feature_columns]

    def handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Capping outliers using the 1st and 99th percentiles (Winsorization)."""
        df_out = df.copy()
        for col in self.feature_columns:
            lower = df_out[col].quantile(0.01)
            upper = df_out[col].quantile(0.99)
            df_out[col] = np.clip(df_out[col], lower, upper)
        return df_out

    def fit_transform(self, transactions: pd.DataFrame) -> pd.DataFrame:
        """Fits imputer and scaler, then transforms the features."""
        logger.info("Starting feature engineering fit_transform...")
        
        features = self.build_features(transactions)
        X = features[self.feature_columns]
        
        # Outlier handling before scaling
        X = self.handle_outliers(X)
        
        # Impute and Scale
        X_imputed = self.imputer.fit_transform(X)
        X_scaled = self.scaler.fit_transform(X_imputed)
        
        features[self.feature_columns] = X_scaled
        self.is_fitted = True
        return features

    def transform(self, transactions: pd.DataFrame) -> pd.DataFrame:
        """Transforms new data using fitted parameters."""
        if not self.is_fitted:
            raise ValueError("FeatureBuilder must be fitted before transform.")
            
        features = self.build_features(transactions)
        X = features[self.feature_columns]
        X = self.handle_outliers(X)
        X_imputed = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imputed)
        
        features[self.feature_columns] = X_scaled
        return features

    def save(self, path: str) -> None:
        """Persists the scaler and imputer to disk."""
        if not self.is_fitted:
            raise ValueError("Cannot save an unfitted FeatureBuilder.")
        state = {
            'scaler': self.scaler,
            'imputer': self.imputer,
            'reference_date': self.reference_date,
            'feature_columns': self.feature_columns
        }
        joblib.dump(state, path)
        logger.info(f"FeatureBuilder state saved to {path}")

    @classmethod
    def load(cls, path: str) -> 'FeatureBuilder':
        """Loads a persisted FeatureBuilder state."""
        state = joblib.load(path)
        builder = cls(reference_date=state['reference_date'])
        builder.scaler = state['scaler']
        builder.imputer = state['imputer']
        builder.feature_columns = state['feature_columns']
        builder.is_fitted = True
        logger.info(f"FeatureBuilder state loaded from {path}")
        return builder