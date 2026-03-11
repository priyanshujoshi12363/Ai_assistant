import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
vectorizer = joblib.load('vectorizer.pkl')
brain = joblib.load('brain.pkl')
vectors = brain['vectors']
responses = brain['responses']

def ask_ai(user_text):
    user_vector = vectorizer.transform([user_text])
    
    similarities = cosine_similarity(user_vector, vectors).flatten()
    best_idx = np.argmax(similarities)
    best_score = similarities[best_idx]
    
    if best_score > 0.15:
        return responses[best_idx]
    else:
        return "That's interesting! Tell me more."