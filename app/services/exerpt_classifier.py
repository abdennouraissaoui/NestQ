import os
import logging
import joblib


class ExerptClassifier:
    def __init__(self, model_config):
        """Initialize the classifier with model configuration.

        Args:
            model_config (dict): Configuration containing:
                - model_type: str, 'ann'
                - pipeline_path: str, path to the saved sklearn Pipeline
        """
        pipeline_path = model_config.get('pipeline_path')

        if not pipeline_path:
            raise ValueError("pipeline_path must be provided")

        # Load pipeline using cloudpickle instead of joblib
        with open(pipeline_path, 'rb') as f:
            self.pipeline = joblib.load(f)
        self.threshold = 0.5

    def predict(self, text):
        """Predict whether the text excerpt should be excluded.

        Args:
            text (str): The text excerpt to classify

        Returns:
            bool: True if the text should be excluded, False otherwise
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        if not text.strip():
            return False  # Return False for empty text

        try:
            probs = self.pipeline.predict_proba([text])
            return probs[0][1] > self.threshold
        except Exception as e:
            logging.error(f"Prediction error: {str(e)}")
            return False  # Default to not excluding on error

    def predict_batch(self, texts):
        """Predict whether multiple text excerpts should be excluded.

        Args:
            texts (list): List of text excerpts to classify

        Returns:
            list: List of booleans indicating whether each text should be excluded
        """
        probs = self.pipeline.predict_proba(texts)
        return [prob[1] > self.threshold for prob in probs]

    def filter_included(self, texts):
        """Filter a list of texts to keep only those that should be included.

        Args:
            texts (list): List of text excerpts to filter

        Returns:
            list: List containing only the text excerpts that should be included
        """
        if not texts:
            return []

        exclude_predictions = self.predict_batch(texts)
        return [text for text, should_exclude in zip(texts, exclude_predictions)
                if not should_exclude]


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))

    context = """
    """
    # Define model configuration
    model_config = {
        'pipeline_path': os.path.join(current_dir, "svm_filter_pipeline.pkl")
    }

    texts = context.split('\n\n')
    print("Number of excerpts", len(texts))
    # Test ANN model

    try:
        print("\nTesting SVM model:")
        classifier = ExerptClassifier(model_config)
        print("Predictions:", classifier.predict_batch(texts))
        print("Filtered texts:", classifier.filter_included(texts))
        print("Number of filtered texts:", len(classifier.filter_included(texts)))
        context_filtered = classifier.filter_included(texts)

        # Join filtered texts with a single space to create context string
        context = '\n\n'.join(context_filtered)
        print(context)
    except Exception as e:
        print(f"Error with SVM model: {str(e)}")
