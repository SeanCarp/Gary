import os
import Pushover
import Gmail

# Ask for username
message = input("Please enter message to send: ")

# Pushover API test
pushover = Pushover.Pushover()
pushover.send_notification(message, "Test")


# Gmail API test
gmail = Gmail.Gmail()
gmail.sign_in()

flag = True

import time
while flag:
    status = gmail.check_inbox()
    flag = False if status["status"] == "ERROR (Connection)" else True
    if status["status"] == "MAIL":
        print(status["payload"],"\n")


    time.sleep(5)