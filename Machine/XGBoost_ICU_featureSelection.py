import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score

# Load csv file with features 
df_data_features = pd.read_csv("df_so_far_extracted_features.csv")

# Load csv file with labels
df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")

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

# Feedforward selection
selected_features = []
remaining_features = list(X_train.columns)
best_score = 0
#the feature selection process depends on the performance matric of roc_auc_score
while remaining_features:
    scores = []
    for feature in remaining_features:
        trial_features = selected_features + [feature]
        model = XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            gamma=1,
            min_child_weight=5,
            eval_metric='logloss',
            random_state=42
        )
        model.fit(X_train[trial_features], y_train)
        y_prob = model.predict_proba(X_test[trial_features])[:, 1]
        score = roc_auc_score(y_test, y_prob) 
        scores.append((score, feature))
    
    scores.sort(reverse=True)  # higher AUC is better
    best_new_score, best_new_feature = scores[0]

    if best_new_score > best_score:
        selected_features.append(best_new_feature)
        remaining_features.remove(best_new_feature)
        best_score = best_new_score
        print(f" Added: {best_new_feature} | AUC: {best_new_score:.3f}")
    else:
        print(" No improvement — stopping.")
        break

# Final selected features
print("\n Final selected features:")
print(selected_features)

# Features that were not selected
not_selected_features = [f for f in X_train.columns if f not in selected_features]
print("\n Features not selected:")
print(not_selected_features)
