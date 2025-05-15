import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
import os

# Ensure Machine folder exists
os.makedirs("Machine", exist_ok=True)

# Load test features only
df_test = pd.read_csv("TestTrainingSet/test_ids_pre&peri.csv")

# Remove columns not used for training if they exist
for col in ['icu_days_binary', 'subjectid']:
    if col in df_test.columns:
        df_test = df_test.drop(columns=[col])

# Save case IDs if present
case_ids = df_test["caseid"] if "caseid" in df_test.columns else None

# Drop 'caseid' if present
if 'caseid' in df_test.columns:
    X_test = df_test.drop(columns=['caseid'])
else:
    X_test = df_test.copy()

# Check feature names from the model
model = joblib.load('Machine/best_xgboost_model_preperi.joblib')
model_features = model.get_booster().feature_names

# Select only model features from test set (to be safe)
X_test = X_test[model_features]

# Now you can predict safely
y_pred_proba = model.predict_proba(X_test)[:, 1]
y_pred = model.predict(X_test)

# Save predicted probabilities and labels along with case IDs
preds_df = pd.DataFrame({
    "caseid": case_ids if case_ids is not None else range(len(y_pred)),
    "predicted_probability": y_pred_proba,
    "predicted_label": y_pred
})
preds_df.to_csv("Machine/test_predictions.csv", index=False)
print("Predictions saved to Machine/test_predictions.csv")

# Optional: Calculate SHAP values for test features
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Handle shap values for binary classification (list)
if isinstance(shap_values, list):
    shap_values_positive_class = shap_values[1]
else:
    shap_values_positive_class = shap_values

# Check shape before saving SHAP values
if shap_values_positive_class.shape == X_test.shape:
    shap_values_df = pd.DataFrame(shap_values_positive_class, columns=X_test.columns)
    if case_ids is not None:
        shap_values_df.insert(0, "caseid", case_ids)
    shap_values_df.to_csv("Machine/shap_values.csv", index=False)
    print("SHAP values saved to Machine/shap_values.csv")
else:
    print("Warning: SHAP values shape does not match test feature matrix shape.")
