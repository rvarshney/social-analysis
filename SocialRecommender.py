import os
import json
import csv
import math
from datetime import datetime 

# analysis of a subset of Facebook users to create a
# basic friend recommender system

# get all the files from the directory
files = os.listdir("/Users/Ruchi/Documents/data/")

# tuple to store user data
user_data = []

def collect_data():
    # iterate through all the files
    for file in files:
        with open("/Users/Ruchi/Documents/data/" + file, 'r') as f:
            entry = json.load(f)
            user = {}
            if 'info' in entry:
                
                # get user id
                if 'id' in entry['info']:
                    user['id'] = entry['info']['id']
                    
                # get hometown id
                if 'hometown' in entry['info']:
                    user['hometown'] = entry['info']['hometown']['id']
                    
                # get gender
                if 'gender' in entry['info']:
                    user['gender'] = entry['info']['gender']
                
                # get age
                if 'birthday' in entry['info']:
                    birthday = datetime.strptime(entry['info']['birthday'].encode('utf-8'), "%m/%d/%Y")
                    user['age'] = math.ceil((datetime.now() - birthday).total_seconds() / (60 * 60 * 24 * 365))
                
                # get language ids
                languages = []
                if 'languages' in entry['info']:
                    for language in entry['info']['languages']:
                        languages.append(language['id'])
                    user['languages'] = languages
    
                # get education details
                schools = []
                concentrations = []
                if 'education' in entry['info']:
                    for education in entry['info']['education']:
                        if 'school' in education:
                            schools.append(education['school']['id'])
                        if 'concentration' in education:
                            for concentration in education['concentration']:
                                concentrations.append(concentration['id'])
                    user['schools'] = schools
                    user['concentrations'] = concentrations
                
                # get employment details
                companies = []
                locations = []
                if 'work' in entry['info']:
                    for company in entry['info']['work']:
                        if 'employer' in company:
                            companies.append(company['employer']['id'])
                        if 'location' in company:
                            locations.append(company['location']['id'])
                    user['companies'] = companies
                    user['locations'] = locations
                
                # get relationship status
                if 'relationship_status' in entry['info']:    
                    user['relationship'] = entry['info']['relationship_status']
    
            # get friend ids
            friends = []
            num_friends = 0
            if 'friends' in entry:
                if 'data' in entry['friends']:
                    for friend in entry['friends']['data']:
                        friends.append(friend['id'])
                        num_friends += 1
                    user['friends'] = friends 
                    user['num_friends'] = num_friends
            
            # get checkin location ids
            checkins = []
            if 'profile_feed' in entry:
                if 'data' in entry['profile_feed']:
                    for profile_feed in entry['profile_feed']['data']:
                        if 'place' in profile_feed:
                            checkins.append(profile_feed['place']['id'])
                    user['checkins'] = checkins
    
            # get page like ids
            page_likes = []
            if 'page_likes' in entry:
                if 'data' in entry['page_likes']:
                    for page_like in entry['page_likes']['data']:
                        page_likes.append(page_like['id'])
                    user['page_likes'] = page_likes
            
            # get group ids
            groups = []
            if 'groups' in entry:
                if 'data' in entry['groups']:
                    for group in entry['groups']['data']:
                        groups.append(group['id'])
                    user['groups'] = groups  
        
            # get event ids
            events = []
            if 'events' in entry:
                if 'data' in entry['events']:
                    for event in entry['events']['data']:
                        events.append(event['id'])
                    user['events'] = events  
    
            # get movie ids
            movies = []
            if 'movies' in entry:
                if 'data' in entry['movies']:
                    for movie in entry['movies']['data']:
                        movies.append(movie['id'])
                    user['movies'] = movies
            
            # get book ids
            books = []
            if 'books' in entry:
                if 'data' in entry['books']:
                    for book in entry['books']['data']:
                        books.append(book['id'])
                    user['books'] = books
            
            user_data.append(user)

def compute_score(user_i, user_j):
    score = 0;
    # same user
    if user_i['id'] == user_j['id']:
        score = 0
    # if you are already friends
    elif user_i['id'] in user_j['friends']:
        score = 0
    else:
        # if hometowns are different, give 5 points
        if 'hometown' in user_i and 'hometown' in user_j:
            if cmp(user_i['hometown'], user_j['hometown']) != 0:
                score += 5
        else:
            score += 1
            
        # if genders are different, give 5 points
        if 'gender' in user_i and 'gender' in user_j:
            if cmp(user_i['gender'], user_j['gender']) != 0:
                score += 10
        else:
            score += 1
                
        if 'relationship' in user_i and 'relationship' in user_j:
            if cmp(user_i['relationship'], user_j['relationship']) == 0:
                if cmp(user_i['relationship'], 'Single') == 0:
                    # more points for different genders
                    if cmp(user_i['gender'], user_j['gender']) == 0:
                        score += 5
                    else:
                        score += 20
                else:
                    # if you are engaged, in a relationship etc, more points for being the same gender
                    if cmp(user_i['gender'], user_j['gender']) == 0:
                        score += 10
                    else:
                        score += 5
        else:
            score += 1
            
        if 'friends' in user_i and 'friends' in user_j:    
            # having more friends results in more points
            if user_i['num_friends'] < user_j['num_friends']:
                score += 5
                
            # give points for difference in number in friends
            diff_num_friends = abs(user_i['num_friends'] - user_j['num_friends'])
            if diff_num_friends != 0:
                score += math.ceil(math.log(diff_num_friends, 2))

            # give points for mutual friends
            mutual_friends = set(user_i['friends']).intersection(set(user_j['friends']))
            if len(mutual_friends) != 0:
                score += math.ceil(math.log(len(mutual_friends), 2))
        else:
            score += 1
                   
        # give points for less difference in age
        if 'age' in user_i and 'age' in user_j:
            diff_age = abs(user_i['age'] - user_j['age'])
            score += math.ceil(math.log(60 - diff_age, 2))
        else:
            score += 1
                   
        # give points for common languages
        if 'languages' in user_i and 'languages' in user_j:
            mutual_languages = set(user_i['languages']).intersection(set(user_j['languages']))
            score += (2 * len(mutual_languages))
        else:
            score += 1
            
        # give points for different schools
        if 'schools' in user_i and 'schools' in user_j:
            mutual_schools = set(user_i['schools']).intersection(set(user_j['schools']))
            score += (10 - len(mutual_schools))
        else:
            score += 1
            
        # give points for different education concentrations
        if 'concentrations' in user_i and 'concentrations' in user_j:
            mutual_concentrations = set(user_i['concentrations']).intersection(set(user_j['concentrations']))
            score += (5 - len(mutual_concentrations))
        else:
            score += 1 
        
        # give points for common page likes
        if 'page_likes' in user_i and 'page_likes' in user_j:
            mutual_page_likes = set(user_i['page_likes']).intersection(set(user_j['page_likes']))
            score += (2 * len(mutual_page_likes))
        else:
            score += 1
                
        # give points for common movies
        if 'movies' in user_i and 'movies' in user_j:
            mutual_movies = set(user_i['movies']).intersection(set(user_j['movies']))
            score += len(mutual_movies)
        else:
            score += 1
            
        # give points for common books
        if 'books' in user_i and 'books' in user_j:
            mutual_books = set(user_i['books']).intersection(set(user_j['books']))
            score += len(mutual_books)
        
        # give points for common groups
        if 'groups' in user_i and 'groups' in user_j:
            mutual_groups = set(user_i['groups']).intersection(set(user_j['groups']))
            score += len(mutual_groups)
        else:
            score += 1
            
        # give points for common checkins
        if 'checkins' in user_i and 'checkins' in user_j:
            mutual_checkins = set(user_i['checkins']).intersection(set(user_j['checkins']))
            score += (2 * len(mutual_checkins))
        else:
            score += 1
                
        # give points for common events
        if 'events' in user_i and 'events' in user_j:
            mutual_events = set(user_i['events']).intersection(set(user_j['events']))
            score += len(mutual_events)
        else:
            score += 1
            
        # give points for common employers
        if 'companies' in user_i and 'companies' in user_j:
            mutual_companies = set(user_i['companies']).intersection(set(user_j['companies']))
            score += len(mutual_companies)
        else:
            score += 1
            
        # give points for different employment locations
        if 'locations' in user_i and 'locations' in user_j:
            mutual_locations = set(user_i['locations']).intersection(set(user_j['locations']))
            score += (10 - len(mutual_locations))
        else:
            score += 1
        
        if score < 0:
            print user_i['id'], user_j['id']
            
    return score

# gather data
collect_data()

# sort the data
user_data = sorted(user_data, key=lambda user: user['id'], reverse=False)  

# compute matrix
writer = csv.writer(open('matrix.csv', 'wb'), delimiter=',')
for user_i in user_data:
    user_i_scores = []
    norm_user_i_scores = []
    user_i_scores_sum = 0
    var_user_i_score_sum = 0
    num_scores = 0
    for user_j in user_data:
        score = compute_score(user_i, user_j)
        user_i_scores.append(score)
        user_i_scores_sum += score
        num_scores += 1
    avg_user_i_score = float(float(user_i_scores_sum) / float(num_scores))
    for i in user_i_scores:
        var_user_i_score_sum += math.pow(i - avg_user_i_score, 2)
    std_user_i_score = math.sqrt(float(float(var_user_i_score_sum) / float(num_scores)))
    for i in user_i_scores:
        norm_user_i_score = float((i - avg_user_i_score) / std_user_i_score)
        norm_user_i_scores.append(norm_user_i_score)
    writer.writerow(norm_user_i_scores)
