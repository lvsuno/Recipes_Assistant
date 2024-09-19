import functools
import logging
import smtplib
import time
import traceback
from email.mime.text import MIMEText
import streamlit as st
from typing import Iterable
from pathlib import Path


ROOT_PATH: Path = Path(".").resolve()
WRK_PATH: Path = ROOT_PATH/"recipe_assistant"

# data
DATA_FILE: Path = ROOT_PATH/"data/data.csv"
DATA_IMAGES_PATH: Path = ROOT_PATH/"data/Food_Images/"
GROUND_TRUTH_FILE: Path = ROOT_PATH/"data/ground-truth-data.csv"


# ========= Chat Bot =============
# Assets
BOT_AVATAR_FILE: Path = WRK_PATH/"assets/logo.png"
BOT_DISCLAIMER_FILE: Path = WRK_PATH/"assets/disclaimer.md"


def stream_text(response: str, sleep: float = 0.05) -> Iterable[str]:
    for word in response.split(" "):
        yield word + " "
        time.sleep(sleep)


# retry to connect to a source
def retry(max_tries=3, delay_seconds=1):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            tries = 0
            while tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    tries += 1
                    if tries == max_tries:
                        raise e
                    time.sleep(delay_seconds)

        return wrapper_retry

    return decorator_retry


# timing  a function

def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time} seconds to run.")
        return result

    return wrapper


# Logging decorators to print functions log

logging.basicConfig(level=logging.INFO)

def log_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Executing {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"Finished executing {func.__name__}")
        return result

    return wrapper



def email_on_failure(sender_email, password, recipient_email):
    """
    Notification decorator: Send an email whenever the execution of inner function fails
    it can be a Teams/slack notification or anyone. 
   """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # format the error message and traceback
                err_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

                # create the email message
                message = MIMEText(err_msg)
                message['Subject'] = f"{func.__name__} failed"
                message['From'] = sender_email
                message['To'] = recipient_email

                # send the email
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(sender_email, password)
                    smtp.sendmail(sender_email, recipient_email, message.as_string())

                # re-raise the exception
                raise

        return wrapper

    return decorator



def session_keys(key: str | list[str], default_value=None):
    """
    Update Session Keys. 
    This can be used to update session keys after each event.
    """
    if isinstance(key, list):
        for k in key:
            session_keys(k, default_value)
    elif isinstance(key, str):
        if key not in st.session_state:
            st.session_state[key] = default_value


def is_valid_email(email):

    """
    Check if the email is valid
    """
    # Comprehensive regex for email validation
    pattern = r'''
        ^                         # Start of string
        (?!.*[._%+-]{2})          # No consecutive special characters
        [a-zA-Z0-9._%+-]{1,64}    # Local part: allowed characters and length limit
        (?<![._%+-])              # No special characters at the end of local part
        @                         # "@" symbol
        [a-zA-Z0-9.-]+            # Domain part: allowed characters
        (?<![.-])                 # No special characters at the end of domain
        \.[a-zA-Z]{2,}$           # Top-level domain with minimum 2 characters
    ''' 
    # Match the entire email against the pattern
    return re.match(pattern, email, re.VERBOSE) is not None
