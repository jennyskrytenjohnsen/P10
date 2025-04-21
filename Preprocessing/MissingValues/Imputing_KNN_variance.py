# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    precision_recall_curve, average_precision_score
)

# Load csv file with features 
df_data_features = pd.read_csv("df_extracted_features.csv")
df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")

# Extract features and labels
X = df_data_features.drop(columns=["caseid"])  # Drop caseid immediately
y = df_data_labels["icu_days_binary"]

# Variance filter 
# Remove features with very low variance
variance_threshold = 0.05  # You can tune this
feature_variances = X.var()
low_variance_features = feature_variances[feature_variances < variance_threshold].index.tolist()

print(f"Features removed due to low variance (<{variance_threshold}):")
print(low_variance_features)

X = X.drop(columns=low_variance_features)  # Drop low variance features

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
X_train = X[train_mask.values]  # Use filtered X
X_test = X[test_mask.values]
y_train = y[train_mask.values]
y_test = y[test_mask.values]

# Build pipeline: scaling, imputing, then modeling
pipeline = Pipeline([
    ('scaler', StandardScaler()),            # Scaler
    ('imputer', KNNImputer(n_neighbors=15)),  # KNN imputer
    ('model', XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=1,
        min_child_weight=1,
        eval_metric='logloss',
        random_state=42
    ))
])

# Train the model
pipeline.fit(X_train, y_train)

# Predict on test set
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]

# Calculate precision-recall curve
precision, recall, _ = precision_recall_curve(y_test, y_prob)
avg_precision = average_precision_score(y_test, y_prob)

# Check stratification
print("Train set ICU label distribution:")
print(y_train.value_counts(normalize=True))

print("\nTest set ICU label distribution:")
print(y_test.value_counts(normalize=True))

# Evaluate performance
print("\n Performance Metrics:")
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.3f}")
print(f"Precision: {precision_score(y_test, y_pred):.3f}")
print(f"Recall:    {recall_score(y_test, y_pred):.3f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.3f}")
print(f"ROC AUC:   {roc_auc_score(y_test, y_prob):.3f}")
print(f"Average Precision (PR AUC): {avg_precision:.3f}")

# Confusion matrix
print("\n Confusion Matrix:")
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
