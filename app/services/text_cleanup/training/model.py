import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from app.services.text_cleanup.feature_extraction import (
    PageFeatureExtractor,
    ExerptFeatureExtractor,
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

    for file_name, group in grouped_data:
        feature_extractor = extractor_class()

        # Sort the group by page_number to ensure correct order
        group_sorted = group.sort_values("page_number")

        for text in group_sorted["text"]:
            feature_extractor.add(text)

        features_df = feature_extractor.extract_document_features()
        features_df["label"] = group_sorted["label"].reset_index(drop=True)
        feature_dataframes.append(features_df)

    return pd.concat(feature_dataframes, ignore_index=True)


def visualize_feature_importance(X, y):
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)
    feature_importance = pd.DataFrame(
        {"feature": X.columns, "importance": rf.feature_importances_}
    )
    feature_importance = feature_importance.sort_values("importance", ascending=False)

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

    pipeline = Pipeline([("scaler", StandardScaler()), ("svm", SVC(random_state=42))])

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
    print(classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title(f"Confusion Matrix for {model_name}")
    plt.colorbar()
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.tight_layout()
    plt.savefig(f"{model_name}_confusion_matrix.png")
    plt.close()

    cv_scores = cross_val_score(best_model, X, y, cv=10, scoring="precision")
    print(f"\nCross-validation scores (precision) for {model_name}:")
    print(f"Mean: {cv_scores.mean():.4f}, Std: {cv_scores.std():.4f}")

    joblib.dump(best_model, f"{model_name}_classifier.joblib")
    print(f"\nModel saved as '{model_name}_classifier.joblib'")


def main():
    # Page relevance model
    page_data = load_data(
        r"C:\Users\abden\Desktop\NestQ\disclaimer_classification_data.csv"
    )
    page_features = extract_features(page_data, PageFeatureExtractor)
    y_page = page_features["label"]
    X_page = page_features.drop(["label"], axis=1)

    visualize_feature_importance(X_page, y_page)
    train_and_evaluate_model(X_page, y_page, "page_relevance")

    # Exerpt relevance model
    exerpt_data = load_data(
        r"C:\Users\abden\Desktop\NestQ\exerpt_relevance_classification_data.csv"
    )
    exerpt_features = extract_features(exerpt_data, ExerptFeatureExtractor)
    y_exerpt = exerpt_features["label"]
    X_exerpt = exerpt_features.drop(["label"], axis=1)

    visualize_feature_importance(X_exerpt, y_exerpt)
    train_and_evaluate_model(X_exerpt, y_exerpt, "exerpt_relevance")


if __name__ == "__main__":
    main()
