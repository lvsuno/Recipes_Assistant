"""
Define some constants here
"""

import os


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


# ELASTIC_URL = os.getenv("ELASTIC_URL", "http://elasticsearch:9200")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-api-key-here")
# INDEX_NAME = os.getenv('INDEX_NAME', 'recipe-questions')
INDEX_FILENAME = os.getenv('INDEX_FILENAME', 'index')
EVALUATION_MODEL = os.getenv("EVALUATION_MODEL", 'openai/gpt-4o-mini')
USE_RERANKING = get_env_bool_variable('USE_RERANKING', False)
