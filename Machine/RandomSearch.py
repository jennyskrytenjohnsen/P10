import xgboost as xgb
import numpy as np
import pandas as pd
import os
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import log_loss
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import brier_score_loss

# Ensure 'Machine' folder exists
os.makedirs('Machine', exist_ok=True)

# Load dataset
df = pd.read_csv("TestTrainingSet/train_ids_pre.csv")

# Define label (y) and drop from features
y = df["icu_days_binary"]

# Drop unwanted columns from features
X = df.drop(columns=["icu_days_binary", "subjectid"])

# Stratify based on unique case IDs
caseid_labels = df.groupby("caseid")["icu_days_binary"].first().reset_index()

# Stratified split on unique case IDs
train_ids, test_ids = train_test_split(
    caseid_labels["caseid"],
    test_size=0.2,
    random_state=42,
    stratify=caseid_labels["icu_days_binary"]
)

# Boolean masks for splitting
train_mask = X["caseid"].isin(train_ids)
test_mask = X["caseid"].isin(test_ids)

# Final train/test sets without 'caseid'
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
    'n_estimators': np.arange(50, 151, 25),  # e.g. [50, 75, 100, 125, 150]
    'max_depth': np.arange(3, 15),
    'min_child_weight': np.arange(1, 10),
    'gamma': np.linspace(0, 5, 6)
}

# Randomized Search CV
random_search = RandomizedSearchCV(
    xg_clf,
    param_distributions=param_dist,
    n_iter=100,
    cv=5,
    verbose=2,
    random_state=11,
    n_jobs=-1,
    scoring='neg_brier_score'
)

# Fit model
random_search.fit(X_train, y_train)

# Collect results
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

# Save results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv('Machine/xgboost_random_search_results_pre.csv', index=False)

# Print result preview
print(results_df.head())

# Save best model
best_model = random_search.best_estimator_
model_path = 'Machine/best_xgboost_model_pre.joblib'
joblib.dump(best_model, model_path)
print(f"Best model saved to {model_path}")

# --- Print best hyperparameters ---
print("\nBest hyperparameters found:")
print(random_search.best_params_)

# --- Evaluate best model on test data ---
y_pred_proba_best = best_model.predict_proba(X_test)[:, 1]  # Probability for class 1

# Calculate metrics
logloss_best = log_loss(y_test, y_pred_proba_best)
brier_best = brier_score_loss(y_test, y_pred_proba_best)

print(f"\nBest Model Performance on Test Set:")
print(f"Log Loss: {logloss_best:.4f}")
print(f"Brier Score: {brier_best:.4f}")

# --- Plot log loss and Brier score for the best model across boosting rounds ---
##

# Copy best model parameters and remove eval_metric to avoid duplication
best_params = best_model.get_params().copy()
best_params.pop('eval_metric', None)  # Remove if present

# Recreate model with eval_metric explicitly set
best_model_eval = xgb.XGBClassifier(
    **best_params,
    use_label_encoder=False,
    eval_metric=["logloss"]  # Brier not natively supported, only logloss
)

best_model_eval.fit(
    X_train,
    y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

eval_result = best_model_eval.evals_result()


# Extract log loss over boosting rounds
logloss_values = eval_result['validation_0']['logloss']

# Plot log loss vs number of trees
import matplotlib.pyplot as plt

# plt.figure(figsize=(8, 5))
# plt.plot(logloss_values, label='Log Loss', marker='o')
# plt.title("Best Model")
# plt.xlabel("Boosting Rounds")
# plt.ylabel("Log Loss")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.savefig("Machine/best_model_logloss_curve.png")
# plt.show()

# Calculate Brier score for each boosting round
num_rounds = len(logloss_values)
brier_scores = []

for i in range(1, num_rounds + 1):
    # Predict probabilities using the first i trees
    y_pred_proba_iter = best_model_eval.predict_proba(X_test, iteration_range=(0, i))[:, 1]
    brier = brier_score_loss(y_test, y_pred_proba_iter)
    brier_scores.append(brier)

# Plot log loss and Brier score with twin y-axes
fig, ax1 = plt.subplots(figsize=(10, 6))

color1 = 'tab:blue'
ax1.set_xlabel('Boosting Rounds')
ax1.set_ylabel('Log Loss', color=color1)
ax1.plot(range(1, num_rounds + 1), logloss_values, label='Log Loss', color=color1, marker='o')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color2 = 'tab:orange'
ax2.set_ylabel('Brier Score', color=color2)
ax2.plot(range(1, num_rounds + 1), brier_scores, label='Brier Score', color=color2, marker='x')
ax2.tick_params(axis='y', labelcolor=color2)

fig.suptitle("Best Model Log Loss and Brier Score vs Boosting Rounds")
fig.tight_layout(rect=[0, 0, 1, 0.95])

# Save and show the plot
plt.savefig("Machine/best_model_logloss_brier_curve.png")
plt.show()
