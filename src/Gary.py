from APPS.Grade_Checker_GARY_API import Grade_Checker, Result
from APPS.Train_API import Train
from APPS.Scrape_API import Scrape

import Pushover
from Gmail import Gmail, GmailStatus
import GaryNER, GaryIntentClassifier

from helper import *

from threading import Thread
import time, sys

def process_results(results, module_name):
    """Uniformly logs and notifies for single or multiple Results."""
    if not isinstance(results, list):
        results = [results]
    
    for res in results:
        data_str = f". Additional: {res.data}" if res.data else ""
        log("Results", f"{res.success}: {res.message}{data_str}")

        pushover.send_notification(res.message, module_name)


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
    walle = Scrape()

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

                        # MAIN CODE LOGIC
                        log("Command", f"INFO: Command: '{command}'")

                        intent = classifier.predict(command)
                        log("Command", f"INFO: Intent: '{intent}'")

                        doc = ner(command)
                        entities = ner_helper.extract_entities(doc)

                        # TODO: EXECUTE
                        if intent == "grade_checker":
                            results = doodle_hopper.parse_command(entities)
                            process_results(results, "Grade Checker")

                        elif intent == "train":
                            results = baymax.train()
                            process_results(results, "Baymax Training")

                        elif intent == "scrape":
                            results = walle.parse_command(entities)
                            process_results(results, "Wall-E Scraper")

                        else:
                            log("System", f"Intent FAIL: {intent} for command: {command}")
                            pushover.send_notification(f"Intent FAIL: {intent}", command)

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