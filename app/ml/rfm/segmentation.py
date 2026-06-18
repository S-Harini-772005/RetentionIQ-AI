import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class RFMSegmentationEngine:
    """
    Enterprise RFM (Recency, Frequency, Monetary) Segmentation Engine.
    Calculates quintile-based scores and maps customers to predefined business segments.
    """

    def __init__(self):
        # Mapping logic based on R and F scores (Standard RFM Matrix)
        self.segment_map = {
            r'[4-5][4-5]': 'Champions',
            r'[2-5][3-5]': 'Loyal Customers',
            r'[3-5][1-3]': 'Potential Loyalists',
            r'[4-5]1': 'New Customers',
            r'[3-4]1': 'Promising',
            r'[2-3][2-3]': 'Need Attention',
            r'[1-2][2-5]': 'At Risk',
            r'[1-2][1-2]': 'Hibernating',
            r'11': 'Lost Customers'
        }

    def calculate_segments(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Calculates RFM scores and segments.
        Input: DataFrame with [customer_id, recency, frequency, monetary]
        Output: (Scored DataFrame, Segment Statistics)
        """
        if df.empty:
            return pd.DataFrame(), {}

        rfm = df.copy()

        # 1. Calculate Quintiles (1-5)
        # Recency: Lower is better (5 = most recent)
        rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        
        # Frequency: Higher is better
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        
        # Monetary: Higher is better
        rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

        # Convert scores to integers for storage
        rfm['r_score'] = rfm['r_score'].astype(int)
        rfm['f_score'] = rfm['f_score'].astype(int)
        rfm['m_score'] = rfm['m_score'].astype(int)

        # 2. Map to Segments using R and F scores
        rfm['rf_combined'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str)
        
        # Initialize segment column
        rfm['segment_name'] = 'Others'
        for regex, label in self.segment_map.items():
            rfm.loc[rfm['rf_combined'].str.match(regex), 'segment_name'] = label

        # 3. Calculate Global Segment Statistics
        stats = self._calculate_stats(rfm)

        # Drop temporary column
        rfm = rfm.drop(columns=['rf_combined'])
        
        return rfm, stats

    def _calculate_stats(self, rfm: pd.DataFrame) -> Dict[str, Any]:
        """Generates summary statistics for each segment."""
        summary = rfm.groupby('segment_name').agg({
            'customer_id': 'count',
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': ['mean', 'sum']
        }).round(2)

        summary.columns = ['customer_count', 'avg_recency', 'avg_frequency', 'avg_monetary', 'total_revenue']
        
        # Calculate percentages
        total_customers = rfm.shape[0]
        total_revenue = rfm['monetary'].sum()
        
        summary['customer_pct'] = (summary['customer_count'] / total_customers * 100).round(2)
        summary['revenue_pct'] = (summary['total_revenue'] / total_revenue * 100).round(2)
        
        return summary.to_dict(orient='index')

    def prepare_for_postgres(self, rfm_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Converts the DataFrame into a list of dictionaries ready for SQLAlchemy 
        bulk_insert_mappings or PostgreSQL ingestion.
        """
        # Ensure UUIDs/IDs are string formatted if necessary for the schema
        records = rfm_df[[
            'customer_id', 
            'r_score', 
            'f_score', 
            'm_score', 
            'segment_name'
        ]].to_dict(orient='records')
        
        return records

    def get_retention_priority(self, segment_name: str) -> str:
        """Helper to determine business priority based on segment."""
        priorities = {
            'Champions': 'Low (Reward)',
            'Loyal Customers': 'Medium (Upsell)',
            'Potential Loyalists': 'High (Nurture)',
            'New Customers': 'Medium (Onboard)',
            'Promising': 'Medium (Engage)',
            'Need Attention': 'High (Re-engage)',
            'At Risk': 'Critical (Rescue)',
            'Hibernating': 'High (Win-back)',
            'Lost Customers': 'Low (Re-acquire)'
        }
        return priorities.get(segment_name, 'Medium')