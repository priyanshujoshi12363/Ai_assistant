import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import re

daily_pairs = []
try:
    df_daily = pd.read_csv('train.csv')
    for idx, row in df_daily.iterrows():
        utterances = re.findall(r"'([^']*)'", str(row['dialog']))
        for i in range(len(utterances) - 1):
            user = utterances[i].strip().replace('"', '').replace("'", "")
            assistant = utterances[i+1].strip().replace('"', '').replace("'", "")
            if len(user) > 5 and len(assistant) > 5:
                daily_pairs.append({'user': user, 'assistant': assistant})
        if len(daily_pairs) >= 1000:
            break
except:
    daily_pairs = []

assistant_data = [
    ["hello", "Hello! How can I help you today?"],
    ["hi", "Hi there! Nice to meet you."],
    ["hey", "Hey! What's up?"],
    ["good morning", "Good morning! How are you today?"],
    ["how are you", "I'm doing great, thanks for asking! How about you?"],
    ["what's your name", "I'm your voice assistant! You can call me Assistant."],
    ["who are you", "I'm an AI assistant built with machine learning to help you."],
    ["what can you do", "I can answer questions, tell jokes, have conversations, and keep you company!"],
    ["tell me a joke", "Why don't scientists trust atoms? Because they make up everything!"],
    ["i'm sad", "I'm sorry to hear that. Want to talk about what's bothering you?"],
    ["i'm happy", "That's awesome! Happiness looks good on you!"],
    ["i'm bored", "Let's fix that! Want to hear a joke or talk about something interesting?"],
    ["goodbye", "Goodbye! Take care and come back soon!"],
    ["bye", "Bye! It was nice chatting with you."],
    ["thank you", "You're welcome! Always happy to help."],
    ["thanks", "Anytime! That's what I'm here for."],
    ["fuck you", "Let's keep our conversation respectful and helpful. How can I assist you?"],
]


all_pairs = daily_pairs[:1000]
for user, assistant in assistant_data:
    all_pairs.append({'user': user, 'assistant': assistant})
    all_pairs.append({'user': user + "?", 'assistant': assistant})
    all_pairs.append({'user': user + "!", 'assistant': assistant})

df = pd.DataFrame(all_pairs)

vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X = vectorizer.fit_transform(df['user'])

joblib.dump(vectorizer, 'vectorizer.pkl')
joblib.dump({
    'vectors': X,
    'responses': df['assistant'].tolist()
}, 'brain.pkl')

print(f"✅ Model trained on {len(df)} conversations")