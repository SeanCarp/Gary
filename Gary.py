from GaryNER import GaryNER
from APPS.Grade_Checker_GARY_API import Grade_Checker, Result
import APPS.MDLottery3

import Gmail
from threading import Thread
import time

""" For future notes I need to make it so that the NLP has better response back
to the user. I thikn this where transformers really pull ahead."""

def process_command(nlp, nlp_helper:GaryNER, text:str) -> None:
    """ This is where the intent pipeline goes"""
    doc = nlp(text)
    entities = nlp_helper.extract_entities(doc)
    print(doodle_hopper.parse_command(entities).message)


if '__main__' == __name__:
    nlp_helper = GaryNER()
    nlp = nlp_helper.load_model()

    doodle_hopper = Grade_Checker()

    # Runs infinitely
    mail = Gmail.sign_in()
    while True:
        command = Gmail.check_inbox(mail)

        if command["status"] == "ERROR (Connection)":
            mail = Gmail.sign_in()
            if not mail:
                quit("Something went really wrong")

        elif command["status"] == "EMPTY":
            time.sleep(10)  # Avoids 100% CPU usage

        elif command["status"] == "MAIL":
            # Process Command
            Thread(target=process_command, args=(nlp, nlp_helper, command["payload"]))


# doc = nlp("Add section called Finals worth 40 points to MAE411")
# entities = nlp_helper.extract_entities(doc)
# print(doodle_hopper.parse_command(entities).message)

# doc = nlp("Add grade of 34/35 to Finals in MAE411")
# entities = nlp_helper.extract_entities(doc)
# print(doodle_hopper.parse_command(entities).message)


# doc = nlp("Please all mythical GARY, show me my grades for MAE411")
# entities = nlp_helper.extract_entities(doc)
# print(doodle_hopper.parse_command(entities).message)

# doc = nlp("Delete MAE411 from my classes")
# entities = nlp_helper.extract_entities(doc)
# print(doodle_hopper.parse_command(entities).message)
# # Might not be updating the file