import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    precision_recall_curve, average_precision_score
)

# Load pre-split train and test sets
df_train = pd.read_csv("TestTrainingSet/train_ids_pre&peri.csv")
df_test = pd.read_csv("TestTrainingSet/test_ids_pre&peri.csv")

# Drop identifiers and extract features/labels
X_train = df_train.drop(columns=["caseid", "icu_days_binary", "subjectid"])
y_train = df_train["icu_days_binary"]

X_test = df_test.drop(columns=["caseid", "icu_days_binary", "subjectid"])
y_test = df_test["icu_days_binary"]

# Build pipeline: Scaling → KNN Imputer → XGBoost Model
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('imputer', KNNImputer(n_neighbors=15)),  # Try tuning k if needed
    ('model', XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.3,
        gamma=0,
        min_child_weight=1,
        eval_metric='logloss',
        random_state=42
    ))
])

# Train the model
pipeline.fit(X_train, y_train)

# Predict
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]

# Evaluate
precision, recall, _ = precision_recall_curve(y_test, y_prob)
avg_precision = average_precision_score(y_test, y_prob)

print("Train set ICU label distribution:")
print(y_train.value_counts(normalize=True))
print("\nTest set ICU label distribution:")
print(y_test.value_counts(normalize=True))

print("\nPerformance Metrics:")
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.3f}")
print(f"Precision: {precision_score(y_test, y_pred):.3f}")
print(f"Recall:    {recall_score(y_test, y_pred):.3f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.3f}")
print(f"ROC AUC:   {roc_auc_score(y_test, y_prob):.3f}")
print(f"Average Precision (PR AUC): {avg_precision:.3f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Plot Precision-Recall curve
plt.figure()
plt.plot(recall, precision, label=f'Avg Precision = {avg_precision:.3f}')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
