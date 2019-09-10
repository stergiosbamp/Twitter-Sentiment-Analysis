from scipy import special
import requests
import json
from pymongo import MongoClient
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import *
import matplotlib.pyplot as plt
import numpy as np


class TweetsEdit:
    def __init__(self):
        nltk.download('stopwords')
        nltk.download('punkt')


    def tweetEdit(self, collection, topic):
        # gia kathe tweet pou apothikeytike pairnw me to .find() to pedio text kai ginetai oli i epeksergasia
        for obj in collection.find():
            s = (obj['text'])
            pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            s = pattern.sub('', s)
            # afairw ta simvola
            s = re.sub(r'[^\w]', ' ', s)
            # afairw oti einai arithmos
            s = re.sub(r'[\d]', '', s)
            # kanw ta kefalaia mikra
            s = s.lower()
            # spaw tin frasi se lekseis
            word_tokens = word_tokenize(s)

            # orizw tin sillogi me ta stop words
            stop_words = set(stopwords.words('english'))
            filtered_sentence = []


            for w in word_tokens:
                # gia kathe leksi an den einai stopword i an den einai to hastag thn vazw stin lista moy
                # !!kathe fora allazo tin leksi - topic ths ekastote sullogis
                hastag = re.sub(r'[^\w]', '', topic)
                hastag = re.sub(r'[\d]', '', hastag)
                hastag = hastag.lower()
                if w not in stop_words and w != hastag:
                    filtered_sentence.append(w)

            # vazw stin sillogi kainourio pedio onomati filtered_text
            collection.update(obj, {"$set": {"filtered_text": filtered_sentence}})

    def test(self):
        # Testing tokenization and normalization(before/after)
        for obj in collection.find():
            text = (obj['text'])
            print(text)
            text = (obj['filtered_text'])
            print(text)
            print()


class SentimentAnalysis:

    def computeSentiment(self, collection):
        for obj in collection.find():
            url = "http://text-processing.com/api/sentiment/"
            text = (obj['filtered_text'])
            sentence = ' '.join(text)
            if sentence == '':
                collection.update(obj, {"$set": {"label": "neutral"}})
                collection.update(obj, {"$set": {"positive probability": 0}})
                collection.update(obj, {"$set": {"negative probability": 0}})
                collection.update(obj, {"$set": {"neutral probability": 0}})
                continue
            payload = {'text': sentence}
            print(payload)
            r = requests.post(url, payload)
            print(r.text)
            json_data = json.loads(r.text)
            print(json_data['label'])
            collection.update(obj, {"$set": {"label": json_data['label']}})
            collection.update(obj, {"$set": {"positive probability": json_data['probability']['pos']}})
            collection.update(obj, {"$set": {"negative probability": json_data['probability']['neg']}})
            collection.update(obj, {"$set": {"neutral probability": json_data['probability']['neutral']}})


class ComputeStatistics:

    def showPie(self, collection, topic):
        counter = Counter()
        for obj in collection.find():
            label = obj['label']
            if label == 'neutral':
                counter['neutral'] += 1
            elif label == 'pos':
                counter['pos'] += 1
            elif label == 'neg':
                counter['neg'] += 1

        print(counter)

        numberOfNeutrals = counter['neutral']
        numberOfNegs = counter['neg']
        numberOfPos = counter['pos']

        labels = 'neutral', 'negative', 'positive'
        sizes = [numberOfNeutrals, numberOfNegs, numberOfPos]

        fig1, ax1 = plt.subplots()
        plt.title('Sentiment percentages for topic: ' + topic)
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        plt.show()

    def count50Unfiltered(self, collection, topic):
        word_counter = Counter()
        for obj in collection.find():
            my_string = obj['text']
            words = re.findall(r'\w+', my_string.lower())  # This finds words in the document and convert them in lowercase
            # print(words)

            for word in words:
                word_counter[word] += 1

        print(word_counter.most_common(50))

        ## HISTOGRAM :



        labels, values = zip(*word_counter.most_common(50))
        indexes = np.arange(len(labels))
        plt.figure(figsize=(10,5))
        plt.bar(indexes, values)
        plt.title("50 more frequent terms (unfiltered) for: " + topic)
        plt.xticks(indexes, labels, size=8, rotation=70)
        plt.show()


        ## ZIPF :

        vals = []
        for k, v in word_counter.items():
            vals.append(v)

        print(vals)

        a = 2.  # distribution parameter
        # s = np.random.zipf(a,1500)
        s = np.array(vals)

        count, bins, ignored = plt.hist(s[s<50], 50, normed=True)
        x = np.arange(1., 50.)
        y = x ** (-a) / special.zetac(a)
        # plt.xscale('log')
        # plt.yscale('log')
        plt.title('Zipf distribution diagram(log-log scale) for all word, from topic: ' + topic)
        # plt.plot(x, y / max(y), linewidth=2, color='r')
        plt.loglog(x, y / max(y), linewidth=2, color='r')
        plt.show()

    def count50Filtered(self, collection, topic):
        word_counter = Counter()
        for obj in collection.find():
            words = (obj['filtered_text'])
            # print(words)
            for word in words:
                word_counter[word] += 1

        print(word_counter.most_common(50))

        ## HISTOGRAM

        labels, values = zip(*word_counter.most_common(50))
        indexes = np.arange(len(labels))
        plt.figure(figsize=(10,5))
        plt.bar(indexes, values)
        plt.title("50 more frequent terms (filtered) for: " + topic)
        plt.xticks(indexes, labels, size=8, rotation=70)
        plt.show()


if __name__ == '__main__':
    client = MongoClient()

    db = client.twitterDB_2548_2529
    # db = client.test2coll

    # we already have the topics and the tweets so :
    names = ["#FridayFeeling", "2018PredictionsIn5Words", "Angels", "#WhatIWantSantaToBringMe",
             "#ThingsITrustMoreThanFoxNews"]

    
    tweetsEdit = TweetsEdit()

    sentiment = SentimentAnalysis()

    stats = ComputeStatistics()

    for i in range(0, 5):
        if i == 0:
            collection = db.prwti
        elif i == 1:
            collection = db.deuteri
        elif i == 2:
            collection = db.triti
        elif i == 3:
            collection = db.tetarti
        elif i == 4:
            collection = db.pempti

        #Tokenization:
        tweetsEdit.tweetEdit(collection, names[i])
        tweetsEdit.test()

        #Sentiment:
        sentiment.computeSentiment(collection)

        #Statistics:
        stats.showPie(collection,names[i])
        stats.count50Unfiltered(collection, names[i])
        stats.count50Filtered(collection, names[i])
