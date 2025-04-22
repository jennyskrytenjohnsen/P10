# Import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    precision_recall_curve, average_precision_score
)

# Load data
df_data_features = pd.read_csv("df_extracted_features.csv")
df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")

X = df_data_features
y = df_data_labels["icu_days_binary"]

df_labels = df_data_labels.copy()
df_labels["caseid"] = df_data_features["caseid"]
case_labels = df_labels[["caseid", "icu_days_binary"]].drop_duplicates()

# Stratified split
train_ids, test_ids = train_test_split(
    case_labels["caseid"],
    test_size=0.2,
    random_state=42,
    stratify=case_labels["icu_days_binary"]
)

train_mask = df_data_features["caseid"].isin(train_ids)
test_mask = df_data_features["caseid"].isin(test_ids)

X_train = df_data_features[train_mask].drop(columns=["caseid"])
X_test = df_data_features[test_mask].drop(columns=["caseid"])
y_train = y[train_mask]
y_test = y[test_mask]

# Imputer with ExtraTrees (faster MissForest) uses other features to predict missing values
missforest_imputer = IterativeImputer(
    estimator=ExtraTreesRegressor(
        n_estimators=10,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1 # Use all available cores
    ),
    max_iter=1,
    random_state=42
)

# Fit imputer on train, transform both train and test
missforest_imputer.fit(X_train)
X_train_imputed = missforest_imputer.transform(X_train)
X_test_imputed = missforest_imputer.transform(X_test)

# Train XGBoost
model = XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=1,
    min_child_weight=1,
    eval_metric='logloss',
    random_state=42
)

model.fit(X_train_imputed, y_train)

# Predict
y_pred = model.predict(X_test_imputed)
y_prob = model.predict_proba(X_test_imputed)[:, 1]

# Metrics
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

# Plot PR curve
plt.figure()
plt.plot(recall, precision, label=f'Avg Precision = {avg_precision:.3f}')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()