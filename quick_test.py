import os
import Pushover
from Gmail import *

from dotenv import load_dotenv
load_dotenv()

# Ask for username
username = input("Please enter phone number: ")

# Pushover API test
pushover_api = Pushover.Pushover(os.environ["SEAN_KEY"], os.environ["API_TOKEN"])
pushover_api.send_notification("This is a quick test. No action needed.", "Test")


#test = check_inbox(pushover_api)

