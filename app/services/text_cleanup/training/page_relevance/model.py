import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import joblib
from app.services.text_cleanup.feature_extraction import PageFeatureExtractor

# Data Loading
data = pd.read_csv(r"C:\Users\abden\Desktop\NestQ\disclaimer_classification_data.csv")
print("Dataset summary:")
print(data.describe())
print(f"Class distribution:\n{data['label'].value_counts(normalize=True)}")

# Feature Engineering
grouped_data = data.groupby("file_name")

feature_dataframes = []

for file_name, group in grouped_data:
    feature_extractor = PageFeatureExtractor()

    # Sort the group by page_number to ensure correct order
    group_sorted = group.sort_values("page_number")

    for page_text in group_sorted["page_text"]:
        feature_extractor.add_page(page_text)

    features_df = feature_extractor.extract_features()

    features_df["label"] = group_sorted["label"].reset_index(drop=True)

    feature_dataframes.append(features_df)

# Concatenate all feature DataFrames
X = pd.concat(feature_dataframes, ignore_index=True)

# Separate features and labels
y = X["label"]
X = X.drop(["label"], axis=1)

# Feature Selection and Visualization
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

# Model Training
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

pipeline = Pipeline([("scaler", StandardScaler()), ("svm", SVC(random_state=42))])

param_grid = [
    {
        "svm__kernel": ["rbf"],
        "svm__C": [0.1, 1, 10, 100],
        "svm__gamma": ["scale", "auto", 0.1, 1],
    },
    {
        "svm__kernel": ["linear"],
        "svm__C": [0.1, 1, 10, 100],
    },
]

grid_search = GridSearchCV(pipeline, param_grid, cv=10, scoring="precision", n_jobs=-1)
grid_search.fit(X_train, y_train)

# Model Evaluation
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)

print("\nBest model parameters:")
print(grid_search.best_params_)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
print(cm)

cv_scores = cross_val_score(best_model, X, y, cv=10, scoring="precision")
print("\nCross-validation scores (precision):")
print(f"Mean: {cv_scores.mean():.4f}, Std: {cv_scores.std():.4f}")

# Model Persistence
joblib.dump(best_model, "disclaimer_classifier.joblib")
print("\nModel saved as 'disclaimer_classifier.joblib'")

# python -m app.services.text_cleanup.training.page_relevance.model
