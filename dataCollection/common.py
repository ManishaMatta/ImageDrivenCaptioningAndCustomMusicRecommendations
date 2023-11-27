import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class CommonModule:
    @staticmethod
    def similarity_score(document1, document2):
        vectorizer = CountVectorizer()
        return cosine_similarity(vectorizer.fit_transform([document1, document2]))[0][1]
