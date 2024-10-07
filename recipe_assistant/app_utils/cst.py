"""
Define some constants here
"""

import os

from .utils import get_env_bool_variable

# ELASTIC_URL = os.getenv("ELASTIC_URL", "http://elasticsearch:9200")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-api-key-here")
# INDEX_NAME = os.getenv('INDEX_NAME', 'recipe-questions')
INDEX_FILENAME = os.getenv('INDEX_FILENAME', 'index')
EVALUATION_MODEL = os.getenv("EVALUATION_MODEL", 'openai/gpt-4o-mini')
USE_RERANKING = get_env_bool_variable('USE_RERANKING', False)
