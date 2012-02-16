import time
import twitter
import cPickle
import math
from prettytable import PrettyTable

# oath data grabbed from https://dev.twitter.com/apps
consumer_key = 'consumer_key'
consumer_secret = 'consumer_secret'
app_name = 'Ruchi Varshney'

# hard code the oauth tokens
(oauth_token, oauth_token_secret) = ('oauth_token', 'oauth_token_secret')

# init the authenticated client
t = twitter.Twitter(domain='api.twitter.com', api_version='1', auth=twitter.oauth.OAuth(oauth_token, oauth_token_secret, consumer_key, consumer_secret))

# tuple to store user data
users = []

def read_large_users():
    # read list of large users from disk
    large_users = ['allstate', 'elatable', 'edyson', 'andrewmason', 'joshu', 'mlevchin', 'quora', 'Bill_Gross', 'zephoria', 'fredwilson']
    
    for sn in large_users:
        path = '/Users/Ruchi/Documents/data/' + sn + '.txt'
        file = open(path, 'r')
        
        followers = cPickle.load(file)
        file.close()
        
        # record info collected about each screen name
        user = {}
        user['screen_name'] = sn
        user['followers_count'] = len(followers)
        
        # retrieve their most recent 200 tweets
        try:
            response = t.statuses.user_timeline(id=sn, count=200, include_rts=True)
            retweet_sum = 0
            status_count = 0
            for status in response:
                status_count += 1
                value = str(status['retweet_count'])
                if (value[len(value) - 1] == '+'):
                    retweet_sum += int(value[:len(value) - 1])
                else:
                    retweet_sum += int(value)
            user['retweets_sum'] = retweet_sum
            user['tweets_count'] = status_count
            
            # retrieve the listed count
            user['listed_count'] = status['user']['listed_count']
        except twitter.api.TwitterHTTPError, e:
            print e
            
        # retrieve their most recent 200 self-authored tweets
        try:
            response = t.statuses.user_timeline(id=sn, count=200, include_rts=False)
            self_authored_retweet_sum = 0
            status_count = 0
            for status in response:
                status_count += 1 
                value = str(status['retweet_count'])
                if (value[len(value) - 1] == '+'):
                    self_authored_retweet_sum += int(value[:len(value) - 1])
                else:
                    self_authored_retweet_sum += int(value)
            user['self_authored_retweets_sum'] = self_authored_retweet_sum
            user['self_authored_tweets_count'] = status_count
        except twitter.api.TwitterHTTPError, e:
            print e
        
        # calculate average second level follower count
        count = 0
        for follower_screen_name, follower in followers.iteritems():
            print user['screen_name'], follower_screen_name, follower['followers_count']
            count += follower['followers_count']
        user['avg_second_level_followers_count'] = count / user['followers_count']
        
        # append the user to list of users   
        users.append(user)
        

def read_small_users():
    # list of small users
    small_users = ['aweigend', 'enriqueallen', 'marc_smith', 'ptwobrussell', 'mingyeow', 'hirshberg', 'sfnewtech', 'shopkick', 'tglocer', 'thinkandroid']
    
    for sn in small_users:
        # init list of ids
        ids = []
        wait_period = 2
        cursor = -1
        
        # fetching user follower ids
        while cursor != 0:
            try:
                # make API call to get user's followers
                response = t.followers.ids(screen_name=sn, cursor=cursor)
                ids.extend(response['ids'])
                wait_period = 2
            except twitter.api.TwitterHTTPError, e:
                if e.e.code == 401:
                    print 'Encountered 401 Twitter HTTP Authorization Error'
                elif e.e.code in (502, 503):
                    print 'Encountered %i Error. Trying again in %i seconds' % (e.e.code, wait_period)
                    time.sleep(wait_period)
                    wait_period *= 1.5
                    continue
                elif t.account.rate_limit_status()['remaining_hits'] == 0:
                    # handle case when we hit the rate limit
                    now = time.time()
                    when_rate_limit_resets = t.account.rate_limit_status()['reset_time_in_seconds']
                    sleep_time = when_rate_limit_resets - now
                    print 'Rate limit reached. Trying again in %i seconds' % (sleep_time)
                    time.sleep(sleep_time)
                    continue
            
            cursor = response['next_cursor']
        
        print 'Fetched in total %i ids for %s' % (len(ids), sn)
        
        # record info collected about each screen name
        user = {}
        user['screen_name'] = sn
        user['followers_count'] = len(ids)
        
        # retrieve their most recent 200 tweets 
        try:
            response = t.statuses.user_timeline(id=sn, count=200, include_rts=True)
            retweet_sum = 0
            status_count = 0
            for status in response:
                status_count += 1
                value = str(status['retweet_count'])
                if (value[len(value) - 1] == '+'):
                    retweet_sum += int(value[:len(value) - 1])
                else:
                    retweet_sum += int(value)
            user['retweets_sum'] = retweet_sum
            user['tweets_count'] = status_count
            
            # retrieve the listed count
            user['listed_count'] = status['user']['listed_count']
        except twitter.api.TwitterHTTPError, e:
            print e
        
        # retrieve their most recent 200 self-authored tweets
        try:
            response = t.statuses.user_timeline(id=sn, count=200, include_rts=False)
            self_authored_retweet_sum = 0
            status_count = 0
            for status in response:
                status_count += 1
                value = str(status['retweet_count'])
                if (value[len(value) - 1] == '+'):
                    self_authored_retweet_sum += int(value[:len(value) - 1])
                else:
                    self_authored_retweet_sum += int(value)
            user['self_authored_retweets_sum'] = self_authored_retweet_sum
            user['self_authored_tweets_count'] = status_count
        except twitter.api.TwitterHTTPError, e:
            print e
        
        # calculate average second level follower count
        try:
            count = 0
            fetched_follower_count = 0
            for i in range(int(math.ceil(float(float(user['followers_count']) / float(100))))):
                subids = ids[i * 100:(i + 1) * (100 - 1)]
                response = t.users.lookup(user_id=subids)
                for follower in response:
                    print user['screen_name'], follower['screen_name'], follower['followers_count']
                    count += follower['followers_count']
                    fetched_follower_count += 1
            user['avg_second_level_followers_count'] = count / fetched_follower_count
        except twitter.api.TwitterHTTPError, e:
            print e
            
        # append the user to list of users    
        users.append(user)

        
# trivial algorithm 
def trivial_algorithm():
    sorted_user_tuples = sorted(users, key=lambda user: user['followers_count'], reverse=True)    
    fields = ['screen_name', 'followers_count']
    pt = PrettyTable(fields=fields)
    [pt.set_field_align(f, 'l') for f in fields]
    for user in sorted_user_tuples:
        pt.add_row([user['screen_name'], user['followers_count']])
    pt.printt()

# non-trivial algorithm
def non_trivial_algorithm():    
    # normalize followers_count
    max_followers_count = 0
    for user in users:
        max_followers_count = max(max_followers_count, user['followers_count'])
    for user in users:
        user['normalized_followers_count'] = float(float(user['followers_count']) / float(max_followers_count))

    # normalize avg_second_level_followers_count
    max_avg_second_level_followers_count = 0
    for user in users:
        max_avg_second_level_followers_count = max(max_avg_second_level_followers_count, user['avg_second_level_followers_count'])
    for user in users:
        user['normalized_avg_second_level_followers_count'] = float(float(user['avg_second_level_followers_count']) / float(max_avg_second_level_followers_count))
    
    # normalize listed_count
    max_listed_count = 0
    for user in users:
        max_listed_count = max(max_listed_count, user['listed_count'])
    for user in users:
        user['normalized_listed_count'] = float(float(user['listed_count']) / float(max_listed_count))
    
    # calculate and normalize maven_score
    max_maven_score = 0 
    for user in users:
        numerator = user['retweets_sum'] - user['self_authored_retweets_sum']
        denominator = user['tweets_count'] - user['self_authored_tweets_count']
        if numerator == 0 or denominator == 0:
            user['maven_score'] = 0
        else:
            user['maven_score'] = float(float(numerator)) / float((denominator))
        max_maven_score = max(max_maven_score, user['maven_score'])
    for user in users:
        user['normalized_maven_score'] = float(float(user['maven_score']) / float(max_maven_score))
    
    # calculate and normalize avg_self_authored_retweets
    max_avg_self_authored_retweets = 0
    for user in users:
        user['avg_self_authored_retweets_count'] = float(float(user['self_authored_retweets_sum']) / float(user['self_authored_tweets_count']))
        max_avg_self_authored_retweets = max(max_avg_self_authored_retweets, user['avg_self_authored_retweets_count'])
    for user in users:
        user['normalized_avg_self_authored_retweets_count'] = float(float(user['avg_self_authored_retweets_count']) / float(max_avg_self_authored_retweets)) 
                
    for user in users:
        user['objective_function'] = float(100 * (0.4 * user['normalized_avg_self_authored_retweets_count'] + 0.25 * user['normalized_avg_second_level_followers_count'] + 0.15 * user['normalized_followers_count'] + 0.1 * user['normalized_maven_score'] + 0.1 * user['normalized_listed_count']))
    
    sorted_user_tuples = sorted(users, key=lambda user: user['objective_function'], reverse=True)
    
    fields = ['screen_name', 'objective_function']
    pt = PrettyTable(fields=fields)
    [pt.set_field_align(f, 'l') for f in fields]
    for user in sorted_user_tuples:
        pt.add_row([user['screen_name'], user['objective_function']])
    pt.printt()
    
def print_collected_info():
    fields = ['screen_name', 'followers_count', 'avg_second_level_followers_count', 'tweets_count', 'retweets_sum', 'listed_count', 'self_authored_tweets_count', 'self_authored_retweets_sum', 'avg_self_authored_retweets_count', 'maven_score', 'normalized_avg_self_authored_retweets_count', 'normalized_avg_second_level_followers_count', 'normalized_followers_count', 'normalized_maven_score', 'normalized_listed_count', 'objective_function']
    pt = PrettyTable(fields=fields)
    [pt.set_field_align(f, 'l') for f in fields]
    for user in users:
        pt.add_row([user['screen_name'], user['followers_count'], user['avg_second_level_followers_count'], user['tweets_count'], user['retweets_sum'], user['listed_count'], user['self_authored_tweets_count'], user['self_authored_retweets_sum'], user['avg_self_authored_retweets_count'], user['maven_score'], user['normalized_avg_self_authored_retweets_count'], user['normalized_avg_second_level_followers_count'], user['normalized_followers_count'], user['normalized_maven_score'], user['normalized_listed_count'], user['objective_function']])
    pt.printt()
    
# collect all the needed data for the algorithms
read_large_users()
read_small_users()

# run the trivial algorithm
trivial_algorithm()

# run the non-trivial algorithm
non_trivial_algorithm()

# print all the collected info
print_collected_info()
