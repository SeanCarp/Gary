import os
import requests                     # pip install requests
from dotenv import load_dotenv      # pip install dotenv

from helper import *

class Pushover:
    USER_KEY = None
    API_TOKEN = None

    def __init__(self) -> None:
        try:
            # 1. Configuration/Secrets and Retrieval
            load_dotenv()
            self.USER_KEY = os.environ['PUSHOVER_KEY']
            self.API_TOKEN = os.environ['PUSHOVER_API_TOKEN']
        except KeyError as e:
            log("Pushover", f"CRITICAL: Missing environment variable: {e}")


    def send_notification(self, message: str, title=None, priority:int=None) -> int:
        """
        Sends a Push notifcation with the PushOver API
        
        Parameters:
            :param message: Notification Message
            :param title: Notification title (optional)
            :param priority: Notification priority (optional)[-2, 2]"""
        
        URL = 'https://api.pushover.net/1/messages.json'
        data = {
            'user': self.USER_KEY,
            'token': self.API_TOKEN,
            'message': message,
            'title': title,
            'priority': priority
        }

        response = requests.post(URL, data=data)

        # Status RESPONSE
        # NOTE: make sure to read the documentation for the different error codes
        if response.status_code == 200:
            log("Pushover", f"INFO: Notification sent successfully. Message: {message[:20]}")
        else:
            log("Pushover", f"CRITICAL: Failed to send notification. Err: {response.text}")

        return response.status_code