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
#print(df_data_features.head())

# Load csv file with labels
df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")
#print(df_data_labels.head())

# Extract case IDs for group splitting
case_ids = df_data_features["caseid"].unique()

# Extract features and labels
X = df_data_features
y = df_data_labels["icu_days_binary"]

# Split the unique case IDs into train and test sets
train_ids, test_ids = train_test_split(case_ids, test_size=0.2, random_state=42)

# Create boolean masks to filter rows by case ID
#To ensure that no patient (caseid) is in both train and test sets 
train_mask = df_data_features["caseid"].isin(train_ids)
test_mask = df_data_features["caseid"].isin(test_ids)

# Apply masks to select features and targets
X_train = df_data_features[train_mask].drop(columns=["caseid"])
X_test = df_data_features[test_mask].drop(columns=["caseid"])
y_train = y[train_mask]
y_test = y[test_mask]

# Build pipeline with XGBoost (no imputer is included)
# With hyperparameters
#the learning rate and estimators, can lead to better generalization 
#max depth -> shallow trees = lower risk of overfitting
#subsample and colsample_bytree -> add randomness to the model
#gamma + min_child_weight -> avoid splits that do not improve the model
#logloss, measure how well the model predicits probabilities
# LogLoss = - [ y * log(p) + (1 - y) * log(1 - p) ]
pipeline = Pipeline([
    ('model', XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=1,
        min_child_weight=5,
        eval_metric='logloss',
        random_state=42
    ))
])

# Train the model
pipeline.fit(X_train, y_train)

# Predict on test set
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]  # probability for positive class

# Evaluate performance
print("\n Performance Metrics:")
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.3f}")
print(f"Precision: {precision_score(y_test, y_pred):.3f}")
print(f"Recall:    {recall_score(y_test, y_pred):.3f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.3f}")
print(f"ROC AUC:   {roc_auc_score(y_test, y_prob):.3f}")

# Confusion matrix
print("\n Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Plot ROC curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
plt.figure()
plt.plot(fpr, tpr, label=f'ROC AUC = {roc_auc_score(y_test, y_prob):.3f}')
plt.plot([0, 1], [0, 1], '--', color='gray')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()