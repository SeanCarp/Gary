import imaplib, email, os
from dotenv import load_dotenv  # pip install dotenv

from helper import *

class Gmail:
    IMAP_USERNAME = None
    IMAP_PASSWORD = None
    mail = None
    
    def __init__(self) -> None:
        try:
            # 1. Configuration/Secrets and Retrieval
            load_dotenv()
            self.IMAP_USERNAME = os.environ['EMAIL_USERNAME']
            self.IMAP_PASSWORD = os.environ['EMAIL_PASSWORD']
        except KeyError as e:
            return log("Gmail", f"CRITICAL: Missing environment variable: {e}")
        

    def sign_in(self) -> imaplib.IMAP4_SSL | None:
        """ 
        This attempts to sign-in into gmail.
        Returns:
            imaplib.IMAP4_SSL - mail object
            None - if attempt failed
        """
        try:
            # 2. Inital Connection and Log-in
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.IMAP_USERNAME, self.IMAP_PASSWORD)
            log("Gmail", "INFO: Successful login to email server")
            self.mail = mail
            return mail
        
        except Exception as e:
            log("Gmail", f"CRITICAL: Critical error in check_inbox or during initial login/reconnect: {e}")
            return None


    def sign_out(self) -> None:
        """
        Closes out the connection of the mail object.
        """
        try:
            self.mail.close()
            self.mail.logout()
            log("Gmail", "Email connection closed.")
        except:
            log("Gmail", "Email sign-out failed.")


    def check_inbox(self) -> dict[str, str|None]:
        # TODO: These should be enums not dicts
        """
        Checks for unseen emails, marks them as read and returns the text and attachment
        Args:
            mail (imaplib.IMAP4_SSL) - mail object
        Returns:
            (str, object) - string is text/command sent, object is the attachment in the message.
        """
        try:
            self.mail.select('inbox')
            ok, inbox = self.mail.search(None, 'UNSEEN')
            email_list = inbox[0].split() # The list of email objects

            if email_list:
                log("Gmail", f"INFO: Found {len(email_list)} unseen emails. Processing...")

                for m in email_list:
                    try:
                        return read_email(m, self.mail)
                    
                    except IndexError as e:
                        log("Gmail", f"ERROR: Email processing failed (IndexError, likely bad message format): {e}")
                        return {"status": "ERROR ()"}
                    except Exception as e:
                        log("Gmail", f"ERROR: Unexpected error processing email: {e}")
                        return {"status": "ERROR (Unexpected)"}
            else:
                log("Gmail", "DEBUG: No unseen emails found.")
                return {"status": "EMPTY"}

        except imaplib.IMAP4.abort as e:
            log("Gmail", f"WARNING: IMAP connection aborted: {e}. Try reconnecting.")
            return {"status": "ERROR (Connection)"} 
        

def read_email(email_id:str, mail: imaplib.IMAP4_SSL) -> str:
    """ 
    Process individual email and extract commands from attachments
    Args:
        email_id (str) - Email ID to fetch
        mail (imaplib.IMAP4_SSL) - IMAP mail object
    Returns:
        str - string is text/command sent, object is the attachment in the message.
    """
    ok, data = mail.fetch(email_id, '(RFC822)')
    raw_email_string = data[0][1].decode('utf-8') # Not sure what this gets rid
    email_message = email.message_from_string(raw_email_string)
    from_email = email_message['from'] # Extracts FROM

    if check_user(from_email): # Checks if verified user
        log("Gmail", f"Processing email from verified user: {from_email}")
        command_found = False

        for part in email_message.walk():
            # Skip multipart containers
            if part.get_content_maintype() == 'multipart' or \
                part.get('Content-Disposition') is None: 
                continue
    
            fileName = part.get_filename()
            if fileName is not None and '.txt' in fileName.lower():
                try:
                    command = part.get_payload(decode=True).decode('utf-8').strip()
                    command_found = True
                    log("Gmail", f"Command extract from: {command}\n")
                    break
                except UnicodeDecodeError as e:
                    log("Gmail", f"Failed to decode attachment {fileName}: {e}")

        if command_found and command:   # Command_found seems redundant
            log("Gmail", f'Received email from" {from_email}')
            log("Gmail", f'Command: {command}')
            return {"status": "MAIL", "payload": command}
        
        else:       # Not sure this ever gets triggered
            log("Gmail", f"No valid command found in email from {from_email}")
            return {"status": "ERROR (Invalid Command)"}

    else:        # This might send notifications latter
        log("Gmail", f"Received email from UNVERIFIED user: {from_email}")
        return {"status": "ERROR (Unverified User)"}

def check_user(user: str, filename:str='Gary_log/user_list.txt') -> bool:
    """ Verifies the user to make sure that they are in the list of 
    user and returns True/False.

    Args:
        user (str): The email address Gary was contacted at
        filename (str, optional):   Filename of where the userlist is
    
    Returns:
        bool: True/False if the user was in the list
    
    For future features:
    Have a randomly generated question, for a user not in the text file.
    """
    # Checks if file exists
    if os.path.exists(filename):
        with open(filename, '+r') as outp:
            for row in outp:
                if user == row:
                    return True
    
    # Creates the file if one does not exist
    else:
        with open(filename, 'w') as file:
            file.write('Jawa\n')

    return False