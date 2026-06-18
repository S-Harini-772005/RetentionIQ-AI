import pandas as pd
from app.ml.retention.recommendation_engine import RetentionRecommendationEngine

def test_retention_rules_critical():
    engine = RetentionRecommendationEngine()
    data = pd.DataFrame([{
        "customer_id": "C-001",
        "churn_probability": 0.85,
        "clv": 6000.0,
        "frequency": 10
    }])
    
    recommendations = engine.generate_recommendations(data)
    rec = recommendations.iloc[0]
    
    assert rec["PriorityLevel"] == "Critical"
    assert rec["Offer"] == "20% Discount"
    assert rec["ExpectedRevenueSaved"] > 0

def test_retention_rules_loyalty():
    engine = RetentionRecommendationEngine()
    data = pd.DataFrame([{
        "customer_id": "C-002",
        "churn_probability": 0.65,
        "clv": 1000.0,
        "frequency": 8
    }])
    
    recommendations = engine.generate_recommendations(data)
    rec = recommendations.iloc[0]
    
    assert rec["PriorityLevel"] == "High"
    assert rec["Offer"] == "Loyalty Program"

def test_roi_calculation():
    engine = RetentionRecommendationEngine()
    data = pd.DataFrame([{
        "customer_id": "C-003",
        "churn_probability": 0.5,
        "clv": 2000.0,
        "frequency": 2
    }])
    
    recommendations = engine.generate_recommendations(data)
    rec = recommendations.iloc[0]
    
    # Expected Revenue Saved = 2000 * 0.5 * 0.20 (eff_rate) = 200
    # Cost (Retention Call) = 25
    # ROI = (200 - 25) / 25 = 7.0
    assert rec["ROI"] == 7.0