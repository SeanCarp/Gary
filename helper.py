# These are helper functions that are used for GARY

from datetime import datetime


def log(title:str, message:str) -> None:
    """ 
    Write message to log file with timestamp.
    Only writes for off nominal cases.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date = datetime.now().strftime('%Y-%m-%d')
    with open(f'Gary_log/{title}/{date}_message.log', 'a') as f:
        if "DEBUG" not in message:
            f.write(f'{timestamp}: {message}\n')
        print(f'{timestamp}: {message}\n')