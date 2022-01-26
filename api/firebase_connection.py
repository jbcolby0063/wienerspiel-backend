#connecting to firebase
from firebase import firebase
import pyrebase
from requests.api import get
import insta_post
import twitter_post_analytics
import fb_post_analytics
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env.local')
load_dotenv(dotenv_path=dotenv_path)


#Connects to Firebase for Posting
def get_post_information(firebase_table_id):
    '''
    This function will get the information for the firebase database
    returns the post information in a dictionary format
    '''
    url = os.getenv('REACT_APP_FIREBASE_DATABASE_URL') #this is the url for the firebase database (change if necessary)
    firebase_connection = firebase.FirebaseApplication(url, None)
    post_information = firebase_connection.get('/users/' + firebase_table_id, '')
    return post_information #will also contain post-specific analytics too

def get_media_url(uploadTimeID, media_files):
    config = { #need the api keys for pyrebase
    "apiKey": os.getenv('REACT_APP_FIREBASE_API_KEY'),
    "authDomain": os.getenv('REACT_APP_FIREBASE_AUTH_DOMAIN'),
    "databaseURL": os.getenv('REACT_APP_FIREBASE_DATABASE_URL'),
    "storageBucket": os.getenv('REACT_APP_FIREBASE_STORAGE_BUCKET')
    }
    if(os.getenv("IS_APPENGINE") != 'true'):
        config['serviceAccount'] = './serviceAccountKey.json'
    firebase_connection = pyrebase.initialize_app(config)
    storage = firebase_connection.storage()
    urls_media_files = []
    for x in media_files:
        url = storage.child("users/"+ str(uploadTimeID) + '/' +str(x)).get_url(None)
        urls_media_files.append(url)
    return urls_media_files


def get_fb_table_ids(): #gets the list of firebase table ids
    url = os.getenv('REACT_APP_FIREBASE_DATABASE_URL')
    firebase_connection = firebase.FirebaseApplication(url, None)
    firebase_table_id = list(firebase_connection.get('users/', '').keys())
    return firebase_table_id

def publish_to_platform():
    '''
    will publish information to the appropriate platforms
    will return the post id for each platform in the form of an dictionary object
    will also return the media type in the dictionary object (either 'IMAGE' or 'VIDEO')
    '''
    url = os.getenv('REACT_APP_FIREBASE_DATABASE_URL') #this is the url for the firebase database
    firebase_connection = firebase.FirebaseApplication(url, None)
    firebase_table_id = list(firebase_connection.get('users/', '').keys())[-1]
    post_information = get_post_information(firebase_table_id)
    post_title = post_information['title']
    post_description = post_information['text']
    media_type = post_information['fileType']
    social_media_list = post_information['socialMedia']
    timeid = post_information['uploadTimeID']
    list_media = post_information['fileName']
    media_files = get_media_url(timeid, list_media)
    if('facebookCheck' in social_media_list):
        facebook_post_object = fb_post_analytics.fb_post(post_title, post_description, media_type)
        if(facebook_post_object.media_type == 'video'):
            facebook_post_object.post_media_video(media_files)
            firebase_connection.put('/users/' + firebase_table_id, 'Facebook_post_id', str(facebook_post_object.post_id))
        elif(facebook_post_object.media_type == 'image'):
            facebook_post_object.post_media_photo(media_files)
            firebase_connection.put('/users/' + firebase_table_id, 'Facebook_post_id', str(facebook_post_object.post_id))
        else:
            facebook_post_object.post_no_media()
            firebase_connection.put('/users/' + firebase_table_id, 'Facebook_post_id', str(facebook_post_object.post_id))
    if('twitterCheck' in social_media_list):
        twitter_post_object = twitter_post_analytics.twitter_post(post_description, post_title, media_type)
        if(twitter_post_object.media_type != None):
            twitter_post_object.media_file_list(media_files) #"media_files" must be in list format!
            twitter_post_object.tweet_post_media(list_media)
            firebase_connection.put('/users/' + firebase_table_id, 'Twitter_post_id', str(twitter_post_object.post_status_id))
        else:
            twitter_post_object.tweet_post_nomedia()
            firebase_connection.put('/users/' + firebase_table_id, 'Twitter_post_id', str(twitter_post_object.post_status_id))
    if('instagramCheck' in social_media_list):
        instagram_post_object = insta_post.insta_post(post_title, post_description, media_type)
        instagram_post_object.get_media_ids(media_files) #media files must be file path
        instagram_post_object.publish_post()
        firebase_connection.put('/users/' + firebase_table_id, 'Instagram_post_id', str(instagram_post_object.post_id))
    return None

#Connects to Firebase in order to retrieve post specific analytics
def get_fb_post_analytics(name_of_metric, firebase_table_id):
    #will get the post id and then run the specific function based on metric wanted
    post_info = get_post_information(firebase_table_id)
    post_title = post_info['title']
    post_description = post_info['text']
    media_type = post_info['fileType'] #will need to store the media type on firebase!!
    post_id_fb = post_info['Facebook_post_id']
    facebook_post_object = fb_post_analytics.fb_post(post_title, post_description, media_type)
    facebook_post_object.set_fb_post_id(post_id_fb)
    facebook_post_object.set_fb_media_type(media_type)
    if(name_of_metric == 'postImpressions'):
        return facebook_post_object.get_fb_post_impressions()
    elif(name_of_metric == 'engagedUsers'):
        return facebook_post_object.get_fb_post_engage_users()
    elif(name_of_metric == 'reactionsByType'):
        return facebook_post_object.get_fb_post_reactions_by_type_total()
    elif(name_of_metric == 'reactionLikes'):
        return facebook_post_object.get_fb_post_reactions_like_total()
    else:
        return facebook_post_object.get_fb_post_video_avg_time_watched()

def get_twitter_post_analytics(name_of_metric, firebase_table_id):
    #will get the post id and then run the specific function based on metric wanted
    post_info = get_post_information(firebase_table_id)
    post_title = post_info['title']
    post_description = post_info['text']
    media_type = post_info['fileType']#will need to store the media type on firebase!!
    post_id_fb = post_info['Twitter_post_id']
    twitter_post_object = twitter_post_analytics.twitter_post(post_description, post_title, media_type)
    twitter_post_object.set_twitter_post_id(post_id_fb)
    twitter_post_object.set_twitter_media_type(media_type)
    
    if(name_of_metric == 'retweetCount'):
        return twitter_post_object.retweet_counter()
    elif(name_of_metric == 'likeCount'):
        return twitter_post_object.like_counter()
    elif(name_of_metric == 'impressionCount'):
        return twitter_post_object.impression_counter()
    elif(name_of_metric == 'replyCount'):
        return twitter_post_object.reply_counter()
    elif(name_of_metric == 'urlClicks'):
        return twitter_post_object.url_link_clicks_twitter()
    elif(name_of_metric == 'userProfileClicks'):
        return twitter_post_object.user_profile_clicks_twitter()
    elif(name_of_metric == 'mediaQuartileCounter'):
        return twitter_post_object.media_quartile_counter_twitter()
    elif(name_of_metric == 'videoViewCount'):
        return twitter_post_object.video_view_count_twitter()
    else:
        return twitter_post_object.tweet_hashtags()

def get_insta_post_analytics(name_of_metric, firebase_table_id):
    #will get the post id and then run the specific function based on metric wanted
    post_info = get_post_information(firebase_table_id)
    post_title = post_info['title']
    post_description = post_info['text']
    media_type = post_info['fileType'] #will need to store the media type on firebase!!
    post_id_fb = post_info['Instagram_post_id']
    instagram_post_object = insta_post.insta_post(post_title, post_description, media_type)
    instagram_post_object.set_insta_post_id(post_id_fb)
    instagram_post_object.set_insta_media_type(media_type)

    if(name_of_metric == 'impressionCount'):
        return instagram_post_object.impression_counter()
    elif(name_of_metric == 'commentCount'):
        return instagram_post_object.comment_counter()
    elif(name_of_metric == 'likeCount'):
        return instagram_post_object.like_counter()
    else:
        return instagram_post_object.reach_counter()#For TESTING Purposes


#Create list to store dictionary elements
def post_specific_analytics_list_creator():
    """Returns dictionary of dictionaries, where key is uploadtimeID, and value is a dictionary element with all 13 post analytics data as key-value pairs"""
    postAnalyticsDict = dict()
    tableIds = get_fb_table_ids()
    for i in range(len(tableIds)):
        x = dict()
        post_information = get_post_information(tableIds[i])
        social_media_list = post_information['socialMedia']
        if ("facebookCheck" in social_media_list):
            x['postImpressions'] = 5#get_fb_post_analytics("postImpressions",tableIds[i])
            x['engagedUsers'] = 6#get_fb_post_analytics("engagedUsers",tableIds[i])
            x['reactionsByType'] = [7 ,1, 1, 4, 2, 6]#get_fb_post_analytics("reactionsByType",tableIds[i])
            x['reactionLikes'] = 8#get_fb_post_analytics("reactionLikes",tableIds[i])
        if ("twitterCheck" in social_media_list):
            x['retweetCount'] = 9#get_twitter_post_analytics('retweetCount', tableIds[i])
            x['twitterLikeCount'] = 10#get_twitter_post_analytics('likeCount',tableIds[i])
            x['replyCount'] = 11#get_twitter_post_analytics('replyCount', tableIds[i])
            x['twitterViews'] = 12#get_twitter_post_analytics('impressionCount',tableIds[i]) #returns list of hashtags?
            x['hashtags'] = ["#abc", "#bcd"]#get_twitter_post_analytics('hashtags', tableIds[i]) 
        if ("instagramCheck" in social_media_list):
            x['instagramViews'] = 13#get_insta_post_analytics('impressionCount', tableIds[i])
            x['commentCount'] = 14# get_insta_post_analytics('commentCount', tableIds[i])
            x['instagramLikeCount'] = 15#get_insta_post_analytics('likeCount', tableIds[i])
            x['accountReach'] = 16#get_insta_post_analytics('reachCount', tableIds[i])  
        #x has 13 key-value pairs
        #append x as one element in list and repeat for remaining table ids
        postAnalyticsDict[post_information['uploadTimeID']] = x
    return postAnalyticsDict



#Test for firebase_table_id retrieval 


#print("Table ids:", get_fb_table_ids())
#print("URLs:", get_media_url("<uploadID>))


