import logging
import re
from pathlib import Path

import joblib

logger = logging.getLogger(__name__)

# Paths
MODEL_DIR = Path(__file__).resolve().parent / "models"


class MLHandler:
    """Singleton for pre-loading models to ensure lightning-fast prediction."""

    _instance = None
    _model = None
    _vectorizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLHandler, cls).__new__(cls)
            cls._instance._load_artifacts()
        return cls._instance

    def _load_artifacts(self):
        """Load model and vectorizer at startup."""
        model_path = MODEL_DIR / "model.pkl"
        vec_path = MODEL_DIR / "vectorizer.pkl"

        try:
            self._model = joblib.load(model_path)
            self._vectorizer = joblib.load(vec_path)
            logger.info("✅ ML artifacts loaded successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to load ML artifacts: {e}")
            raise RuntimeError(
                f"Missing model files in {MODEL_DIR}. Did you run train_model.py?"
            ) from e

    def preprocess(self, text: str) -> str:
        """
        Clean the input text mimicking the training pipeline:
          - Lowercase
          - Strip punctuation and digits
        """
        text = text.lower()
        text = re.sub(r"[^a-z\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def predict(self, text: str) -> dict:
        """
        Run inference on a single string of text.

        Returns:
            dict: { "vibe_score": float (0-100), "prediction": str }
        """
        # 1. Clean the input text
        clean_text = self.preprocess(text)

        # 2. Transform the text into TF-IDF vector features based on training vocabulary
        #    This ignores words not seen in training and uses the pre-computed stop-words.
        X = self._vectorizer.transform([clean_text])

        # 3. Predict the probability of the positive class (Real = 1)
        #    predict_proba returns [[P(class=0), P(class=1)]]
        probs = self._model.predict_proba(X)[0]
        prob_real = float(probs[1])

        # 4. Map probability to our domain logic
        #    If probability > 50%, it's "Reliable"
        predicted_class = "Reliable" if prob_real >= 0.50 else "Unreliable"

        #    Convert the raw probability to a user-friendly 0-100 "Vibe Score" 
        #    (We use the score of the *predicted* class)
        vibe_score = (prob_real if predicted_class == "Reliable" else probs[0]) * 100.0

        return {
            "prediction": predicted_class,
            "vibe_score": round(vibe_score, 1),
        }


# Export a ready-to-use singleton instance
ml_handler = MLHandler()
