
import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, log_loss
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.model_selection import cross_val_score
from sklearn.base import clone


####### FORWARDS #########

# Load csv file with features 
df_data_features = pd.read_csv("df_extracted_features_pre&peri.csv")
df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")

# Merge features and labels on 'caseid'
df_merged = df_data_features.merge(df_data_labels, on="caseid")

# Remove 'icu_days' if present
df_merged = df_merged.drop(columns=['icu_days'], errors='ignore')

# Extract features and labels
X = df_merged.drop(columns=["icu_days_binary"])
y = df_merged["icu_days_binary"]

# Extract case IDs for group splitting
case_ids = X["caseid"].unique()

# Split the unique case IDs into train and test sets
train_ids, test_ids = train_test_split(case_ids, test_size=0.2, random_state=42)

# Create boolean masks to filter rows by case ID
train_mask = X["caseid"].isin(train_ids)
test_mask = X["caseid"].isin(test_ids)

# Apply masks to select features and targets
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

# Prepare lists to store the results
probabilities_history = []

# Base model setup
base_model = XGBClassifier(
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

# Prepare feature sets
all_features = list(X_train.columns)
selected_features = []
remaining_features = all_features.copy()

probabilities_history = []

best_auc = 0
iteration = 0

while remaining_features:
    iteration += 1
    print(f"\nIteration {iteration}: {len(remaining_features)} features remaining...")

    scores = []
    for feature in remaining_features:
        trial_features = selected_features + [feature]
        model = clone(base_model)
        auc_cv = cross_val_score(model, X_train[trial_features], y_train, cv=5, scoring='roc_auc').mean()
        scores.append((auc_cv, feature))

    # Sort scores descending by AUC
    scores.sort(reverse=True)
    best_trial_auc, best_feature = scores[0]

    if best_trial_auc > best_auc:
        best_auc = best_trial_auc
        selected_features.append(best_feature)
        remaining_features.remove(best_feature)
        probabilities_history.append({
            "Iteration": iteration,
            "AUC": best_auc,
            "Added_Feature": best_feature
        })
        print(f" ➤ Added: {best_feature} | CV AUC: {best_auc:.4f}")
    else:
        print(" ✖ No improvement — stopping.")
        break


####### BACKWARDS #########

# # Load csv file with features 
# df_data_features = pd.read_csv("df_extracted_features_pre&peri.csv")
# df_data_labels = pd.read_csv("For_machinelearning/number_of_days_in_ICU.csv")

# # Merge features and labels on 'caseid'
# df_merged = df_data_features.merge(df_data_labels, on="caseid")

# # Remove 'icu_days' if present
# df_merged = df_merged.drop(columns=['icu_days'], errors='ignore')

# # Extract features and labels
# X = df_merged.drop(columns=["icu_days_binary"])
# y = df_merged["icu_days_binary"]

# # Extract case IDs for group splitting
# case_ids = X["caseid"].unique()

# # Split the unique case IDs into train and test sets
# train_ids, test_ids = train_test_split(case_ids, test_size=0.2, random_state=42)

# # Create boolean masks to filter rows by case ID
# train_mask = X["caseid"].isin(train_ids)
# test_mask = X["caseid"].isin(test_ids)

# # Apply masks to select features and targets
# X_train = X[train_mask].drop(columns=["caseid"])
# X_test = X[test_mask].drop(columns=["caseid"])
# y_train = y[train_mask]
# y_test = y[test_mask]

# # Check stratification
# def check_stratification(name, labels):
#     ratio = labels.mean()
#     print(f"{name} positive class ratio (icu_days_binary == 1): {ratio:.4f} ({labels.sum()}/{len(labels)})")

# check_stratification("Full dataset", y)
# check_stratification("Training set", y_train)
# check_stratification("Test set", y_test)

# # Prepare lists to store the results
# probabilities_history = []

# # Initialize the model
# model = XGBClassifier(
#     n_estimators=300,
#     max_depth=4,
#     learning_rate=0.05,
#     subsample=0.8,
#     colsample_bytree=0.8,
#     gamma=1,
#     min_child_weight=5,
#     eval_metric='logloss',
#     random_state=42
# )

# # Initial model
# model.fit(X_train, y_train)
# y_prob = model.predict_proba(X_test)[:, 1]

# # Save initial AUC and log-loss
# initial_auc = roc_auc_score(y_test, y_prob)
# initial_log_loss = log_loss(y_test, y_prob)

# probabilities_history.append({
#     "Iteration": 0,
#     "AUC": initial_auc,
#     "Log_Loss": initial_log_loss,
#     "Predicted_Probabilities": y_prob
# })

# # Backward elimination loop
# iteration = 0
# selected_features = list(X_train.columns)

# while len(selected_features) > 1:
#     iteration += 1
#     print(f"\nIteration {iteration}: {len(selected_features)} features remaining...")

#     scores = []
#     for feature in selected_features:
#         trial_features = [f for f in selected_features if f != feature]
#         model.fit(X_train[trial_features], y_train)
#         y_prob = model.predict_proba(X_test[trial_features])[:, 1]
        
#         # Calculate AUC and log-loss
#         auc_score = roc_auc_score(y_test, y_prob)
#         log_loss_score = log_loss(y_test, y_prob)
        
#         scores.append((auc_score, log_loss_score, feature))

#     # Sort and choose the best feature to remove
#     scores.sort(reverse=True)
#     best_auc_score, best_log_loss_score, feature_to_remove = scores[0]

#     if best_auc_score >= probabilities_history[-1]["AUC"]:
#         selected_features.remove(feature_to_remove)
#         probabilities_history.append({
#             "Iteration": iteration,
#             "AUC": best_auc_score,
#             "Log_Loss": best_log_loss_score,
#             "Predicted_Probabilities": y_prob
#         })
#         print(f" ➤ Removed: {feature_to_remove} | AUC: {best_auc_score:.3f}")
#     else:
#         print(" ✖ No improvement — stopping.")
#         break

# # Save results to CSV files
# probabilities_df = pd.DataFrame(probabilities_history)

# # Save the probabilities and evaluation results (AUC and Log-Loss)
# probabilities_df.to_csv("Machine/model_probabilities_results.csv", index=False)

# print("\nFinal model evaluation:")
# # Evaluate final model
# model.fit(X_train[selected_features], y_train)
# y_prob = model.predict_proba(X_test[selected_features])[:, 1]
# final_auc = roc_auc_score(y_test, y_prob)
# final_log_loss = log_loss(y_test, y_prob)

# print(f"Final AUC: {final_auc:.3f}")
# print(f"Final Log-Loss: {final_log_loss:.3f}")
