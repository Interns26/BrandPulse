"""
Module: train.py
Purpose: Trains the Multi-Output Random Forest model using the synthetic dataset.
Mechanism: Standardizes numerical scales, one-hot encodes string categories, 
fits decision trees to the three target variables, evaluates accuracy, and exports a .pkl binary.
"""

import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def train_decision_engine(data_path: str = "synthetic_campaigns.csv", model_output_path: str = "../../models_storage/campaign_decision_model.pkl"):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Run generate_synthetic.py first.")

    df = pd.read_csv(data_path)

    # X represents the input feature matrix (the data we know).
    X = df[[
        "severity", 
        "urgency", 
        "volume", 
        "confidence_score", 
        "opportunity_score", 
        "article_age", 
        "vulnerability_type"
    ]]
    
    # Y represents the multi-output targets (the decisions we want to predict).
    Y = df[["strategy", "channel", "content_type"]]

    numeric_features = ["severity", "urgency", "volume", "confidence_score", "opportunity_score", "article_age"]
    categorical_features = ["vulnerability_type"]

    # Preprocessor normalizes the data.
    # StandardScaler: Converts 0-100 ranges into standardized Z-scores so large numbers don't dominate.
    # OneHotEncoder: Converts the vulnerability string (e.g., "Data Breach") into binary columns (0 or 1).
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )

    # Base estimator: Random Forest with 100 decision trees.
    # class_weight="balanced" penalizes the model heavier for missing rare classifications.
    rf_base = RandomForestClassifier(
        n_estimators=100, 
        max_depth=10, 
        random_state=42, 
        class_weight="balanced"
    )

    # Pipeline chains the preprocessing and the classifier together.
    # MultiOutputClassifier duplicates the Random Forest to predict all 3 targets simultaneously.
    model_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", MultiOutputClassifier(rf_base))
    ])

    # 80/20 train-test split for statistical evaluation.
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.20, random_state=42)

    # FIT: The model studies the relationships and locks in its mathematical weights.
    model_pipeline.fit(X_train, Y_train)

    # EVALUATE: Ask the model to predict on the 20% holdout set and compare against the ground truth.
    Y_pred = model_pipeline.predict(X_test)
    Y_pred_df = pd.DataFrame(Y_pred, columns=Y_test.columns, index=Y_test.index)

    print("=== EVALUATION METRICS ===")
    for col in Y_test.columns:
        print(f"\n--- Output Target: {col} ---")
        print(classification_report(Y_test[col], Y_pred_df[col]))

    # Serialize the trained pipeline into a binary file for rapid inference in production.
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(model_pipeline, model_output_path)
    print(f"Model saved to {model_output_path}")

if __name__ == "__main__":
    train_decision_engine()