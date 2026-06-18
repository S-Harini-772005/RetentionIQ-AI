import pandas as pd
from app.ml.churn.train import ChurnModelTrainer

# Load dataset
df = pd.read_excel("data/processed/customer_summary.xlsx")

print("Dataset shape:", df.shape)
print(df["Churn"].value_counts())

trainer = ChurnModelTrainer()

result = trainer.train(
    df=df,
    target_col="Churn"
)
print(df.dtypes)
print(result)