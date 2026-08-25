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

    X = df[[
        "severity", 
        "urgency", 
        "volume", 
        "confidence_score", 
        "opportunity_score", 
        "article_age", 
        "vulnerability_type"
    ]]
    
    Y = df[["strategy", "channel", "content_type"]]

    numeric_features = ["severity", "urgency", "volume", "confidence_score", "opportunity_score", "article_age"]
    categorical_features = ["vulnerability_type"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )

    rf_base = RandomForestClassifier(
        n_estimators=100, 
        max_depth=10, 
        random_state=42, 
        class_weight="balanced"
    )

    model_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", MultiOutputClassifier(rf_base))
    ])

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.20, random_state=42)

    model_pipeline.fit(X_train, Y_train)

    Y_pred = model_pipeline.predict(X_test)
    Y_pred_df = pd.DataFrame(Y_pred, columns=Y_test.columns, index=Y_test.index)

    print("=== EVALUATION METRICS ===")
    for col in Y_test.columns:
        print(f"\n--- Output Target: {col} ---")
        print(classification_report(Y_test[col], Y_pred_df[col]))

    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(model_pipeline, model_output_path)
    print(f"Model saved to {model_output_path}")

if __name__ == "__main__":
    train_decision_engine()