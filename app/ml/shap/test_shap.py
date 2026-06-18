import pandas as pd
from app.ml.shap.explain import SHAPExplainabilityEngine

df = pd.read_excel(
    "data/processed/customer_summary.xlsx"
)

# Remove target column
X = df.drop(columns=["Churn"])

customer_ids = X["Customer ID"].tolist()

engine = SHAPExplainabilityEngine()

result = engine.explain_customers(
    X.head(5),
    customer_ids[:5]
)

print(result)