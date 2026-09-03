import imaplib, email, time, csv, os
from datetime import datetime

# This is running in a USB script
import sys, os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import APPS.MDLottery2 as MDLottery2, APPS.WVLottery2 as WVLottery2
import APPS.Grade_Checker_GARY_API as GC
import Pushover
from threading import Thread

from dotenv import load_dotenv
load_dotenv()

def log(message:str) -> None:
    """ Write message to log file with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('Gary/commands.log', 'a') as f:
        f.write(f'{timestamp}: {message}\n')

def check_inbox(liberator: Pushover.Pushover) -> None:
    """
    Constantly checks the inbox for unseen emails and extracts the command from the attachment. 
    And sends the command to command_run 
    """
    try:
        IMAP_USERNAME = os.environ['EMAIL_USERNAME']
        IMAP_PASSWORD = os.environ['EMAIL_PASSWORD']
    except KeyError as e:
        return log(f"Missing environment variable: {e}")

    try:
        # SIGN-IN to email server
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(IMAP_USERNAME, IMAP_PASSWORD)
        log("Successful login to email server")

        while True:
            try:
                mail.select('inbox')
                ok, inbox = mail.search(None, 'UNSEEN')
                email_list = inbox[0].split() # The list of email objects
                log(f"Found {len(email_list)} unseen emails") if len(email_list) != 0 else 0

                for m in email_list:
                    try:
                        read_email(m, mail, liberator)
                    except Exception as e:
                        log(f"Error processing email: {e}") # Error list index out of range
                        continue

            except imaplib.IMAP4.abort as e:
                log(f"IMAP connection aborted: {e}. Reconnecting...")
                try:
                    mail.close()
                    mail.logout()
                except:
                    pass

                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(IMAP_USERNAME, IMAP_PASSWORD)
                log("Reconnected to email server")
            
            except Exception as e:
                log(f"Error in email checking loop: {e}\nBe back in 5")
                time.sleep(5)

    except Exception as e:
        log(f"Critical error in check inbox: {e}")
    finally:
        # Cleanup connection
        if mail:
            try:
                mail.close()
                mail.logout()
                log("Email connection closed")
            except:
                pass

def read_email(email_id, mail, liberator: Pushover.Pushover):
    """ Process individual email and extract commands from attachments
    
    Args:
        email_id:   Email ID to fetch
        mail:       IMAP mail object
        liberator:  Liberator object for notifications
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

        if command_found and command:
            log(f'Received email from" {from_email}')
            log(f'Command: {command}')

            # Start command processing in seperate thread                
            Thread(target=search_for_commands, args=(command, liberator)).start()
        else:
            log(f"No valid command found in email from {from_email}")
    else:
        log(f"Received email from UNVERIFIED user: {from_email}")

def check_user(user: str, filename:str='Gary/user_list.csv') -> bool:
    """ Verifies the user to make sure that they are in the list of 
    user and returns True/False.

    Args:
        user (str): The email address Gary was contacted at
        filename (str, optional):   Filename of where the userlist is
    
    Returns:
        bool: True/False if the user was in the list
    
    For future features:
    Have a randomly generated questionn, for a user not in the csv.
    """
    # Checks if file exists
    if os.path.exists(filename):
        with open(filename, '+r') as outp:
            datareader = csv.reader(outp)
            for row in datareader:
                if user == row[0]:
                    return True
    
    # Creates the file if one does not exist
    else:
        with open(filename, 'w') as file:
            datawriter = csv.writer(file)
            datawriter.writerow(['Jawa'])

    return False


def search_for_commands(command: str, liberator: Pushover.Pushover) -> str:
    """ Search for commands in the input string and execute corresponding functions
    
    Args:
        command (str):  Command string to parse
        liberator:      Liberator object for sending notifications
        
    Returns:
        str: Outcome of command execution
        
    Notes:
        Later version I will build a NLP to do this later
    """
    outcome = ''
    command = command.lower().strip()
    if 'mdlottery' in command:
        liberator.send_notification('Started', 'MDLottery')
        liberator.send_notification(MDLottery2.main(), 'MDLottery')
        outcome += 'Mdlottery '

    if 'wvlottery' in command:
        liberator.send_notification('Started', 'WVLottery')
        liberator.send_notification(WVLottery2.main(), 'WVLottery')
        outcome += 'Wvlottery '

    if 'test' in command:
        liberator.send_notification('Test', 'This is just a test')
        outcome += 'Test '

    else:
        outcome += 'Command FAILED'
    return outcome

if '__main__' == __name__:
    pot = Pushover.Pushover(os.environ["SEAN_KEY"], os.environ["API_TOKEN"])
    check_inbox(pot)