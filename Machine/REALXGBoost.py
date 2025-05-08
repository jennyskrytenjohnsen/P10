import pandas as pd
import joblib
from sklearn.metrics import (
    brier_score_loss,
    accuracy_score,
    roc_auc_score,
    roc_curve,
    precision_score,
    recall_score,
    f1_score
)
import matplotlib.pyplot as plt

# Load test features and labels
df_data_features = pd.read_csv("TestTrainingSet/test_ids_pre&peri.csv")
df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")

# Merge on 'caseid'
df_merged = df_data_features.merge(df_data_labels, on="caseid")

# Drop 'icu_days' column if it exists
df_merged = df_merged.drop(columns=['icu_days'], errors='ignore')

# Define features (X) and labels (y)
X = df_merged.drop(columns=["icu_days_binary"])
y = df_merged["icu_days_binary"]

# Drop 'caseid' if present
if 'caseid' in X.columns:
    X = X.drop(columns=['caseid'])

# Load the saved model
model = joblib.load('Machine/best_xgboost_model.joblib')

# Predict probabilities and class labels
y_pred_proba = model.predict_proba(X)[:, 1]
y_pred = model.predict(X)

# Evaluation metrics
brier = brier_score_loss(y, y_pred_proba)
accuracy = accuracy_score(y, y_pred)
auc = roc_auc_score(y, y_pred_proba)
precision = precision_score(y, y_pred)
recall = recall_score(y, y_pred)
f1 = f1_score(y, y_pred)

# Print metrics
print(f"Brier score: {brier:.4f}")
print(f"Accuracy: {accuracy:.4f}")
print(f"AUC: {auc:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

# Plot ROC curve
fpr, tpr, _ = roc_curve(y, y_pred_proba)
plt.figure(figsize=(6, 6))
plt.plot(fpr, tpr, label=f'AUC = {auc:.2f}')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend(loc="lower right")
plt.grid(True)
plt.tight_layout()
plt.show()
