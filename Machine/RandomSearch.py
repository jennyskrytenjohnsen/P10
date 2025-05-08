import xgboost as xgb
import numpy as np
import pandas as pd
import os
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import log_loss
import joblib

# Ensure 'Machine' folder exists
os.makedirs('Machine', exist_ok=True)

# Load features and labels
df_data_features = pd.read_csv("TestTrainingSet/train_ids_pre&peri.csv")
df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")

# Merge on 'caseid'
df_merged = df_data_features.merge(df_data_labels, on="caseid")

# Drop 'icu_days' column if it exists
df_merged = df_merged.drop(columns=['icu_days'], errors='ignore')

# Define features (X) and labels (y)
X = df_merged.drop(columns=["icu_days_binary"])
y = df_merged["icu_days_binary"]

# Stratify case IDs based on label
# We'll take the first label from each caseid group
caseid_labels = df_merged.groupby("caseid")["icu_days_binary"].first().reset_index()

# Stratified split on unique case IDs
train_ids, test_ids = train_test_split(
    caseid_labels["caseid"],
    test_size=0.2,
    random_state=42,
    stratify=caseid_labels["icu_days_binary"]
)

# Create boolean masks
train_mask = X["caseid"].isin(train_ids)
test_mask = X["caseid"].isin(test_ids)

# Final datasets without 'caseid'
X_train = X[train_mask].drop(columns=["caseid"])
X_test = X[test_mask].drop(columns=["caseid"])
y_train = y[train_mask]
y_test = y[test_mask]

# Check stratification
def check_stratification(name, labels):
    ratio = labels.mean()
    print(f"{name} positive class ratio (icu_days_binary == 1): {ratio:.4f} ({labels.sum()}/{len(labels)})")

check_stratification("Full dataset", y)
check_stratification("Training set", y_train)
check_stratification("Test set", y_test)


# Initialize XGBoost classifier
xg_clf = xgb.XGBClassifier(objective="binary:logistic", random_state=42, eval_metric='logloss')

# Define hyperparameter space
param_dist = {
    'learning_rate': np.linspace(0.01, 0.3, 30),
    'n_estimators': np.arange(50, 300, 50),
    'max_depth': np.arange(3, 15),
    'min_child_weight': np.arange(1, 10),
    'gamma': np.linspace(0, 5, 6)
}

# Perform Randomized Search
random_search = RandomizedSearchCV(
    xg_clf,
    param_distributions=param_dist,
    n_iter=100,
    cv=5,
    verbose=2,
    random_state=42,
    n_jobs=-1,
    scoring='neg_brier_score'
)

# Fit to training data
random_search.fit(X_train, y_train)

# Store all results
results = []

for i in range(random_search.n_iter):
    params = random_search.cv_results_['params'][i]
    neg_brier_score = random_search.cv_results_['mean_test_score'][i]

    model = xgb.XGBClassifier(
        objective="binary:logistic",
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss',
        **params
    )
    model.fit(X_train, y_train)

    y_pred_proba = model.predict_proba(X_test)
    logloss = log_loss(y_test, y_pred_proba)

    results.append({**params, 'log_loss': logloss, 'neg_brier_score': neg_brier_score})

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv('Machine/xgboost_random_search_results.csv', index=False)

# Print preview
print(results_df.head())

# Get best model from RandomizedSearchCV
best_model = random_search.best_estimator_

# Save the best model to disk
model_path = 'Machine/best_xgboost_model.joblib'
joblib.dump(best_model, model_path)

print(f"Best model saved to {model_path}")
