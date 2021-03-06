from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

import twitter_credentials
import numpy as np
import pandas as pd

'''
TWITTER CLIENT
Data from one twitter account
'''
class TwitterClient():

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user
    
    '''
    Grab number_of_tweets from the timeline of the specified user
    if twitter_user=None --> goes to your own timeline
    '''
    def get_user_timeline_tweets(self, number_of_tweets):
        tweets =[]
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(number_of_tweets):
            tweets.append(tweet)
        return tweets

    def get_twitter_client_api(self):
        return self.twitter_client
'''
TWITTER AUTHENTICATOR
'''
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        # Authenticate code
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        # Authenticate application
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

'''
TWITTER STREAMER
Class for streaming and processing tweets
'''
class TwitterStreamer():
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()
    '''
    This method handles Twitter authentication and the connection to the twitter Streaming API
    Save tweets to file 'fetched_tweets_filename'
    '''
    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # Create object
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()

        # create a data stream
        stream = Stream(auth, listener)

        # Define words for filtering Twitter streams 
        stream.filter(track=hash_tag_list)

'''
TWITTER STREAM LISTENER
Class that inherit from StreamListener
Prints received tweets to stdout
'''
class TwitterListener(StreamListener):
    # Constructor
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename
        self.i = 0

    # Method who takes the data (listening to tweets)
    def on_data(self, raw_data):
        try:
            json_load = json.loads(raw_data)
            text = json_load['text']
            coded = text.encode('utf-8')
            s = str(coded)
            print("########## NEW TWEET: Nr: %i ########## \n" % (self.i), s[2:-1])

            self.i +=1
            text = json_load['geo']
            s = str(text)
            print("LOCATION", s)
            print()


            '''MORE CODE HERE'''

            # Save to file
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(raw_data)
            return True

        except BaseException as e:
            print("Error on raw_data: %s" %str(e))
        return True

    # Method who handles errors
    def on_error(self, status_code):
        '''
        402 error from twitter API = hit the rate limit. You have to wait
        a certain time before proceed otherwise Twitter looks the app out
        '''
        if status_code == 420:
            return False
        print(status_code)

'''
Analyzing content from tweets and store it in a dataframe
'''
class TweetAnalzer():
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['geo'] = np.array([tweet.geo for tweet in tweets])

        return df

if __name__ == "__main__":
    '''
    CLIENT PART
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalzer()
    api = twitter_client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name="realDonaldTrump", count=2)

    # Take data and put it in a dataframe and store it in df
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    print(df.head(10))

    # Get avarage length over all tweets
    print(np.mean(df['len']))
    '''

    '''STREAMER PART'''
    hash_tag_list = ["bitcoin"]
    fetched_tweets_filename = "tweets.txt"
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)

  
    
