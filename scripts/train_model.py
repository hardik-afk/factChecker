"""
VeriVibe — ML Training Pipeline
================================
Trains a Logistic Regression classifier on the Kaggle "Fake and Real News Dataset"
and exports serialized artifacts for the FastAPI backend.

Dataset:
    Download from https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset
    Place `True.csv` and `Fake.csv` into the `data/` directory.

Usage:
    python scripts/train_model.py
"""

import re
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Paths (all relative to project root)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "backend" / "models"

# Hyperparameters
MAX_FEATURES = 10_000
NGRAM_RANGE = (1, 2)
TEST_SIZE = 0.2
RANDOM_STATE = 42
MAX_ITER = 1000


# ---------------------------------------------------------------------------
# 1. Data Ingestion
# ---------------------------------------------------------------------------
def load_data(data_dir: Path) -> pd.DataFrame:
    """
    Load and label the Kaggle Fake/Real News CSVs.

    Returns a shuffled DataFrame with columns: ['text', 'label']
        label=1 → Real news
        label=0 → Fake news
    """
    true_path = data_dir / "True.csv"
    fake_path = data_dir / "Fake.csv"

    if not true_path.exists() or not fake_path.exists():
        print(
            "\n❌  Dataset not found!\n"
            "    Please download the Kaggle 'Fake and Real News Dataset':\n"
            "    https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset\n"
            f"    Place True.csv and Fake.csv into: {data_dir}\n"
        )
        sys.exit(1)

    df_real = pd.read_csv(true_path)
    df_fake = pd.read_csv(fake_path)

    df_real["label"] = 1
    df_fake["label"] = 0

    # Combine title + text into a single field for richer signal
    for df in (df_real, df_fake):
        df["text"] = df["title"].fillna("") + " " + df["text"].fillna("")

    df = pd.concat([df_real[["text", "label"]], df_fake[["text", "label"]]], ignore_index=True)
    df = df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    print(f"✅  Loaded {len(df):,} articles  (Real: {(df['label']==1).sum():,} | Fake: {(df['label']==0).sum():,})")
    return df


# ---------------------------------------------------------------------------
# 2. Preprocessing
# ---------------------------------------------------------------------------
def preprocess(text: str) -> str:
    """
    Clean a single text string:
      - Lowercase
      - Strip punctuation and digits
      - (Stop-word removal handled by TfidfVectorizer)
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)  # keep only letters and whitespace
    text = re.sub(r"\s+", " ", text).strip()  # collapse multiple spaces
    return text


# ---------------------------------------------------------------------------
# 3. Training
# ---------------------------------------------------------------------------
def build_vectorizer() -> TfidfVectorizer:
    """Return a configured TF-IDF vectorizer with built-in stop-word removal."""
    return TfidfVectorizer(
        max_features=MAX_FEATURES,
        ngram_range=NGRAM_RANGE,
        stop_words="english",  # scikit-learn built-in list — no nltk needed
        sublinear_tf=True,     # apply log normalization for better performance
    )


def train_model(X_train, y_train) -> LogisticRegression:
    """Fit a Logistic Regression classifier."""
    model = LogisticRegression(
        max_iter=MAX_ITER,
        random_state=RANDOM_STATE,
        solver="lbfgs",
        C=1.0,
    )
    model.fit(X_train, y_train)
    return model


# ---------------------------------------------------------------------------
# 4. Evaluation
# ---------------------------------------------------------------------------
def evaluate(model, X_test, y_test) -> float:
    """Print evaluation metrics and return accuracy."""
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("\n" + "=" * 60)
    print("  MODEL EVALUATION REPORT")
    print("=" * 60)
    print(f"\n  Accuracy: {acc:.4f}  ({acc*100:.2f}%)\n")
    print("  Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"    {'':>12} Pred Fake   Pred Real")
    print(f"    {'Actual Fake':>12}   {cm[0][0]:>5}       {cm[0][1]:>5}")
    print(f"    {'Actual Real':>12}   {cm[1][0]:>5}       {cm[1][1]:>5}")
    print(f"\n  Classification Report:\n")
    print(
        classification_report(
            y_test, y_pred, target_names=["Fake", "Real"]
        )
    )
    print("=" * 60)
    return acc


# ---------------------------------------------------------------------------
# 5. Artifact Serialization
# ---------------------------------------------------------------------------
def save_artifacts(model, vectorizer, output_dir: Path) -> None:
    """Serialize model and vectorizer to disk via joblib."""
    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / "model.pkl"
    vec_path = output_dir / "vectorizer.pkl"

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vec_path)

    print(f"\n💾  Artifacts saved:")
    print(f"    Model      → {model_path}")
    print(f"    Vectorizer → {vec_path}")
    print(f"    Model size : {model_path.stat().st_size / 1024:.1f} KB")
    print(f"    Vec size   : {vec_path.stat().st_size / (1024*1024):.1f} MB")


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------
def main():
    print("\n🚀  VeriVibe ML Training Pipeline")
    print("─" * 40)

    # 1. Load
    df = load_data(DATA_DIR)
         
    # 2. Preprocess
    print("\n⏳  Preprocessing text...")
    df["text"] = df["text"].apply(preprocess)

    # 3. Vectorize
    print("⏳  Building TF-IDF features...")
    vectorizer = build_vectorizer()
    X = vectorizer.fit_transform(df["text"])
    y = df["label"]
    print(f"    Feature matrix shape: {X.shape}")

    # 4. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"    Train: {X_train.shape[0]:,}  |  Test: {X_test.shape[0]:,}")

    # 5. Train
    print("\n⏳  Training Logistic Regression...")
    model = train_model(X_train, y_train)

    # 6. Evaluate
    acc = evaluate(model, X_test, y_test)

    if acc < 0.90:
        print("\n⚠️  WARNING: Accuracy below 90% target. Consider tuning hyperparameters.")

    # 7. Save
    save_artifacts(model, vectorizer, MODEL_DIR)

    print("\n✅  Pipeline complete!\n")


if __name__ == "__main__":
    main()
