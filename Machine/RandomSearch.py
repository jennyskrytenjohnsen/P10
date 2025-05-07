import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss

# Generate a synthetic binary classification dataset
X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create XGBoost classifier model
xg_clf = xgb.XGBClassifier(objective="binary:logistic", random_state=42)

# Define the hyperparameter grid for random search
param_dist = {
    'learning_rate': np.linspace(0.01, 0.3, 30),
    'n_estimators': np.arange(50, 300, 50),
    'max_depth': np.arange(3, 15),
    'min_child_weight': np.arange(1, 10),
    'gamma': np.linspace(0, 5, 6)
}

# Perform Randomized Search with cross-validation
random_search = RandomizedSearchCV(
    xg_clf,
    param_distributions=param_dist,
    n_iter=100,
    cv=5,
    verbose=2,
    random_state=42,
    n_jobs=-1
)

# Fit the model to the training data
random_search.fit(X_train, y_train)

# Initialize a list to store results
results = []

# Loop over the results of each random search iteration
for i in range(random_search.n_iter):
    # Extract the hyperparameters
    params = random_search.cv_results_['params'][i]
    
    # Get the CV mean test score
    mean_test_score = random_search.cv_results_['mean_test_score'][i]
    
    # Train a model using these parameters to evaluate log loss on test set
    model = xgb.XGBClassifier(
        objective="binary:logistic",
        random_state=42,
        **params
    )
    model.fit(X_train, y_train)
    
    # Predict probabilities and calculate log loss
    y_pred_proba = model.predict_proba(X_test)
    logloss = log_loss(y_test, y_pred_proba)
    
    # Store the result
    results.append({**params, 'log_loss': logloss, 'mean_test_score': mean_test_score})

# Save results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv('Machine/xgboost_random_search_results.csv', index=False)

# Print preview
print(results_df.head())
