import tweepy
from pymongo import MongoClient


class Tweets:

    def __init__(self):
        # consumer key, consumer secret, access token, access secret.
        ckey = 'i1QhUrFyQqcmkBJzvF5zQYpah'
        csecret = 'UOza8S2imQp3BY1JFROCAisaisqVe65ck5h6sUnq5JTIg8gLds'
        atoken = '931513757632811009-IPHmddqyJxEfDWIw557cyS1YHYxJ04g'
        asecret = 'JgkiPadHlfdGS39OAAt5D7ohtnJ2BY77wSX66oQV7g0GC'

        auth = tweepy.OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)
        self.api = tweepy.API(auth)


    def trendsUSA(self):
        US_WOE_ID = 23424977
        us_trends = self.api.trends_place(US_WOE_ID)
        # trends1 is a list with only one element in it, which is a
        # dict which we'll put in data.
        data = us_trends[0]
        # grab the trends
        trends = data['trends']
        # grab the name from each trend
        names = [trend['name'] for trend in trends]
        return names[0:5]


    def getTweets(self, query, collection):

        counterForTweets = 1046

        for tweet in tweepy.Cursor(self.api.search, q=query, lang="en", since_id=939462510150811648).items():
            if (not tweet.retweeted) and ('RT @' not in tweet.text):
                print(tweet.id)
                collection.insert(tweet._json)
                counterForTweets = counterForTweets + 1
                if counterForTweets == 1500:
                    break


if __name__ == '__main__':

    # check README.txt first
    # open DB, change by hand the name of collection for new topic, and the trend for each topic
    client = MongoClient()
	
    # db = client.twitterDB_2548_2529
    # db = client.test2coll
	
    collection = db.prwti
    tweets = Tweets()

    trends = tweets.trendsUSA()
    print(trends)

    tweets.getTweets(trends[0], collection)
