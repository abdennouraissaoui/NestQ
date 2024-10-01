import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from model.feature_extraction import (
    PageFeatureExtractor,
    excerptFeatureExtractor,
)


def load_data(file_path):
    data = pd.read_csv(file_path)
    print(f"Dataset summary for {file_path}:")
    print(data.describe())
    print(f"Class distribution:\n{data['label'].value_counts(normalize=True)}")
    return data


def extract_features(data, extractor_class):
    grouped_data = data.groupby("file_name")
    feature_dataframes = []

    for file_name, document in grouped_data:
        feature_extractor = extractor_class()

        for text in document["text"]:
            feature_extractor.add(text)

        features_df = feature_extractor.extract_document_features()
        features_df["label"] = document["label"].reset_index(drop=True)
        feature_dataframes.append(features_df)

    return pd.concat(feature_dataframes, ignore_index=True)


def visualize_feature_importance(X, y):
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)
    feature_importance = pd.DataFrame(
        {"feature": X.columns, "importance": rf.feature_importances_}
    )
    feature_importance = feature_importance.sort_values(
        "importance", ascending=False
    )

    plt.figure(figsize=(10, 6))
    plt.barh(feature_importance["feature"], feature_importance["importance"])
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title("Feature Importance")
    plt.tight_layout()
    plt.savefig("feature_importance.png")
    plt.close()


def train_and_evaluate_model(X, y, model_name):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = Pipeline(
        [("scaler", StandardScaler()), ("svm", SVC(random_state=42))]
    )

    param_grid = [
        {
            "svm__kernel": ["rbf"],
            "svm__C": [0.001, 0.1, 1, 10, 100],
            "svm__gamma": ["scale", "auto", 0.1, 1],
        },
        {
            "svm__kernel": ["linear"],
            "svm__C": [0.001, 0.1, 1, 10, 100],
        },
    ]

    grid_search = GridSearchCV(
        pipeline, param_grid, cv=10, scoring="precision", n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)

    print(f"\nBest model parameters for {model_name}:")
    print(grid_search.best_params_)

    print(f"\nClassification Report for {model_name}:")
    print(classification_report(y_test, y_pred, zero_division=1))

    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(
        cm,
        columns=["Predicted Negative", "Predicted Positive"],
        index=["Actual Negative", "Actual Positive"],
    )
    print(f"\nConfusion Matrix for {model_name}:")
    print(cm_df)

    cv_scores = cross_val_score(best_model, X, y, cv=10, scoring="precision")
    print(f"\nCross-validation scores (precision) for {model_name}:")
    print(f"Mean: {cv_scores.mean():.4f}, Std: {cv_scores.std():.4f}")

    joblib.dump(best_model, f"{model_name}_classifier.joblib")
    print(f"\nModel saved as '{model_name}_classifier.joblib'")


def main():
    # Page relevance model
    # page_data = load_data(r"./model/data/disclaimer_classification_data.csv")
    # page_features = extract_features(page_data, PageFeatureExtractor)
    # y_page = page_features["label"]
    # X_page = page_features.drop(["label"], axis=1)

    # visualize_feature_importance(X_page, y_page)
    # train_and_evaluate_model(X_page, y_page, "page_relevance")

    # excerpt relevance model
    excerpt_data = load_data(
        r"./model/data/excerpt_relevance_classification_data.csv"
    )
    excerpt_features = extract_features(excerpt_data, excerptFeatureExtractor)
    y_excerpt = excerpt_features["label"]
    X_excerpt = excerpt_features.drop(["label"], axis=1)

    visualize_feature_importance(X_excerpt, y_excerpt)
    train_and_evaluate_model(X_excerpt, y_excerpt, "excerpt_relevance")


if __name__ == "__main__":
    main()
