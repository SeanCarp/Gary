from APPS.Grade_Checker_GARY_API import Grade_Checker, Result
from APPS.Train_API import Train
#import APPS.MDLottery3

import Pushover
from Gmail import Gmail, GmailStatus
import GaryNER, GaryIntentClassifier

from helper import *

from threading import Thread
import time, sys


def process_command(text:str, nlp, nlp_helper:GaryNER.GaryNER) -> None:
    """ This is where the intent pipeline goes"""
    doc = nlp(text)
    entities = nlp_helper.extract_entities(doc)
    result = doodle_hopper.parse_command(entities)
    print(result.message)


if '__main__' == __name__:
    # Communication Objects
    pushover = Pushover.Pushover()
    gmail = Gmail()

    # GARY's NLP (Intent/NER)
    ner_helper = GaryNER.GaryNER()
    classifier = GaryIntentClassifier.GaryIntentClassifier()
    ner = ner_helper.load_model()
    classifier.load()

    # APPs
    doodle_hopper = Grade_Checker()
    baymax = Train()

    failed_sessions = 0
    while True:
        if failed_sessions > 1:
            pushover.send_notification("Total System failure. Needs immedimate attention", 1)
            log("System", "CRITICAL: Total system failure. Unable to connect to SMTP")
            sys.exit(0)
    
        status = gmail.sign_in()
        if status == GmailStatus.ERROR_CONNECTION:
            pushover.send_notification("Three consecutive failed SMTP sign-in attempts. \
                                       Will try again in 1 hour.", "G-Mail Failed Sign-in", 1)
            time.sleep(60 * 60)
            failed_sessions += 1
            continue

        try:
            while True:
                responses = gmail.check_inbox()
                for res in responses:
                    if res["status"] == GmailStatus.EMPTY:
                        time.sleep(10) # Avoids 100% CPU usage

                    if res['status'] == GmailStatus.MAIL:
                        command = res['payload']
                        print(f"Executing: {command}")

                        # MAIN CODE LOGIC
                        log("Command", f"INFO: Command: '{command}'")

                        # TODO: Intent
                        intent = classifier.predict(command)
                        print("Intent:", intent)

                        # TODO: NER
                        doc = ner(command)
                        entities = ner_helper.extract_entities(doc)

                        # TODO: EXECUTE
                        if intent == "grade_checker":
                            result = doodle_hopper.parse_command(entities)
                            log("Result", f"{result.success}: {result.message}. Additional: {result.data}")
                            pushover.send_notification("Grade Checker", result.message)

                        elif intent == "train":
                            result = baymax.train()
                            pushover.send_notification("Train", result.message)
                        else:
                            pushover.send_notification(f"Intent FAIL: {intent}", command)

                        # TODO: RESPONSED
                        #pushover.send_notification("Grade Checker", command)


        except Exception as e:
            log("Gmail", f"WARNING: Work loop interrupted (likely connection drop): {e}")


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