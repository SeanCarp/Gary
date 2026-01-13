import imaplib, email, os
from datetime import datetime
from dotenv import load_dotenv  # pip install dotenv

def log(message:str) -> None:
    """ 
    Write message to log file with timestamp.
    Only writes for off nominal cases.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date = datetime.now().strftime('%Y-%m-%d')
    with open(f'Gary/{date}_commands.log', 'a') as f:
        if "DEBUG" not in message:
            f.write(f'{timestamp}: {message}\n')
        print(f'{timestamp}: {message}\n')


def sign_in() -> imaplib.IMAP4_SSL | None:
    """ 
    This attempts to sign-in into gmail.
    Returns:
        imaplib.IMAP4_SSL - mail object
        None - if attempt failed
    """
    try:
        # 1. Configuration/Secrets and Retrieval
        load_dotenv()
        IMAP_USERNAME = os.environ['EMAIL_USERNAME']
        IMAP_PASSWORD = os.environ['EMAIL_PASSWORD']
    except KeyError as e:
        return log(f"CRITICAL: Missing environment variable: {e}")

    try:
        # 2. Inital Connection and Log-in
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(IMAP_USERNAME, IMAP_PASSWORD)
        log("INFO: Successful login to email server")
        return mail
    
    except Exception as e:
        log(f"CRITICAL: Critical error in check_inbox or during initial login/reconnect: {e}")
        return None


def sign_out(mail: imaplib.IMAP4_SSL) -> None:
    """
    Closes out the connection of the mail object.
    """
    try:
        mail.close()
        mail.logout()
        log("Email connection closed.")
    except:
        log("Email sign-out failed.")


def check_inbox(mail:imaplib.IMAP4_SSL) -> dict[str, str|None]:
    # TODO: These should be enums not dicts
    """
    Checks for unseen emails, marks them as read and returns the text and attachment
    Args:
        mail (imaplib.IMAP4_SSL) - mail object
    Returns:
        (str, object) - string is text/command sent, object is the attachment in the message.
    """
    try:
        mail.select('inbox')
        ok, inbox = mail.search(None, 'UNSEEN')
        email_list = inbox[0].split() # The list of email objects

        if email_list:
            log(f"INFO: Found {len(email_list)} unseen emails. Processing...")

            for m in email_list:
                try:
                    return read_email(m, mail)
                
                except IndexError as e:
                    log(f"ERROR: Email processing failed (IndexError, likely bad message format): {e}")
                    return {"status": "ERROR ()"}
                except Exception as e:
                    log(f"ERROR: Unexpected error processing email: {e}")
                    return {"status": "ERROR (Unexpected)"}
        else:
            log("DEBUG: No unseen emails found.")
            return {"status": "EMPTY"}

    except imaplib.IMAP4.abort as e:
        log(f"WARNING: IMAP connection aborted: {e}. Try reconnecting.")
        return {"status": "ERROR (Connection)"} 
    
def read_email(email_id:str, mail:imaplib.IMAP4_SSL) -> str:
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
        log(f"Processing email from verified user: {from_email}")
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
                    log(f"Command extract from: {command}\n")
                    break
                except UnicodeDecodeError as e:
                    log(f"Failed to decode attachment {fileName}: {e}")

        if command_found and command:   # Command_found seems redundant
            log(f'Received email from" {from_email}')
            log(f'Command: {command}')
            return {"status": "MAIL", "payload": command}
        
        else:       # Not sure this ever gets triggered
            log(f"No valid command found in email from {from_email}")

    else:        # This might send notifications latter
        log(f"Received email from UNVERIFIED user: {from_email}")

def check_user(user: str, filename:str='Gary/user_list.txt') -> bool:
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


if '__main__' == __name__:
    load_dotenv()
    check_inbox()