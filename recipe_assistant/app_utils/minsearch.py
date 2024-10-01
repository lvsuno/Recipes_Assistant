import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
from tqdm.auto import tqdm

import numpy as np

def index_vec_doc(doc, model, fields):

    combined = ''
    for field in fields:
        combined = combined + doc[field] + " "

    return model.encode(combined).tolist()


def par_indexing (documents,fields, model) :
    executor = ThreadPoolExecutor(8)
    results = []

    with tqdm(total=len(documents)) as progress:
            futures = []
            for doc in documents:
                future = executor.submit(index_vec_doc, doc, model, fields)
                # attaches a callback to the future that will update
                # the progress bar each time a task is completed
                future.add_done_callback(lambda p: progress.update())
                futures.append(future)
            for future in futures:
                # The code waits for each future to complete by calling future.result().
                # This call  will block until the task is finished, and
                # then it retrieves the result.
                result = future.result()
                results.append(result)
    return np.array(results)

class Index:
    """
    A simple search index using TF-IDF and cosine similarity for text fields and exact matching for keyword fields.

    Attributes:
        text_fields (list): List of text field names to index.
        keyword_fields (list): List of keyword field names to index.
        vectorizers (dict): Dictionary of TfidfVectorizer instances for each text field.
        keyword_df (pd.DataFrame): DataFrame containing keyword field data.
        text_matrices (dict): Dictionary of TF-IDF matrices for each text field.
        docs (list): List of documents indexed.
    """

    def __init__(self, text_fields, keyword_fields, type='text', vectorizer_params={}, model=None):
        """
        Initializes the Index with specified text and keyword fields.

        Args:
            text_fields (list): List of text field names to index.
            keyword_fields (list): List of keyword field names to index.
            vectorizer_params (dict): Optional parameters to pass to TfidfVectorizer.
        """
        self.text_fields = text_fields
        self.type = type

        if type == 'text':
            self.keyword_fields = keyword_fields
            self.vectorizers = {field: TfidfVectorizer(**vectorizer_params)
                                for field in text_fields}
            self.keyword_df = None
            self.text_matrices = {}
            self.docs = []
        elif type == 'vector':
            self.keyword_fields = keyword_fields
            self.model = model
            self.keyword_df = None
            self.vector_matrices = []
            self.docs = []
        elif type == 'hybrid':
            self.keyword_fields = keyword_fields
            self.vectorizers = {field: TfidfVectorizer(**vectorizer_params)
                                for field in text_fields}
            self.keyword_df = None
            self.text_matrices = {}
            self.model = model
            self.vector_matrices = []
            self.docs = []
    def fit(self, docs):
        """
        Fits the index with the provided documents.

        Args:
            docs (list of dict): List of documents to index. Each document is a dictionary.
        """
        self.docs = docs
        keyword_data = {field: [] for field in self.keyword_fields}

        if self.type == 'text':

            for field in self.text_fields:
                texts = [doc.get(field, '') for doc in docs]
                self.text_matrices[field] = self.vectorizers[field].fit_transform(texts)
        elif self.type == 'vector':
            self.vector_base = par_indexing (self.docs,self.text_fields, self.model)
        elif self.type == 'hybrid':

            for field in self.text_fields:
                texts = [doc.get(field, '') for doc in docs]
                self.text_matrices[field] = self.vectorizers[field].fit_transform(texts)
            self.vector_base = par_indexing (self.docs,self.text_fields, self.model)


        for doc in docs:
            for field in self.keyword_fields:
                keyword_data[field].append(doc.get(field, ''))

        self.keyword_df = pd.DataFrame(keyword_data)

        return self

    def search(self, query, filter_dict={}, boost_dict={}, num_results=10, hybrid_boost={'text':0.5, 'vector':0.5}):
        """
        Searches the index with the given query, filters, and boost parameters.

        Args:
            query (str): The search query string.
            filter_dict (dict): Dictionary of keyword fields to filter by. Keys are field names and values are the values to filter by.
            boost_dict (dict): Dictionary of boost scores for text fields. Keys are field names and values are the boost scores.
            num_results (int): The number of top results to return. Defaults to 10.

        Returns:
            list of dict: List of documents matching the search criteria, ranked by relevance.
        """
        if self.type == 'text':
            query_vecs = {field: self.vectorizers[field].transform([query]) for field in self.text_fields}
            scores = np.zeros(len(self.docs))

            # Compute cosine similarity for each text field and apply boost
            for field, query_vec in query_vecs.items():
                sim = cosine_similarity(query_vec, self.text_matrices[field]).flatten()
                boost = boost_dict.get(field, 1)
                scores += sim * boost

        if self.type == 'vector':
            query_vec = self.model.encode(query).reshape(1, -1)
            scores = np.zeros(len(self.docs))

            # Compute cosine similarity for each text field and apply boost
            scores = cosine_similarity(query_vec, self.vector_base).flatten()

        if self.type == 'hybrid':
            query_vecs = {field: self.vectorizers[field].transform([query])
                          for field in self.text_fields}
            scores = np.zeros(len(self.docs))

            # Compute cosine similarity for each text field and apply boost
            for field, query_vec in query_vecs.items():
                sim = cosine_similarity(query_vec, self.text_matrices[field]).flatten()
                boost = boost_dict.get(field, 1)
                scores += sim * boost

            query_vec = self.model.encode(query).reshape(1, -1)

            # Compute cosine similarity for each text field and apply boost
            scores = hybrid_boost.get('text')*scores + hybrid_boost.get('vector') * cosine_similarity(query_vec, self.vector_base).flatten()


        # Apply keyword filters
        for field, value in filter_dict.items():
            if field in self.keyword_fields:
                mask = self.keyword_df[field] == value
                scores = scores * mask.to_numpy()

        # Use argpartition to get top num_results indices
        top_indices = np.argpartition(scores, -num_results)[-num_results:]
        top_indices = top_indices[np.argsort(-scores[top_indices])]

        # Filter out zero-score results
        top_docs = [self.docs[i] for i in top_indices if scores[i] > 0]

        return top_docs
