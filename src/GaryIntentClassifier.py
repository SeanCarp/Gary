import pickle, json, glob, os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model  import LogisticRegression

class GaryIntentClassifier:
    def __init__(self, training_data_path: str='Brain/training_data',
                 model_path="Brain/intent.pkl"):
        self.model_path = model_path
        self.training_data_path = training_data_path
        self.vectorizer = None
        self.classifier = None

        #return self.load()

    def train(self):
        train_data = []
        try:
            file_paths = glob.glob(os.path.join(self.training_data_path, "*.json"))
            for file_path in file_paths:
                with open(file_path, 'r') as f:
                    train_data.extend(json.load(f))
        except Exception as e:
            print(f"Error laoding training data, {e}")
            return None
        
        texts = [item["text"] for item in train_data]
        labels = [item["intent"] for item in train_data]

        self.vectorizer = TfidfVectorizer(ngram_range=(1,2))
        X = self.vectorizer.fit_transform(texts)
        self.classifier = LogisticRegression(class_weight='balanced')
        self.classifier.fit(X, labels)
        print("Intent Classifier Trained")

    def predict(self, text: str) -> str:
        # Assumes that model is trained and loaded
        X = self.vectorizer.transform([text])
        return self.classifier.predict(X)[0]
    
    def save(self):
        """Serializes the vectorizer and classifier to a single file."""
        data = {
            "vectorizer": self.vectorizer,
            "classifier": self.classifier
        }

        with open(self.model_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Model succesfully saved to {self.model_path}")

    def load(self):
        """Loads the model from the disk."""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.vectorizer = data["vectorizer"]
                self.classifier = data["classifier"]
            print("Model loaded successfully.")
        else:
            print(f"No model found at {self.model_path}. Please train first.")

if '__main__' == __name__:
    intent = GaryIntentClassifier()
    intent.train()
    intent.save()
    intent.load()