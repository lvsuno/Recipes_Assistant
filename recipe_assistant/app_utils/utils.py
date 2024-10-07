import os
import re
import time
import base64
import logging
import smtplib
import functools
import traceback
from typing import Iterable
from pathlib import Path
from email.mime.text import MIMEText

import streamlit as st

ROOT_PATH: Path = Path(".").resolve()
WRK_PATH: Path = ROOT_PATH / "recipe_assistant"


# data
DATA_FILE: Path = ROOT_PATH / "data/clean_data.csv"
DATA_IMAGES_PATH: str = (
    "https://raw.githubusercontent.com/lvsuno/Recipes_Assistant/refs/heads/main/data/Food_Images/"
)
GROUND_TRUTH_FILE: Path = ROOT_PATH / "data/ground-truth-data.csv"

# util path
APP_UTILS_PATH = WRK_PATH / "app_utils"


# ========= Chat Bot =============
# Assets
BOT_AVATAR_FILE: Path = WRK_PATH / "assets/logo.png"
USER_AVATAR_FILE: Path = WRK_PATH / "assets/user_avatar.png"
BOT_DISCLAIMER_FILE: Path = WRK_PATH / "assets/disclaimer.md"


# def load_bootstrap():
#     return st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)


def get_env_bool_variable(name: str, default_value: bool | None = None) -> bool:
    """
    Get boolean envionment variables
    """

    true_ = ('true', '1', 't', 'y', 'yes', 'on')
    false_ = ('false', '0', 'f', 'n', 'no', 'off')
    value: str | None = os.getenv(name, None)
    if value is None:
        if default_value is None:
            raise ValueError(f'Variable `{name}` not set!')
        else:
            value = str(default_value)
    if value.lower() not in true_ + false_:
        raise ValueError(f'Invalid value `{value}` for variable `{name}`')
    return value in true_


def stream_text(response: str, sleep: float = 0.05) -> Iterable[str]:
    """
    Allow the text to be displayed like a streaming
    """
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


def session_keys(key: str | list[str], default_value=None) -> None:
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


def check_llm_api_key(model_choice: str) -> bool:
    """
    Check validity of the api key
    """
    if model_choice.startswith('openai/'):
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        try:
            client.models.list()
        except openai.AuthenticationError:
            st.session_state["key_val"] = check_validity
            return False
        else:
            return True
    elif model_choice.startswith('Groq/'):
        client = groq.Groq(api_key=GROQ_API_KEY)
        try:
            client.models.list()
        except groq.AuthenticationError:
            return False
        else:
            return True
    else:
        return True


# load_bootstrap()


# def img_to_bytes(img_path: str):
#     """
#     Images to bytes
#     """
#     img_bytes = Path(img_path).read_bytes()
#     encoded = base64.b64encode(img_bytes).decode()
#     return encoded


# def img_to_html(img_path: str):
#     """
#     Images to html
#     """
#     img_html = f"<img src='data:image/png;base64,{img_to_bytes(img_path)}' class='img-fluid'>"
#     return img_html


# def replace_image_syntax(text):
#     """
#     Replace any ![...] by img_to_html
#     """
#     # Define a regular expression pattern to match ![something](url)
#     pattern = r'!\[.*?\]\((.*?)\)'

#     # Replace the matched pattern with img_to_html(url)
#     replaced_text = re.sub(pattern, r'img_to_html(\1)', text)

#     return replaced_text
