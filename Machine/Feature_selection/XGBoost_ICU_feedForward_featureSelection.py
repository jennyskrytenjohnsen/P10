# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, average_precision_score
)
import warnings
warnings.filterwarnings('ignore')

# Load csv file with features and labels included
df = pd.read_csv("TestTrainingSet/train_ids_pre&peri.csv")

# Extract subject-level labels for stratified splitting
subject_labels = df.groupby("subjectid")["icu_days_binary"].first().reset_index()

# Stratified split based on subject-level ICU label
train_subjects, val_subjects = train_test_split(
    subject_labels["subjectid"],
    test_size=0.2,
    random_state=42,
    stratify=subject_labels["icu_days_binary"]
)

# Filter rows by subject ID
train_mask = df["subjectid"].isin(train_subjects)
val_mask = df["subjectid"].isin(val_subjects)

# Select features and labels, and drop identifiers
X_train = df[train_mask].drop(columns=["subjectid", "caseid", "icu_days_binary"])
X_val = df[val_mask].drop(columns=["subjectid", "caseid", "icu_days_binary"])
y_train = df[train_mask]["icu_days_binary"]
y_val = df[val_mask]["icu_days_binary"]

# Feedforward Feature Selection Setup
all_features = X_train.columns.tolist()
selected_features = []
remaining_features = all_features.copy()
n_features_to_select = 50  # you can adjust this

# Tracking metrics
metrics_history = {
    'n_features': [],
    'accuracy': [],
    'precision': [],
    'recall': [],
    'f1': [],
    'roc_auc': [],
    'average_precision': []
}

# Create cross-validation generator
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Start feedforward feature selection
previous_best_score = -np.inf  # Initialize with a very low F1 score
for step in range(n_features_to_select):
    print(f"\nStep {step+1}")
    best_feature = None
    best_score = previous_best_score  # Start with the previous best F1 score

    # Track scores for each fold to calculate mean
    fold_accuracies = []
    fold_precisions = []
    fold_recalls = []
    fold_f1s = []
    fold_roc_aucs = []
    fold_avg_precisions = []

    for feature in remaining_features:
        trial_features = selected_features + [feature]

        pipeline = Pipeline([
            ('model', XGBClassifier(
                n_estimators=300,
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

        # Cross-validation scores
        for train_idx, val_idx in cv.split(X_train[trial_features], y_train):
            X_train_fold, X_val_fold = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_train_fold, y_val_fold = y_train.iloc[train_idx], y_train.iloc[val_idx]

            pipeline.fit(X_train_fold[trial_features], y_train_fold)
            y_pred = pipeline.predict(X_val_fold[trial_features])
            y_prob = pipeline.predict_proba(X_val_fold[trial_features])[:, 1]

            fold_accuracies.append(accuracy_score(y_val_fold, y_pred))
            fold_precisions.append(precision_score(y_val_fold, y_pred))
            fold_recalls.append(recall_score(y_val_fold, y_pred))
            fold_f1s.append(f1_score(y_val_fold, y_pred))
            fold_roc_aucs.append(roc_auc_score(y_val_fold, y_prob))
            fold_avg_precisions.append(average_precision_score(y_val_fold, y_prob))

        mean_f1_score = np.mean(fold_f1s)

        # Add the feature as long as there is any improvement
        if mean_f1_score > best_score:
            best_score = mean_f1_score
            best_feature = feature

    if best_feature is None:
        print("No improvement, stopping early.")
        break

    # Update selected features
    selected_features.append(best_feature)
    remaining_features.remove(best_feature)
    print(f"Selected feature: {best_feature} - Mean F1 Score: {best_score:.4f}")

    # Record metrics for selected features after cross-validation
    metrics_history['n_features'].append(len(selected_features))
    metrics_history['accuracy'].append(np.mean(fold_accuracies))
    metrics_history['precision'].append(np.mean(fold_precisions))
    metrics_history['recall'].append(np.mean(fold_recalls))
    metrics_history['f1'].append(np.mean(fold_f1s))
    metrics_history['roc_auc'].append(np.mean(fold_roc_aucs))
    metrics_history['average_precision'].append(np.mean(fold_avg_precisions))

    # Update the previous best score
    previous_best_score = best_score

print("\nFinal selected features:")
print(selected_features)

# Convert history to dataframe
metrics_df = pd.DataFrame(metrics_history)
print("\nPerformance Metrics per Number of Features (averaged over 5 folds):")
print(metrics_df)

# Plot performance vs number of features
plt.figure(figsize=(10,6))
plt.plot(metrics_df['n_features'], metrics_df['accuracy'], marker='o', label='Accuracy')
plt.plot(metrics_df['n_features'], metrics_df['precision'], marker='s', label='Precision')
plt.plot(metrics_df['n_features'], metrics_df['recall'], marker='^', label='Recall')
plt.plot(metrics_df['n_features'], metrics_df['f1'], marker='v', label='F1 Score')
plt.plot(metrics_df['n_features'], metrics_df['roc_auc'], marker='D', label='ROC AUC')
plt.plot(metrics_df['n_features'], metrics_df['average_precision'], marker='x', label='Avg Precision (PR AUC)')
plt.xlabel('Number of Features Selected')
plt.ylabel('Score')
plt.title('Performance Metrics vs Number of Selected Features')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
