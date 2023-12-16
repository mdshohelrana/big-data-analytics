from flask import Flask
from TwitterClient import TwitterClient

app = Flask(__name__)

@app.route('/')
def home():
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name="JoeBiden", count=200)

    return "<br>".join([tweet.text for tweet in tweets])

if __name__ == '__main__':
    app.run(debug=True)
