import tweepy
from TwitterAuthenticator import TwitterAuthenticator

#### TWITTER CLIENT ####
class TwitterClient():
    """
    Access to client's tweets and other user's tweets.
    """
    def __init__(self,twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        # Client
        self.twitter_client = tweepy.API(self.auth)
        # Other users
        self.twitter_user = twitter_user
        
    def get_twitter_client_api(self):
        return self.twitter_client
        
    def get_user_timeline_tweets(self,num_tweets):
        tweets = []
        for tweet in tweepy.Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
    
    def get_friend_list(self,num_friends):
        friend_list = []
        for friend in tweepy.Cursor(self.twitter_client.friends,id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list
    
    def get_home_timeline_tweets(self,num_tweets):
        home_timeline_tweets = []
        for tweet in tweepy.Cursor(self.twitter_client.home,id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets