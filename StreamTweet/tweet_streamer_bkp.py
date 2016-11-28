import tweepy
import json
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from credentials import consumer_key, consumer_secret,access_token,access_token_secret, queue_name

host = "search-jask-tweetmap-hhk4izgywmbpwob2zah4fcdiry.us-west-2.es.amazonaws.com"
awsauth = AWS4Auth(consumer_key, consumer_secret,'us-west-2','es')
es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        use_ssl=True,
        http_auth=awsauth,
        verify_certs=True,
        connection_class=RequestsHttpConnection
        )

print(es.info())

# This is the listener, resposible for receiving data
class StdOutListener(tweepy.StreamListener):
    def on_status(self, status):
        json_data = status._json
        user_info = json_data['user']
        if json_data['coordinates']:
            data = {
                    'id': json_data['id'],
                    'content': json_data['text'].lower().encode('ascii','ignore').decode('ascii'),
                    'user': user_info['name'],
                    'user_id': user_info['id'],
                    }

            print(data)
            #Add to elastic search
            try:
                es.index(index='cloud_tweet', doc_type='twitter', body=data)
            except:
                print('ElasticSearch indexing failed')

        return True

def on_error(self, status):
    print status

if __name__ == '__main__':
    l = StdOutListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = tweepy.Stream(auth, l)
    #filter for these terms in tweet text
    terms = [
            'jobs','programming' , 'elections', 'Trump', 'usa', 'wanderlust'
            ,'movies','sports','music','finance','technology'
            ,'fashion','science','travel','health','cricket'
            ,'india', 'love', 'shit','bjp', 'aap', 'india'
            ,'epl', 'football','goal', '1-0' ]
    #stream
    #stream.filter(None,terms)
    while True:
        try:
            stream.filter(track=terms)
        except Exception as e:
            pass
