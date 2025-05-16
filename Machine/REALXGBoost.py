import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
import os
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    brier_score_loss, confusion_matrix, roc_curve, auc, precision_recall_curve
)

# Ensure Machine folder exists
os.makedirs("Machine", exist_ok=True)

# Load test features only
df_test = pd.read_csv("TestTrainingSet/test_ids_pre.csv") #ÆNDRE HER FOR pre vs preperi

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

# Load model and get feature names
model = joblib.load('Machine/best_xgboost_model_pre.joblib') #ÆNDRE HER FOR pre vs preperi
model_features = model.get_booster().feature_names

# Ensure test features match model
X_test = X_test[model_features]

# Predict probabilities and labels
y_pred_proba = model.predict_proba(X_test)[:, 1]
y_pred = model.predict(X_test)

# Save predictions
preds_df = pd.DataFrame({
    "caseid": case_ids if case_ids is not None else range(len(y_pred)),
    "predicted_probability": y_pred_proba,
    "predicted_label": y_pred
})
preds_df.to_csv("Machine/test_predictions_pre.csv", index=False) #ÆNDRE HER FOR pre vs preperi
print("Predictions saved to Machine/test_predictions_pre.csv") #ÆNDRE HER FOR pre vs preperi

# If true labels exist in original test data, evaluate performance
if 'icu_days_binary' in pd.read_csv("TestTrainingSet/test_ids_pre.csv").columns: #ÆNDRE HER FOR pre vs preperi
    df_with_labels = pd.read_csv("TestTrainingSet/test_ids_pre.csv") #ÆNDRE HER FOR pre vs preperi
    y_true = df_with_labels.loc[X_test.index, 'icu_days_binary']

    # Metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    brier = brier_score_loss(y_true, y_pred_proba)

    # Sensitivity and specificity
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)

    print("\nPerformance Metrics:")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"Brier Score: {brier:.4f}")
    print(f"Sensitivity (Recall): {sensitivity:.4f}")
    print(f"Specificity:          {specificity:.4f}")

    # ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate (Sensitivity)')
    plt.title('ROC Curve')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("Machine/roc_curve.png")
    plt.show()

    # Precision-Recall Curve
    precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)

    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, label='Precision-Recall Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("Machine/precision_recall_curve.png")
    plt.show()
else:
    print("No true labels found in the test data. Performance metrics not computed.")

# Optional: Calculate SHAP values
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

if isinstance(shap_values, list):
    shap_values_positive_class = shap_values[1]
else:
    shap_values_positive_class = shap_values

# Save SHAP values
if shap_values_positive_class.shape == X_test.shape:
    shap_values_df = pd.DataFrame(shap_values_positive_class, columns=X_test.columns)
    if case_ids is not None:
        shap_values_df.insert(0, "caseid", case_ids)
    shap_values_df.to_csv("Machine/shap_values_pre.csv", index=False) #ÆNDRE HER FOR pre vs preperi
    print("SHAP values saved to Machine/shap_values_pre.csv") #ÆNDRE HER FOR pre vs preperi
else:
    print("Warning: SHAP values shape does not match test feature matrix shape.")
