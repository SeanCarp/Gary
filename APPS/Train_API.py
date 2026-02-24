import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import GaryNER, GaryIntentClassifier, Result
class Train:
    """ This class loads all the models and then it trains them
    and saves them back for use again."""

    def __init__(self) -> None:
        """ Initialize a new Train instance and loads previous models."""
        self.ner_helper = GaryNER.GaryNER()
        self.ner = self.ner_helper.load_model()

        self.classifier = GaryIntentClassifier.GaryIntentClassifier()
        self.classifier.load()

    def train(self) -> 'Result':
        """ Trains all the available models."""
        try:
            # NER
            self.ner = self.ner_helper.train_model()
            self.ner_helper.save_model(self.ner)

            # Classifier
            self.classifier.train()
            self.classifier.save()
            return Result.Result(True, "Models trained successfully.")
        except Exception as e:
            return Result.Result(False, f"{e}: Error training models")
        
if __name__ == "__main__":
    test = Train()
    result = test.train()
    print(result.message)