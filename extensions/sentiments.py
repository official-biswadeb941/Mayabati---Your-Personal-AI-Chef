# sentiment_analysis.py
from textblob import TextBlob

def analyze_sentiment(message):
    """
    Analyze the sentiment of the given message using TextBlob.
    :param message: The text to analyze.
    :return: A string representing sentiment (e.g., 'positive', 'negative', 'neutral').
    """
    blob = TextBlob(message)
    sentiment_score = blob.sentiment.polarity

    if sentiment_score > 0:
        return 'positive'
    elif sentiment_score < 0:
        return 'negative'
    else:
        return 'neutral'
