# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, average_precision_score
)

# Load csv file with features 
df_data_features = pd.read_csv("df_extracted_features.csv")

# Load csv file with labels
df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")

# Extract features and labels
X = df_data_features.drop(columns=["caseid"])
y = df_data_labels["icu_days_binary"]

# Merge labels with caseid for stratified splitting
df_labels = df_data_labels.copy()
df_labels["caseid"] = df_data_features["caseid"]
case_labels = df_labels[["caseid", "icu_days_binary"]].drop_duplicates()

# Stratified split based on ICU label at case level
train_ids, test_ids = train_test_split(
    case_labels["caseid"],
    test_size=0.2,
    random_state=42,
    stratify=case_labels["icu_days_binary"]
)

# Create boolean masks to filter rows by case ID
train_mask = df_data_features["caseid"].isin(train_ids)
test_mask = df_data_features["caseid"].isin(test_ids)

# Apply masks to select features and targets
X_train = X[train_mask]
X_test = X[test_mask]
y_train = y[train_mask]
y_test = y[test_mask]

# Train initial model to get feature importances
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

model.fit(X_train, y_train)

# Get feature importances
feature_importances = model.feature_importances_
feature_importance_df = pd.DataFrame({
    'feature': X_train.columns,
    'importance': feature_importances
}).sort_values(by='importance', ascending=False)

print("\nTop features based on XGBoost feature importance:")
print(feature_importance_df.head(20))

# Plot Feature Importance
plt.figure(figsize=(10, 6))
plt.barh(feature_importance_df['feature'].head(20), feature_importance_df['importance'].head(20))
plt.gca().invert_yaxis()
plt.xlabel('Feature Importance')
plt.title('Top 20 Features by XGBoost Importance')
plt.grid(True)
plt.tight_layout()
plt.show()

# Select top N features
n_features_to_select = 20
selected_features = feature_importance_df.head(n_features_to_select)['feature'].tolist()

# Evaluate model with selected features
model_selected = XGBClassifier(
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

model_selected.fit(X_train[selected_features], y_train)
y_pred = model_selected.predict(X_test[selected_features])
y_prob = model_selected.predict_proba(X_test[selected_features])[:, 1]

print("\nPerformance Metrics with XGBoost feature importance-selected features:")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
print(f"Precision: {precision_score(y_test, y_pred):.3f}")
print(f"Recall: {recall_score(y_test, y_pred):.3f}")
print(f"F1 Score: {f1_score(y_test, y_pred):.3f}")
print(f"ROC AUC: {roc_auc_score(y_test, y_prob):.3f}")
print(f"Average Precision (PR AUC): {average_precision_score(y_test, y_prob):.3f}")

# Plot Precision-Recall Curve
from sklearn.metrics import precision_recall_curve
precision, recall, _ = precision_recall_curve(y_test, y_prob)

plt.figure()
plt.plot(recall, precision, marker='.')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve (XGBoost Feature Importance)')
plt.grid()
plt.tight_layout()
plt.show()
