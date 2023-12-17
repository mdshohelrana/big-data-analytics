from flask import Flask, jsonify
import pandas as pd
import re
from datetime import datetime, timedelta
import random
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import os
from collections import Counter

# Initialize Flask app
app = Flask(__name__)

# Setting up the relative path for the JSON file
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, 'data', 'data_503986.json')

# NLTK downloads
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Sentiment Intensity Analyzer
sid = SentimentIntensityAnalyzer()

# Load and preprocess data at startup
df = pd.read_json(file_path)

def pre_process(text):
    # Preprocessing steps
    text = re.sub('http[s]?://\\S+', '', text)  # Remove URLs
    text = re.sub('@\\w+', '', text)  # Remove mentions
    text = re.sub('#\\w+', '', text)  # Remove hashtags
    text = re.sub('[^a-zA-Z]', ' ', text)  # Remove special characters
    text = re.sub('\\s+', ' ', text)  # Remove extra spaces
    text = text.lower().strip()  # Convert to lowercase
    return text

# Apply preprocessing to the tweet text
df['processed_text'] = df['text'].apply(pre_process)

# Simulate a 'date' column for the last two months
start_date = datetime.now() - timedelta(days=60)
df['date'] = [start_date + timedelta(days=random.randint(0, 60)) for _ in range(len(df))]


def sentiment_analysis(text):
    # Add your sentiment analysis code here
    return {"neg": 0.0, "neu": 0.0, "pos": 0.0, "compound": 0.0}

# API Endpoints
@app.route('/api/tweet_volume_per_day')
def tweet_volume_per_day():
    # Group by date and count tweets
    tweet_volume = df.groupby('date').size().reset_index(name='tweet_count')
    result = tweet_volume.to_dict(orient='records')

    return jsonify(result)

@app.route('/api/top_5_words')
def top_5_words():
    # Flatten the list of words in all tweets
    words = [word for tweet in df['processed_text'] for word in tweet.split()]
    
    # Count the frequency of each word
    word_counts = Counter(words)

    # Get the top 5 most common words
    top_words = word_counts.most_common(5)

    # Format the result for JSON serialization
    result = [{'word': word, 'count': count} for word, count in top_words]

    return jsonify(result)

@app.route('/api/sentiment_distribution')
def sentiment_distribution():
    # Apply sentiment analysis to each tweet
    df['sentiments'] = df['processed_text'].apply(lambda text: sentiment_analysis(text))

    # Aggregate sentiment counts
    sentiment_counts = df['sentiments'].apply(lambda x: 'positive' if x['compound'] > 0.05 
                                              else 'negative' if x['compound'] < -0.05 
                                              else 'neutral').value_counts().to_dict()

    # Format the result for JSON serialization
    result = [{'sentiment': k, 'count': v} for k, v in sentiment_counts.items()]
    return jsonify(result)


# @app.route('/api/tweet_volume_by_hour')
# def tweet_volume_by_hour():
#     df = read_data()
#     # Add processing code for tweet volume by hour
#     return jsonify(result)

# @app.route('/api/sentiment_trend_over_time')
# def sentiment_trend_over_time():
#     df = read_data()
#     # Add processing code for sentiment trend over time
#     return jsonify(result)

# @app.route('/api/top_hashtags_used')
# def top_hashtags_used():
#     df = read_data()
#     # Add processing code for top hashtags used
#     return jsonify(result)

# @app.route('/api/word_cloud_data')
# def word_cloud_data():
#     df = read_data()
#     # Add processing code for word cloud data
#     return jsonify(result)

# @app.route('/api/detailed_sentiment_analysis_over_time')
# def detailed_sentiment_analysis_over_time():
#     df = read_data()
#     # Add processing code for detailed sentiment analysis over time
#     return jsonify(result)

# @app.route('/api/geographic_distribution_of_tweets')
# def geographic_distribution_of_tweets():
#     df = read_data()
#     # Add processing code for geographic distribution of tweets
#     return jsonify(result)

# @app.route('/api/time_series_analysis_of_tweet_volume_and_sentiment')
# def time_series_analysis_of_tweet_volume_and_sentiment():
#     df = read_data()
#     # Add processing code for time series analysis of tweet volume and sentiment
#     return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)