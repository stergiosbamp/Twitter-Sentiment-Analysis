import matplotlib.pyplot as plt
import re
import numpy as np
from pymongo import MongoClient
from collections import Counter
from scipy import special
from collections import defaultdict


class UserStats:

    def stats(self, collection):
        myList = list()
        dict = defaultdict(list)
        for obj in collection.find():
            userId = obj['user']['id']

            scorePos = 0
            scoreNeg = 0
            scoreNeutral = 0

            tweets = 0

            followers = obj['user']['followers_count']
            friends = obj['user']['friends_count']

            if friends == 0:
                ratio = 0
                # myList.append(ratio)
                # continue
            else:
                ratio = followers / friends
            # collection.update(obj, {"$set": {"ratio(followers/friends)": ratio}})
            myList.append(ratio)
            # print(followers, friends, ratio)

            for object in collection.find():
                if object['user']['id'] == userId:
                    tweets += 1

                    scoreNeutral += object['neutral probability']

                    scorePos += object['positive probability']

                    scoreNeg += object['negative probability']

            scorePos = scorePos / tweets
            scoreNeg = scoreNeg / tweets
            scoreNeutral = scoreNeutral / tweets

            if scorePos > scoreNeg and scorePos > scoreNeutral:
                max = scorePos
                result = 'pos'
            elif scoreNeg > scorePos and scoreNeg > scoreNeutral:
                max = scoreNeg
                result = 'neg'
            elif scoreNeutral > scorePos and scoreNeutral > scoreNeg:
                max = scoreNeutral
                result = 'neutral'
            else:
                result = 'undefined'
                max = 0

            res = [result, max]

            dict[userId] = res

        print(dict)


        # CDF:
        print(myList)
        print()
        print()
        data = myList

        values, base = np.histogram(data, bins=40)
        cumulative = np.cumsum(values)
        plt.plot(base[:-1], cumulative, c='blue')
        # plt.loglog(base[:-1], cumulative, c='blue')
        plt.show()

        return dict

    def writeToFile(self, dict, text_file):

        for k, v in dict.items():
            # lab = []
            # for token in v:
            #   lab.append(token)
            # string = str(k) + "                     " + str(lab[0]) + "                     " + str(lab[1]) + "\n"
            string = str(k) + "     " + str(v[0]) + "\n"
            text_file.write(string)

        text_file.close()

        print("Data have been writen to file.")


if __name__ == '__main__':

    client = MongoClient()
	
	# ! it will override the .txt files
	
    # db = client.twitterDB_2548_2529
    # db = client.test2col

    userStats = UserStats()

    for i in range(0, 5):
        if i == 0:
            collection = db.prwti
            text_file = open("sent_prwti.txt", "w")
        elif i == 1:
            collection = db.deuteri
            text_file = open("sent_deuteri.txt", "w")
        elif i == 2:
            collection = db.triti
            text_file = open("sent_triti.txt", "w")
        elif i == 3:
            collection = db.tetarti
            text_file = open("sent_tetarti.txt", "w")
        elif i == 4:
            collection = db.pempti
            text_file = open("sent_pempti.txt", "w")

        dictionary = userStats.stats(collection)
        userStats.writeToFile(dictionary, text_file)

