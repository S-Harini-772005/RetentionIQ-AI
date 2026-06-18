import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Union
from uuid import UUID

logger = logging.getLogger(__name__)

class RetentionRecommendationEngine:
    """
    Enterprise Retention Intelligence Engine.
    Maps churn risk and customer value to prescriptive business actions.
    Calculates financial impact metrics (ROI, Revenue Saved) for retention strategies.
    """

    def __init__(self, currency_symbol: str = "$"):
        self.currency_symbol = currency_symbol
        # Operational costs for retention actions
        self.cost_map = {
            "20% Discount": 50.0,      # Estimated margin impact/cost per high-value customer
            "Loyalty Program": 15.0,   # Operational/Onboarding cost
            "Retention Call": 25.0,    # Staff time cost
            "Win-back Email": 2.0,     # Automation cost
            "Standard Newsletter": 0.5 # Baseline cost
        }

    def generate_recommendations(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Processes customer metrics to generate prescriptive retention actions.
        
        Required Columns:
        - customer_id
        - churn_probability
        - clv (Customer Lifetime Value)
        - frequency
        """
        logger.info("Generating prescriptive retention recommendations...")
        
        results = data.apply(self._apply_prescriptive_rules, axis=1)
        recommendation_df = pd.DataFrame(results.tolist())
        
        # Merge with original identifiers
        final_df = pd.concat([data[['customer_id', 'churn_probability', 'clv']], recommendation_df], axis=1)
        
        logger.info(f"Successfully generated {len(final_df)} recommendations.")
        return final_df

    def _apply_prescriptive_rules(self, row: pd.Series) -> Dict[str, Any]:
        """
        Core logic for assigning retention actions and calculating financial ROI.
        """
        churn_prob = row['churn_probability']
        clv = row['clv']
        freq = row.get('frequency', 0)
        
        # Default values
        action = "Monitor"
        offer = "Standard Newsletter"
        priority = "Low"
        
        # 1. Critical Rule: High Churn & High Value
        if churn_prob > 0.80 and clv > 5000:
            priority = "Critical"
            action = "Aggressive Retention"
            offer = "20% Discount"
            
        # 2. Loyalty Rule: Significant Churn Risk & High Frequency
        elif churn_prob > 0.60 and freq > 5:
            priority = "High"
            action = "Loyalty Engagement"
            offer = "Loyalty Program"
            
        # 3. Medium Risk Rule: Moderate Churn
        elif churn_prob > 0.40:
            priority = "Medium"
            action = "Personal Outreach"
            offer = "Retention Call"
            
        # 4. Low Risk / Win-back
        elif churn_prob > 0.20:
            priority = "Low"
            action = "Re-engagement"
            offer = "Win-back Email"

        # Financial Impact Calculations
        # Expected Revenue Saved = CLV * Probability of Churn (Revenue at risk that we aim to recover)
        # Note: In a production setting, we apply an 'effectiveness_rate' (e.g., 0.15) to Revenue Saved.
        effectiveness_rate = 0.20 # Assume we can stop 20% of predicted churners
        expected_revenue_saved = round(clv * churn_prob * effectiveness_rate, 2)
        
        retention_cost = self.cost_map.get(offer, 5.0)
        
        # ROI = (Net Gain from Investment) / Cost of Investment
        roi = round((expected_revenue_saved - retention_cost) / max(retention_cost, 1), 2)

        return {
            "RecommendedAction": action,
            "Offer": offer,
            "PriorityLevel": priority,
            "ExpectedRevenueSaved": expected_revenue_saved,
            "RetentionCost": retention_cost,
            "ROI": roi
        }

    def get_summary_metrics(self, recommendations: pd.DataFrame) -> Dict[str, Any]:
        """
        Aggregates financial projections for the retention campaign.
        """
        summary = {
            "total_revenue_at_risk": round(recommendations['clv'].sum(), 2),
            "projected_revenue_saved": round(recommendations['ExpectedRevenueSaved'].sum(), 2),
            "total_campaign_cost": round(recommendations['RetentionCost'].sum(), 2),
            "average_campaign_roi": round(recommendations['ROI'].mean(), 2),
            "priority_distribution": recommendations['PriorityLevel'].value_counts().to_dict()
        }
        return summary

    def format_recommendation_for_db(self, rec_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formats a single recommendation for storage in the retention_actions table.
        """
        return {
            "customer_id": rec_row['customer_id'],
            "action_type": rec_row['RecommendedAction'],
            "status": "Pending",
            "offer_details": f"Offer: {rec_row['Offer']} | Expected ROI: {rec_row['ROI']}",
            "priority": rec_row['PriorityLevel']
        }