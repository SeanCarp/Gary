import random, json
import spacy        # pip install spacy
from pathlib import Path
from spacy.util import minibatch
from spacy.training.example import Example

# pip install cupy

class GaryNER:
    """ Gary's Named Entity Recognition system for educational command processing."""
    def __init__(self, training_data_path: str='Brain/training_data.json',
                 model_save_path: str='Brain', language: str='en'):
        self.training_data_path = training_data_path
        self.model_save_path = model_save_path
        self.language = language

    def train_model(self, iteration:int=100, batch_size:int=4, gpu_process:bool=False) -> 'spacy.Language':
        """ Train a spaCy NER model on predefined training data for entity recognitition.
        This function trains the Named Entitiy Recognition (NER) component of a spaCy language model.

        Args:
            iteration (optional, int): Num of iterations the model trains on. Defaults to 100
            batch_size (optional, int): Num of items in a batch when training. Defaults to 4. Keep powers of 2.
            gpu_process (optional, bool): Whether or not to use the GPU, it is responsbility of the user to make sure CUDA is install. Defaults to False.

        Returns:
            spacy.Lanaguage: The trained spaCy modle with updated NER weights. 
            The returned model can be used for inference or saved to disk.

        Notes:
            - Disabling pipes saves RAM and gives better speed performance
            - Training method should use ADAM as the optimizer
            - Minibatch splits training data into small batches
            - .make_doc() Tokenizations the data for us.
            - .from_dict() matches the annotations with the tokenizations
            - .update() does back propagation
        """
        try:
            with open(self.training_data_path, 'r') as f:
                train_data = json.load(f)
        except Exception as e:
            print(f"Error loading training data, {e}")
            return None
        
        # BONUS: Use GPU if asked for
        if gpu_process:
            gpu_activated = spacy.prefer_gpu()
            print(f"Using GPU: {gpu_activated}")


        # Creates the NLP object and adds NER
        nlp = spacy.blank(self.language)
        if "ner" not in nlp.pipe_names:
            ner = nlp.add_pipe("ner")
        else:
            ner = nlp.get_pipe("ner")

        # Add all labels to the NER component
        for item in train_data:
            for ent in item['entities']:
                    ner.add_label(ent[2])

        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
        with nlp.disable_pipes(*other_pipes):
            optimizer = nlp.begin_training()
            optimizer.learn_rate = 0.001 # Lower learning rate to prevent loss spikes

            for i in range(iteration):
                losses = {}
                random.shuffle(train_data)
                batches = minibatch(train_data, size=batch_size)
                
                for batch in batches:
                    examples = []
                    for item in batch:
                        text = item['text']
                        annotations = {'entities': item['entities']}
                        doc = nlp.make_doc(text)
                        example = Example.from_dict(doc, annotations)
                        examples.append(example)

                    nlp.update(examples, drop=0.5, losses=losses, sgd=optimizer)
                current_loss = losses.get('ner', 0)
                if current_loss < 0.001:
                    print(f"Stopping: Excellent loss achieved ({current_loss:.4f})")
                    break

                print(f"Losses at iteration {i+1}: {current_loss}")
        return nlp

    def save_model(self, nlp: 'spacy.Language') -> None:
        """ Save a trained spacy model to disk with error handling.
        Args:
            nlp (spacy.Language):       The trained spaCy model to save.
        """
        try:
            # Create directory if it doesn't exist
            Path(self.model_save_path).mkdir(parents=True, exist_ok=True)
            nlp.to_disk(self.model_save_path)
            print(f"\n Model saved to: {self.model_save_path}")

            model_size = sum(f.stat().st_size for f in Path(self.model_save_path).rglob('*') if f.is_file())
            print(f"📁 Model size: {model_size / (1024*1024):.2f} MB")     
        
        except Exception as e:
            print(f"Error with saving model {e}")

    def load_model(self) -> 'spacy.Language':
        """ Load a trained spaCy model from disk with comprehensive error handling.
        Returns:
            spacy.Lanaguage: The loaded spaCy model ready for inference. Contains all trained pipeline
        """
        try:
            return spacy.load(self.model_save_path)
        
        except Exception as e:
            print(f"Error with loading model {e}")

    def extract_entities(self, doc) -> dict:
        """ Convert spaCy doc.ents into a dict of label -> text single best hit)."""
        ent_map = {}
        for ent in doc.ents:
            ent_map.setdefault(ent.label_, []).append({
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char
            })
        return ent_map


if '__main__' == __name__:
    ner_helper = GaryNER()
    
    nlp = ner_helper.train_model(gpu_process=True, batch_size=16)
    ner_helper.save_model(nlp)