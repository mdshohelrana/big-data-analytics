from flask import Flask, jsonify
import pandas as pd
import re
from datetime import datetime, timedelta
import random
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import os
from collections import Counter
import emot
import contractions
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Setting up the relative path for the JSON file
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, 'data', 'data_503986.json')
emoji_results = []

# NLTK downloads
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Sentiment Intensity Analyzer
sid = SentimentIntensityAnalyzer()

# Emoticon extraction
emot_obj = emot.core.emot()

# Load and preprocess data at startup
df = pd.read_json(file_path)

# Simulate a 'date' column for the last two months
start_date = datetime.now() - timedelta(days=60)
df['date'] = [start_date + timedelta(days=random.randint(0, 60)) for _ in range(len(df))]

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

def expand_contractions(text):
    try:
        return contractions.fix(text)
    except:
        return text

# Spam removal
to_drop = ["LP LOCKED", "accumulated 1 ETH","This guy accumulated over $100K", "help me sell a nickname", "As A Big Fuck You To The SEC", "Wanna be TOP G", "#walv", "#NFTProject", "#1000xgem", "$GALI", "NFT", "What the Soul of USA is", "#BUSD", "$FXMS", "#fxms", "#Floki", "#FLOKIXMAS", "#memecoin", "#lowcapgem", "#frogxmas", "Xmas token", "crypto space", "Busd Rewards", "TRUMPLON", "NO PRESALE", "#MIKOTO", "$HATI", "$SKOLL", "#ebaydeals", "CHRISTMAS RABBIT", "@cz_binance", "NFT Airdrop", "#NFT"]
df = df[~df['text'].str.contains('|'.join(to_drop))]

# Expand contractions and preprocess text
df['expanded_text'] = df['text'].apply(expand_contractions)
df['processed_text'] = df['expanded_text'].apply(pre_process)

def extract_emoticons(text):
    res = emot_obj.emoji(text)
    return res['value']

df['emoticons'] = df['text'].apply(extract_emoticons)

def sentiment_analysis(text):
    return sid.polarity_scores(text)

# Apply preprocessing and sentiment analysis
df['processed_text'] = df['text'].apply(pre_process)
df['sentiments'] = df['processed_text'].apply(sentiment_analysis)
df['compound_sentiment'] = df['sentiments'].apply(lambda x: x['compound'])

# Simulate engagement_count and impressions_count based on sentiment
df['engagement_count'] = df['sentiments'].apply(lambda x: np.random.randint(1, 100) if x['compound'] > 0 else np.random.randint(1, 50))
df['impressions_count'] = df['engagement_count'] * np.random.uniform(1.5, 3.0)

# API Endpoints
@app.route('/api/tweet_volume_per_day')
def tweet_volume_per_day():
    # Group by date and count tweets
    tweet_volume = df.groupby('date').size().reset_index(name='tweet_count')
    result = tweet_volume.to_dict(orient='records')

    return jsonify(result)

@app.route('/api/top_emojis')
def top_5_emojis():
    global emoji_results
    
    if not emoji_results:
        # Combine and count emoticons
        combined_counts = sum(df['emoticons'].apply(lambda x: Counter(x)), Counter())
        sorted_emoji_dict = dict(sorted(combined_counts.items(), key=lambda x: x[1], reverse=True))

        # Select top 20 emojis and create a DataFrame
        top_emojis = {k: v for i, (k, v) in enumerate(sorted_emoji_dict.items()) if i < 20}
        df_emojis = pd.DataFrame(list(top_emojis.items()), columns=['Emojis', 'Count'])

        # Modify specific emojis if necessary
        df_emojis.at[5, 'Emojis'] = '❤️'
        df_emojis.at[6, 'Emojis'] = '🤡'

        result = df_emojis.to_dict(orient='records')
        emoji_results = result;

    return jsonify(result)

@app.route('/api/sentiment_distribution')
def sentiment_distribution():
    # Aggregate sentiment counts
    sentiment_counts = df['sentiments'].apply(lambda x: 'positive' if x['compound'] > 0.05 
                                              else 'negative' if x['compound'] < -0.05 
                                              else 'neutral').value_counts().to_dict()

    # Format the result for JSON serialization
    result = [{'sentiment': k, 'count': v} for k, v in sentiment_counts.items()]
    return jsonify(result)

@app.route('/api/time_series_analysis_of_tweet_volume_and_sentiment')
def time_series_analysis_of_tweet_volume_and_sentiment():
    # Group by date and aggregate compound sentiment scores and count tweets
    time_series_data = df.groupby('date').agg({'compound_sentiment': 'mean', 'text': 'count'}).reset_index()
    time_series_data.rename(columns={'text': 'tweet_count', 'compound_sentiment': 'average_sentiment'}, inplace=True)

    # Convert to a format suitable for JSON serialization
    result = time_series_data.to_dict(orient='records')
    return jsonify(result)

@app.route('/api/average_tweet_volume_per_hour')
def average_tweet_volume_per_hour():
    # Convert 'date' to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])

    # Extract hour from the date
    df['hour'] = df['date'].dt.hour

    # Group by hour and count tweets, then calculate the average count per hour
    average_volume = df.groupby('hour').size().reset_index(name='tweet_count')
    average_volume['average_tweet_count'] = average_volume['tweet_count'] / len(df['date'].dt.date.unique())

    # Drop the original tweet count column
    average_volume.drop('tweet_count', axis=1, inplace=True)

    # Convert to a format suitable for JSON serialization
    result = average_volume.to_dict(orient='records')
    return jsonify(result)

@app.route('/api/ratio_positive_tweets')
def ratio_positive_tweets():
    # Count the number of positive tweets
    num_positive_tweets = df[df['sentiments'].apply(lambda x: x['compound']) > 0.05].shape[0]

    # Calculate the ratio of positive tweets
    total_tweets = len(df)
    ratio_positive = num_positive_tweets / total_tweets if total_tweets > 0 else 0

    return jsonify({'ratio_positive_tweets': float(ratio_positive)})

@app.route('/api/ratio_negative_tweets')
def ratio_negative_tweets():
    # Count the number of negative tweets
    # Assuming negative sentiment is indicated by a compound score less than -0.05
    num_negative_tweets = df[df['sentiments'].apply(lambda x: x['compound']) < -0.05].shape[0]

    # Calculate the ratio of negative tweets
    total_tweets = len(df)
    ratio_negative = num_negative_tweets / total_tweets if total_tweets > 0 else 0

    return jsonify({'ratio_negative_tweets': float(ratio_negative)})


# API Endpoint for Average Engagement Rate
@app.route('/api/average_engagement_rate')
def average_engagement_rate():
    avg_engagement_rate = df['engagement_count'].mean()
    return jsonify({'average_engagement_rate': avg_engagement_rate})

# API Endpoint for Average Impressions
@app.route('/api/average_impressions')
def average_impressions():
    avg_impressions = df['impressions_count'].mean()
    return jsonify({'average_impressions': avg_impressions})

@app.route('/api/tweets_with_hashtags')
def tweets_with_hashtags():
    # Function to check if a tweet contains hashtags (case insensitive)
    def contains_hashtag(text):
        return any(word.lower().startswith('#') for word in text.split())

    # Filter tweets that contain hashtags
    tweets_with_hashtag = df[df['processed_text'].apply(contains_hashtag)]

    # Debugging: Print the number of tweets found
    print(f"Number of tweets with hashtags: {tweets_with_hashtag.shape[0]}")

    # Select relevant columns, for example, 'text' or 'processed_text'
    result = tweets_with_hashtag[['text']].to_dict(orient='records')

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

if __name__ == '__main__':
    app.run(debug=True)