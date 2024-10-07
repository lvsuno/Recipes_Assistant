import os
import json
import time
import pickle
from typing import Dict

import groq
import openai
from app_utils.cst import (
    OLLAMA_URL,
    GROQ_API_KEY,
    USE_RERANKING,
    INDEX_FILENAME,
    OPENAI_API_KEY,
    EVALUATION_MODEL
)
from prompt_builder import ENTRY_TEMPLATE, PROMPT_INSTRUCTION
from app_utils.utils import (  # , replace_image_syntax
    APP_UTILS_PATH,
    DATA_IMAGES_PATH
)

# from elasticsearch import Elasticsearch
# from sentence_transformers import SentenceTransformer


with open(f'{APP_UTILS_PATH}/{INDEX_FILENAME}.pkl', 'rb') as ind:
    index = pickle.load(ind)
# es_client = Elasticsearch(ELASTIC_URL)
# model = SentenceTransformer(MODEL_NAME)


def minsearch_hybrid_rrk_improved(query: str):
    """
    Hybrid search function
    """

    boost = {
        'Title': 1.301766512843531,
        'Instructions': 0.7387164179150028,
        'text': 0.36555723393033346,
        #   'Cleaned_Ingredients': 1.3020399036175552,
        #   'Image_Name': 1.7024187651904266
    }

    text = boost.pop('text')

    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        hybrid_boost={'text': text, 'vector': 1 - text},
        reranking=USE_RERANKING,
        num_results=5,
    )

    return results


# def elastic_search_text(query,  index_name=INDEX_NAME):
#     search_query = {
#         "size": 5,
#         "query": {
#             "bool": {
#                 "must": {
#                     "multi_match": {
#                         "query": query,
#                         "fields": ["Cleaned_Ingredients^3", "Title", "Instructions"],
#                         "type": "best_fields",
#                     }
#                 },
#             }
#         },
#     }

#     response = es_client.search(index=index_name, body=search_query)
#     return [hit["_source"] for hit in response["hits"]["hits"]]


# def elastic_search_knn(field, vector, index_name=INDEX_NAME):
#     knn = {
#         "field": field,
#         "query_vector": vector,
#         "k": 5,
#         "num_candidates": 10000,
#     }

#     search_query = {
#         "knn": knn,
#         "_source": ["Image_Name", "Title", "Cleaned_Ingredients", "Instructions", "Id"],
#     }

#     es_results = es_client.search(index=index_name, body=search_query)

#     return [hit["_source"] for hit in es_results["hits"]["hits"]]


# def elastic_search_hybrid(field, query, vector, index_name=INDEX_NAME):
#     knn_query = {
#         "field": field,
#         "query_vector": vector,
#         "k": 5,
#         "num_candidates": 10000,
#         "boost": 0.5
#     }

#     keyword_query = {
#         "bool": {
#             "must": {
#                 "multi_match": {
#                     "query": query,
#                     "fields": ["Cleaned_Ingredients", "Title", "Instructions"],
#                     "type": "best_fields",
#                     "boost": 0.5,
#                 }
#             }
#         }
#     }

#     search_query = {
#         "knn": knn_query,
#         "query": keyword_query,
#         "size": 5,
#         "_source": ["Image_Name", "Title", "Cleaned_Ingredients", "Instructions", "Id"]
#     }

#     es_results = es_client.search(
#         index=index_name,
#         body=search_query
#     )

#     result_docs = []

#     for hit in es_results['hits']['hits']:
#         result_docs.append(hit['_source'])

#     return result_docs


def build_prompt(query, search_results):
    """
    Build system prompt
    """
    context = ""

    for doc in search_results:
        context = context + ENTRY_TEMPLATE.format(**doc) + "\n\n"

    return PROMPT_INSTRUCTION.format(
        question=query, context=context, DATA_IMAGES_PATH=DATA_IMAGES_PATH
    ).strip()


def llm(messages, model_choice):
    start_time = time.time()
    if model_choice.startswith('ollama/'):
        ollama_client = openai.OpenAI(base_url=OLLAMA_URL, api_key="ollama")
        response = ollama_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=messages,  # [{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens,
        }
    elif model_choice.startswith('Groq/'):
        groq_client = groq.Groq(api_key=GROQ_API_KEY)
        response = groq_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=messages,  # [{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens,
        }
    elif model_choice.startswith('openai/'):
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = openai_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=messages,  # [{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens,
        }
    else:
        raise ValueError(f"Unknown model choice: {model_choice}")
    end_time = time.time()
    response_time = end_time - start_time
    return answer, tokens, response_time


def evaluate_relevance(question, answer):
    prompt_template = """
    You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
    Your task is to analyze the relevance of the generated answer to the given question.
    Based on the relevance of the generated answer, you will classify it
    as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

    Here is the data for evaluation:

    Question: {question}
    Generated Answer: {answer}

    Please analyze the content and context of the generated answer in relation to the question
    and provide your evaluation in parsable JSON without using code blocks:

    {{
      "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
      "Explanation": "[Provide a brief explanation for your evaluation]"
    }}
    """.strip()

    prompt = prompt_template.format(question=question, answer=answer)

    evaluation, tokens, _ = llm([{"role": "user", "content": prompt}], EVALUATION_MODEL)

    try:
        json_eval = json.loads(evaluation)
        return json_eval['Relevance'], json_eval['Explanation'], tokens
    except json.JSONDecodeError:
        return "UNKNOWN", "Failed to parse evaluation", tokens


# from https://openai.com/pricing#language-models
def calculate_openai_cost(model_choice: str, tokens: Dict[str, float]) -> float:
    """
    Calculate openai cost
    """
    openai_cost = 0

    if model_choice == 'openai/gpt-3.5-turbo':
        openai_cost = (
            tokens['prompt_tokens'] * 0.0015 + tokens['completion_tokens'] * 0.002
        ) / 1000
    elif model_choice == 'openai/gpt-4o':
        openai_cost = (
            tokens['prompt_tokens'] * 0.005 + tokens['completion_tokens'] * 0.015
        ) / 1000
    elif model_choice == 'openai/gpt-4o-mini':
        openai_cost = (
            tokens['prompt_tokens'] * 0.00015 + tokens['completion_tokens'] * 0.0006
        ) / 1000
    return openai_cost


def get_answer(query: str, model_choice: str, conv_history: list[Dict[str, str]]):
    """
    Get RAG answer from query given a llm model
    """
    # if search_type == 'Vector':
    #     vector = model.encode(query)
    #     search_results = elastic_search_knn('question_text_vector', vector, course)
    # else:
    #     search_results = elastic_search_text(query, course)
    search_results = minsearch_hybrid_rrk_improved(query)
    prompt = build_prompt(query, search_results)

    # System prompt + context data
    messages: list[dict[str, str]] = [{"role": "system", "content": prompt}]

    # Add the conversation history so that the llm can keep track of conversations
    messages.extend(
        [{"role": msg["role"], "content": msg["content"]} for msg in conv_history]
    )

    answer, tokens, response_time = llm(messages, model_choice)

    # answer = replace_image_syntax(answer)

    relevance, explanation, eval_tokens = evaluate_relevance(query, answer)

    openai_cost = calculate_openai_cost(model_choice, tokens)

    return {
        'answer': answer,
        'response_time': response_time,
        'relevance': relevance,
        'relevance_explanation': explanation,
        'model_used': model_choice,
        'prompt_tokens': tokens['prompt_tokens'],
        'completion_tokens': tokens['completion_tokens'],
        'total_tokens': tokens['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
        'openai_cost': openai_cost,
    }
