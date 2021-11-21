# Flask API Project
from flask import Flask, render_template, redirect, url_for, render_template, request
from fbOverall import fb_x_fnl, fb_y_fnl, ig_y_fnl
from igOverall import reach_x, reach_y, follower_x, follower_y
import firebase_connection
import fb_post_analytics
import insta_post
from datetime import datetime
import schedule
import time

app = Flask(__name__)


'''
Integration of Posting Feature
'''
@app.route('/', methods=['POST', 'GET'])
def post_to_platform():
    if (request.method == 'POST'):
        firebase_connection.publish_to_platform()
    return {"posted": True}
        



'''
Integration of Overall analytics page
'''
@app.route("/analytics") #used in TotalViews.js and FacebookOverall.js
def analytics():
    """Returns data to plot on FacebookOverall.js and TotalViews.js"""
    return {'engagement':sum(fb_y_fnl),
            'impressions':fb_post_analytics.get_fb_page_impressions_by_age_gender_unique(),
            'reach_x_labels':reach_x, 'reach_y_labels':reach_y, 'follower_x_labels':follower_x, 'follower_y_labels':follower_y,
            'fb_x_labels':fb_x_fnl, 'fb_y_labels':fb_y_fnl, 'ig_y_labels':ig_y_fnl,
            'post_analytics':firebase_connection.post_specific_analytics_list_creator()}
    #{'post test1_1628629828115': {'postImpressions': 100, 'engagedUsers': 6, 'reactionsByType': 7, 'reactionLikes': 100, 'retweetCount': 9, 'twitterLikeCount': 10, 'replyCount': 11, 'twitterViews': 12, 'hashtags': ['#abc', '#bcd'], 'instagramViews': 13, 'commentCount': 14, 'instagramLikeCount': 15, 'accountReach': 16}, 'ttt v2_1628665969542': {'postImpressions': 22, 'engagedUsers': 22, 'reactionsByType': 22, 'reactionLikes': 22, 'retweetCount': 22, 'twitterLikeCount': 22, 'replyCount': 22, 'twitterViews': 22, 'hashtags': ['#abc', '#bcd'], 'instagramViews': 33, 'commentCount': 22, 'instagramLikeCount': 22, 'accountReach': 22}}
    #What table ID to use above? What user? need for each post?


'''
Integration of Post specific Analytics
'''


if __name__ == "__main__":
    app.run()
