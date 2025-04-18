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
import warnings
warnings.filterwarnings('ignore')

# Load csv file with features 
df_data_features = pd.read_csv("df_extracted_features.csv")

# Load csv file with labels
df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")

# Extract features and labels
X = df_data_features
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

# Apply masks to select features and targets, and drop caseid column from features
X_train = df_data_features[train_mask].drop(columns=["caseid"])
X_test = df_data_features[test_mask].drop(columns=["caseid"])
y_train = y[train_mask]
y_test = y[test_mask]

# Backward Feature Elimination Setup
all_features = X_train.columns.tolist()
selected_features = all_features.copy()

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

# Start backward feature elimination
while len(selected_features) > 1:
    print(f"\nStep with {len(selected_features)} features")
    worst_feature = None
    best_score = -np.inf
    current_features = selected_features.copy()

    for feature in selected_features:
        trial_features = [f for f in current_features if f != feature]

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

        pipeline.fit(X_train[trial_features], y_train)
        y_prob = pipeline.predict_proba(X_test[trial_features])[:, 1]
        score = average_precision_score(y_test, y_prob)

        if score > best_score:
            best_score = score
            worst_feature = feature

    if worst_feature is None:
        print("No improvement, stopping early.")
        break

    # Remove the feature
    selected_features.remove(worst_feature)
    print(f"Removed feature: {worst_feature} - Avg Precision Score: {best_score:.4f}")

    # Retrain model on current selected features and record full metrics
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

    pipeline.fit(X_train[selected_features], y_train)
    y_pred = pipeline.predict(X_test[selected_features])
    y_prob = pipeline.predict_proba(X_test[selected_features])[:, 1]

    metrics_history['n_features'].append(len(selected_features))
    metrics_history['accuracy'].append(accuracy_score(y_test, y_pred))
    metrics_history['precision'].append(precision_score(y_test, y_pred))
    metrics_history['recall'].append(recall_score(y_test, y_pred))
    metrics_history['f1'].append(f1_score(y_test, y_pred))
    metrics_history['roc_auc'].append(roc_auc_score(y_test, y_prob))
    metrics_history['average_precision'].append(average_precision_score(y_test, y_prob))

print("\nFinal selected features:")
print(selected_features)

# Convert history to dataframe
metrics_df = pd.DataFrame(metrics_history)
print("\nPerformance Metrics per Number of Features:")
print(metrics_df)

# Plot performance vs number of features
plt.figure(figsize=(10,6))
plt.plot(metrics_df['n_features'], metrics_df['accuracy'], marker='o', label='Accuracy')
plt.plot(metrics_df['n_features'], metrics_df['precision'], marker='s', label='Precision')
plt.plot(metrics_df['n_features'], metrics_df['recall'], marker='^', label='Recall')
plt.plot(metrics_df['n_features'], metrics_df['f1'], marker='v', label='F1 Score')
plt.plot(metrics_df['n_features'], metrics_df['roc_auc'], marker='D', label='ROC AUC')
plt.plot(metrics_df['n_features'], metrics_df['average_precision'], marker='x', label='Avg Precision (PR AUC)')
plt.xlabel('Number of Features Remaining')
plt.ylabel('Score')
plt.title('Performance Metrics vs Number of Features (Backward Selection)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
