import json, os

def load_training_data(file, intent_name):
    """Load existing training data or return empty list."""

    if not os.path.exists(file):
        return []
    
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_training_data(file, data):
    """Save updated training data."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_train_examples(new_examples: list, training_file, intent_name):
    data = load_training_data(TRAINING_FILE)
    exisiting_texts = {item["text"].strip().lower() for item in data}

   
    new_entries = []
    for phrase in new_examples:
        if phrase.strip().lower() not in exisiting_texts:
            new_entries.append({
                "text": phrase,
                "entities": [],
                "intent": INTENT_NAME
            })

    if not new_entries:
        print("No new entries to add (all duplicates.)")
        return
    
    data.extend(new_entries)
    save_training_data(TRAINING_FILE, data)
    print(f"Added {len(new_entries)} new training examples.")
    print(f"Total training samples: {len(data)}")
    

if __name__ == "__main__":
    TRAINING_PATH = "Brain/training_data"

    INTENT_NAME = "train"
    TRAINING_FILE = TRAINING_PATH + "/" + INTENT_NAME + ".json"

    new_train_commands = input("Please enter new commands").split("\n")
    new_train_commands = """Run scheduled retraining.
Start the weekly retrain job.
Trigger the retrain pipeline.
Run the training pipeline again.
Start the model update job.
Deploy a newly trained model.
Train a fresh model version.""".split("\n")
    
    add_train_examples(new_train_commands, training_file=TRAINING_FILE, intent_name=INTENT_NAME)