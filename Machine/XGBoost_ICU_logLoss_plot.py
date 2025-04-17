# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, roc_curve, confusion_matrix
)

# Load csv file with features 
df_data_features = pd.read_csv("df_so_far_extracted_features.csv")
# print(df_data_features.head())

# Load csv file with labels
df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")
# print(df_data_labels.head())

# Extract features and labels
X = df_data_features
y = df_data_labels["icu_days_binary"]

# Merge labels with caseid for stratified splitting
df_labels = df_data_labels.copy()
df_labels["caseid"] = df_data_features["caseid"]  # ensure caseid is in label dataframe
case_labels = df_labels[["caseid", "icu_days_binary"]].drop_duplicates()

# Stratified split based on ICU label at case level
train_ids, test_ids = train_test_split(
    case_labels["caseid"],
    test_size=0.2,
    random_state=42,
    stratify=case_labels["icu_days_binary"]  # ensures balanced class distribution
)

# Create boolean masks to filter rows by case ID
# Ensures that no patient (caseid) appears in both train and test sets
train_mask = df_data_features["caseid"].isin(train_ids)
test_mask = df_data_features["caseid"].isin(test_ids)

# Apply masks to select features and targets, and drop caseid column from features
X_train = df_data_features[train_mask].drop(columns=["caseid"])
X_test = df_data_features[test_mask].drop(columns=["caseid"])
y_train = y[train_mask]
y_test = y[test_mask]

# Build pipeline with XGBoost (no imputer is included) 
# the pipeline is not used when plotting the logloss
# With tuned hyperparameters:
# - learning rate and n_estimators can improve generalization
# - max_depth limits overfitting
# - subsample and colsample_bytree add randomness for robustness
# - gamma and min_child_weight control complexity of splits
# - eval_metric='logloss' is a common choice for binary classification
# Build model separately (no pipeline) so we can access evals_result_
model = XGBClassifier(
    n_estimators=120,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=1,
    min_child_weight=1,
    eval_metric='logloss',
    random_state=42
)

# Train the model
model.fit(X_train, y_train)
# Predict
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1] 


# Define eval set
eval_set = [(X_train, y_train), (X_test, y_test)]

# Train the model with evaluation set
model.fit(
    X_train,
    y_train,
    eval_set=eval_set,
    verbose=False  # You can set True if you want to see live printing
)

# Access the logloss evolution
results = model.evals_result()

#check stratification in test and train 
print("Train set ICU label distribution:")
print(y_train.value_counts(normalize=True))

print("\nTest set ICU label distribution:")
print(y_test.value_counts(normalize=True))

print("\n Performance Metrics:")
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.3f}")
print(f"Precision: {precision_score(y_test, y_pred):.3f}")
print(f"Recall:    {recall_score(y_test, y_pred):.3f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.3f}")
print(f"ROC AUC:   {roc_auc_score(y_test, y_prob):.3f}")

print("\n Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Plot logloss
plt.figure()
epochs = len(results['validation_0']['logloss'])
x_axis = range(epochs)
plt.plot(x_axis, results['validation_0']['logloss'], label='Train')
plt.plot(x_axis, results['validation_1']['logloss'], label='Test')
plt.xlabel('Iteration')
plt.ylabel('Log Loss')
plt.title('Log Loss Over Training')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
