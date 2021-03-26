#########################################
##### Name:  Tzu-Ching Lin          #####
##### Uniqname:    tzlin            #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests
import operator

import secrets # file that contains your OAuth credentials

CACHE_FILENAME = "twitter_cache_ec.json"
CACHE_DICT = {}

client_key = secrets.TWITTER_API_KEY
client_secret = secrets.TWITTER_API_SECRET
access_token = secrets.TWITTER_ACCESS_TOKEN
access_token_secret = secrets.TWITTER_ACCESS_TOKEN_SECRET

oauth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)

def test_oauth():
    ''' Helper function that returns an HTTP 200 OK response code and a 
    representation of the requesting user if authentication was 
    successful; returns a 401 status code and an error message if 
    not. Only use this method to test if supplied user credentials are 
    valid. Not used to achieve the goal of this assignment.'''

    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    auth = OAuth1(client_key, client_secret, access_token, access_token_secret)
    authentication_state = requests.get(url, auth=auth).json()
    return authentication_state


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params

    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_") 
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    #TODO Implement function
    param_list = []
    for i in params.keys():
        param_list.append(f'{i}_{params[i]}')
    # param_list.sort()
    unique_key = baseurl + '_' +  '_'.join(param_list)
    return unique_key


def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    #TODO Implement function
    response = requests.get(baseurl, params=params, auth=oauth)
    return response.json()


def make_request_with_cache(baseurl, hashtag, count):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache, 
    but it will help us to see if you are appropriately attempting to use the cache.
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    hashtag: string
        The hashtag to search for
    count: integer
        The number of results you request from Twitter
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    #TODO Implement function
    param_dict = {'q':hashtag, 'count': str(count)}
    key = construct_unique_key(baseurl,param_dict)
    if key in CACHE_DICT:
        print("fetching cached data",key)
        return CACHE_DICT[key]
    else:
        print("making new request",key)
        CACHE_DICT[key] = make_request(baseurl,param_dict)
        save_cache(CACHE_DICT)
        return CACHE_DICT[key]


def find_top3_cooccurring_hashtag(tweet_data, hashtag_to_ignore):
    ''' Finds the top three hashtags that most commonly co-occurs with the hashtag
    queried in make_request_with_cache().

    Parameters
    ----------
    tweet_data: dict
        Twitter data as a dictionary for a specific query
    hashtag_to_ignore: string
        the same hashtag that is queried in make_request_with_cache() 
        (e.g. "#MarchMadness2021")

    Returns
    -------
    list of strings
        a list of hashtags which are the top 3 common with the given hashtag 
        for the query

    '''
    # TODO: Implement function 
    if '#' in hashtag_to_ignore: 
        hashtag_string = hashtag_to_ignore.replace('#','')
    else:
        hashtag_string = hashtag_to_ignore

    tweets = tweet_data['statuses']
    hash_dict = {}
    top3_list = []
    for t in tweets:
        if len(t['entities']['hashtags']) is not 0: 
            for h in t['entities']['hashtags']:
                if (h['text'] != hashtag_string) and (h['text'].lower() != hashtag_string.lower()):
                    if h['text'] not in hash_dict:
                        hash_dict[h['text']] = 1
                    else:
                        hash_dict[h['text']] = hash_dict[h['text']] + 1
    if  len(hash_dict) != 0:
        for i in range(3):
            top3_list.append(max(hash_dict.items(), key=operator.itemgetter(1))[0])
            del hash_dict[top3_list[i]]
            if len(hash_dict) < 1:
                break
    
    return top3_list

if __name__ == "__main__":
    if not client_key or not client_secret:
        print("You need to fill in CLIENT_KEY and CLIENT_SECRET in secret_data.py.")
        exit()
    if not access_token or not access_token_secret:
        print("You need to fill in ACCESS_TOKEN and ACCESS_TOKEN_SECRET in secret_data.py.")
        exit()

    CACHE_DICT = open_cache()

    baseurl = "https://api.twitter.com/1.1/search/tweets.json"
    count = 100

    # User prompt:
    while(True):
        hashtag = input("Enter the hashtag you want to search, or enter exit: ")
        if hashtag == "exit":
            break
        tweet_data = make_request_with_cache(baseurl, hashtag, count)
        top3_list = find_top3_cooccurring_hashtag(tweet_data, hashtag)
        if len(top3_list) == 0:
            print(f"There are no hashtags for {hashtag} or no top three co-occurring hashtags")
        else:
            for i in range(len(top3_list)):
                print(f"The NO{i+1} co-occurring hashtag with {hashtag} is #{top3_list[i]}")
