import shap
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

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

# Use the same model config you trained earlier
model_top = XGBClassifier(
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


# Fit the model (on full training data with all features)
model_top.fit(X_train, y_train)

# Initialize SHAP explainer
explainer = shap.Explainer(model_top, X_train)

# Calculate SHAP values
shap_values = explainer(X_train)

# Bar plot of top 20 features
shap.plots.bar(shap_values, max_display=20)

# Beeswarm plot
shap.plots.beeswarm(shap_values, max_display=20)


# Get mean absolute SHAP values per feature
mean_shap = np.abs(shap_values.values).mean(axis=0)
feature_names = X_train.columns
shap_importance = pd.Series(mean_shap, index=feature_names).sort_values(ascending=False)

# Show top 20 most important features
top_n = 20
top_features = shap_importance.head(top_n).index.tolist()
print(f"\n Top {top_n} features based on SHAP:")
print(top_features)

# OPTIONAL: retrain model using only top SHAP features
model_top = XGBClassifier(
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

model_top.fit(X_train[top_features], y_train)




