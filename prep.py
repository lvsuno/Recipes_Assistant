"""
Module to index the data for search and initialize the database
"""

import os
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer
#from elasticsearch import Elasticsearch
from tqdm.auto import tqdm
from dotenv import load_dotenv

from recipe_assistant.db import init_db
from recipe_assistant.app_utils import minsearch


# To use the init_db do in terminal:
# export POSTGRES_HOST="localhost"

load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL_LOCAL")

MODEL_NAME = os.getenv("MODEL_NAME")
# INDEX_NAME = os.getenv("INDEX_NAME")
INDEX_FILENAME = os.getenv("INDEX_FILENAME")


def load_documents():
    """
    Load the documents
    """
    print("Loading documents...")
    df = pd.read_csv('../data/clean_data.csv')
    documents = df.to_dict(orient='records')
    print(f"Loaded {len(documents)} documents")
    return documents


def load_ground_truth():

    print("Loading ground truth data...")
    ground_truth_url = "../data/ground-truth-retrieval.csv"
    df_ground_truth = pd.read_csv(ground_truth_url)
    ground_truth = df_ground_truth.to_dict(orient="records")
    print(f"Loaded {len(ground_truth)} ground truth records")
    return ground_truth


def load_model():
    print(f"Loading model: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)


def index_documents(documents, model):
    """
    function to index documents
    """
    minsearch_hybrid_index = minsearch.Index(
        text_fields=['Title', 'Instructions'], # 'Cleaned_Ingredients', 'Image_Name'],
        keyword_fields=['Id'],
        model=model,
        type='hybrid'
    )
    minsearch_hybrid_index.fit(documents)
    return minsearch_hybrid_index



# def setup_elasticsearch():
#     print("Setting up Elasticsearch...")
#     print(ELASTIC_URL)
#     es_client = Elasticsearch(ELASTIC_URL, request_timeout=100)

#     index_settings = {
#         "settings": {"number_of_shards": 1, "number_of_replicas": 0},
#         "mappings": {
#             "properties": {
#                 "Title": {"type": "text"},
#                 "Instructions": {"type": "text"},
#                 "Cleaned_Ingredients": {"type": "text"},
#                 "Image_Name": {"type": "text"},
#                 "Id": {"type": "keyword"},
#                 "instr_vector": {
#                     "type": "dense_vector",
#                     "dims": 384,
#                     "index": True,
#                     "similarity": "cosine",
#                 },
#                 "ingr_vector": {
#                     "type": "dense_vector",
#                     "dims": 384,
#                     "index": True,
#                     "similarity": "cosine",
#                 },
#                 "instr_ingr_vector": {
#                     "type": "dense_vector",
#                     "dims": 384,
#                     "index": True,
#                     "similarity": "cosine",
#                 },
#             }
#         }
#     }

#     es_client.indices.delete(index=INDEX_NAME, ignore_unavailable=True)
#     es_client.indices.create(index=INDEX_NAME, body=index_settings)
#     print(f"Elasticsearch index '{INDEX_NAME}' created")
#     return es_client


# def index_documents(es_client, documents, model):
#     print("Indexing documents...")
#     for doc in tqdm(documents):
#         instructions = doc["Instructions"]
#         ingredients = doc["Cleaned_Ingredients"]
#         doc["instr_vector"] = model.encode(instructions)
#         doc["ingr_vector"] = model.encode(ingredients)
#         doc["instr_ingr_vector"] = model.encode(instructions + " " + ingredients).tolist()
#         es_client.index(index=INDEX_NAME, document=doc)
#     print(f"Indexed {len(documents)} documents")


def main():
    """
    The main function to launch indexation and database initialization
    """

    print("Starting the indexing process...")

    documents = load_documents()
    # ground_truth = load_ground_truth()
    model = load_model()
    index = index_documents (documents, model)


    with open(f'recipe_asistant/app_utils/{INDEX_FILENAME}.pkl', 'wb') as ind:
        pickle.dump(index, ind, protocol=pickle.HIGHEST_PROTOCOL)
    # es_client = setup_elasticsearch()
    # index_documents(es_client, documents, model)
    # you may consider to comment <end>

    print("Initializing database...")
    init_db()

    print("Indexing process completed successfully!")


if __name__ == "__main__":
    main()
