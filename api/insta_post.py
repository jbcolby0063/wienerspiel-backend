import requests
import json
import time
import asyncio
import facebook
import pyshorteners
from firebase import firebase
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('../.env.local')
load_dotenv(dotenv_path=dotenv_path)

#only allows for one image post or 1 video post!
class insta_post:
    def __init__(self, post_title, post_description, media_type):
        url = os.getenv('REACT_APP_FIREBASE_DATABASE_URL')
        firebase_connection = firebase.FirebaseApplication(url, None)
        self.access = firebase_connection.get('/apikeys/facebook_instagram_api/facebook_instagram_api_key/','')
        self.graph_domain = 'https://graph.facebook.com/'
        self.graph_version = 'v10.0'
        self.endpoint_base = self.graph_domain + self.graph_version + '/'
        self.insta_account = "17841448226950067"
        self.response = None
        self.post_title = post_title
        self.post_description = post_description
        self.media_id = None
        self.media_type = media_type
        self.post_id = None
    
    def api_call(self, url, endpointParams, type):
        #conditional that posts the endpoints to the url specified
        if type == 'POST' : # post request
            data = requests.post( url,endpointParams)
        else : # get request
            data = requests.get( url, endpointParams )

        #stores the response information
        self.response = dict() # hold response info
        self.response['url'] = url # url we are hitting
        self.response['endpoint_params'] = endpointParams #parameters for the endpoint
        self.response['endpoint_params_pretty'] = json.dumps(endpointParams, indent= 4) # pretty print for cli
        self.response['json_data'] = json.loads(data.content) # response data from the api
        self.response['json_data_pretty'] = json.dumps(self.response['json_data'], indent= 4) # pretty print for cli

        return self.response # get and return content

    def get_media_ids(self, media_urls):
        url = self.endpoint_base + self.insta_account + '/media'

        endpointParams = dict()
        endpointParams['caption'] = self.post_description
        endpointParams['access_token'] = self.access
        
        #converting media urls
        s = pyshorteners.Shortener()
        url1 = s.chilpit.short(media_urls[0])

        if(self.media_type == 'image'):
            endpointParams['image_url'] = url1
        else:
            endpointParams['video_url'] = url1
            endpointParams['media_type'] = 'VIDEO'

        self.media_id = self.api_call(url, endpointParams, 'POST')['json_data']['id']

        return self.media_id
    
    def publish_post(self):
        url = self.endpoint_base + self.insta_account + '/media_publish'

        endpointParams = dict()
        endpointParams['creation_id'] = self.media_id
        endpointParams['access_token'] = self.access
        self.api_call(url, endpointParams, 'POST')
        time.sleep(30)
        get_url = self.endpoint_base + self.insta_account + '/media?access_token=' + self.access
        ids = requests.request('GET', get_url).json()
        self.post_id = ids['data'][0]['id']
        return self.post_id

    def set_insta_post_id(self, post_id):
        self.post_id = post_id
        return self.post_id
    
    def set_insta_media_type(self, media_type):
        self.media_type = media_type
        return self.media_type
    

    #analytics
    def impression_counter(self):
        url = 'https://graph.facebook.com/' + str(self.post_id) + '/insights?metric=impressions&access_token=' + self.access
        data = requests.request('GET', url).json()['data'][0]['values'][0]['value']
        return data
    
    def comment_counter(self):
        url = 'https://graph.facebook.com/v10.0/' + str(self.post_id) + '?fields=comments_count&access_token=' + self.access
        data = requests.request('GET', url).json()
        return data['comments_count']

    def like_counter(self):
        url = 'https://graph.facebook.com/v10.0/' + str(self.post_id) + '?fields=like_count&access_token=' + self.access
        data = requests.request('GET', url).json()
        return data['like_count']

    def reach_counter(self):
        url = 'https://graph.facebook.com/' + str(self.post_id) + '/insights?metric=reach&access_token=' + self.access
        data = requests.request('GET', url).json()['data'][0]['values'][0]['value']
        return data
    


#user account analytics
def get_access():
    url = os.getenv('REACT_APP_FIREBASE_DATABASE_URL')
    firebase_connection = firebase.FirebaseApplication(url, None)
    access = firebase_connection.get('/apikeys/facebook_instagram_api/facebook_instagram_api_key/','')
    return access

def get_insta_account_reach_count():
    access = get_access()
    url = 'https://graph.facebook.com/v10.0/17841448226950067/insights?metric=reach&period=week&fields=values&access_token=' + access
    info = requests.request('GET', url).json()
    return info['data'][0]['values'][1]['value']

def get_insta_account_follower_count(): #need a minimum of 100 followers in order to get data
    access = get_access()
    url = 'https://graph.facebook.com/v10.0/17841448226950067/insights?metric=follower_count&period=day&fields=values&access_token=' + access
    info = requests.request('GET', url).json()
    return info['data']

def get_insta_account_audience_country(): #need a minimum of 100 followers in order to get data
    access = get_access()
    url = 'https://graph.facebook.com/v10.0/17841448226950067/insights?metric=audience_country&period=lifetime&fields=values&access_token=' + access
    info = requests.request('GET', url).json()
    return info['data']

def get_insta_account_profile_views():
    access = get_access()
    url = 'https://graph.facebook.com/v10.0/17841448226950067/insights?metric=profile_views&period=day&fields=values&access_token=' + access
    info = requests.request('GET', url).json()
    print('info:', info)
    return info['data'][0]['values'][1]['value']


def get_insta_account_online_followers(): #need a minimum of 100 followers in order to get data
    access = get_access()
    url = 'https://graph.facebook.com/v10.0/17841448226950067/insights?metric=online_followers&period=lifetime&fields=values&access_token=' + access
    info = requests.request('GET', url).json()
    return info['data']

def get_insta_account_audience_gender_age(): #need a minimum of 100 followers in order to get data
    access = get_access()
    url = 'https://graph.facebook.com/v10.0/17841448226950067/insights?metric=audience_gender_age&period=lifetime&fields=values&access_token=' + access
    info = requests.request('GET', url).json()
    return info['data']
