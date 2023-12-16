import tweepy

#### TWITTER AUTHENTICATOR ####
class TwitterAuthenticator:
    """
    A class for authentication of the consumer.
    """
    def authenticate_twitter_app(self):
        consumer_key = 'W4lzvY0sJjk7Nh0fqfSo6RqTP'
        consumer_secret = 'oh5r96fuC382iIqXF7pslwrUbadAsmxpZnEfEo2yz7lLB9mhlG'
        access_token = '220636914-oEA2K0QKhlwGNuCeKf6k5wE6NL60Mnp0vEDGqP2r'
        access_token_secret = '2XUjFZTifvIXQXDVlqqzACNXTzDNiqYaekG4kkzenThX3'

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return auth