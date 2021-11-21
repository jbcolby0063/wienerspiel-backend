import firebase
import fb_post_analytics
import insta_post
from datetime import datetime, timedelta
from firebase import firebase
import schedule
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env.local')
load_dotenv(dotenv_path=dotenv_path)

firebasePost = firebase.FirebaseApplication(os.getenv('REACT_APP_FIREBASE_DATABASE_URL'), None)
ig_data = {
    datetime.today().strftime("%d-%m-%y"): insta_post.get_insta_account_reach_count(),
}
fb_data = {
    datetime.today().strftime("%d-%m-%y"): fb_post_analytics.get_fb_daily_page_views_total()
}

def update_daily_views():
    firebasePost.post('ViewsGraph/FacebookOverall/totalViews', fb_data)
    firebasePost.post('ViewsGraph/InstagramOverall/totalViews', ig_data)

update_daily_views() #Call function to update daily views when needed

firebaseGet = firebase.FirebaseApplication(os.getenv('REACT_APP_FIREBASE_DATABASE_URL'), None)
fb_get = firebaseGet.get('ViewsGraph/FacebookOverall/totalViews', '')
ig_get = firebaseGet.get('ViewsGraph/InstagramOverall/totalViews', '')

fb_x = []
fb_y = []
ig_y = []

fb_x_fnl = []
fb_y_fnl = []
ig_y_fnl = []

for value in fb_get.values():
    for key,val in value.items():
        fb_x.append(key)
        fb_y.append(val)

for value in ig_get.values():
    for val in value.values():
        ig_y.append(val)



# if (len(fb_x) > 7):
#     # count_delete = len(fb_x) - 7
#     # del fb_x[:count_delete]
#     # del fb_y[:count_delete]
#     # del ig_y[:count_delete]
for n in reversed(range(7)): # last 7 days
    t = datetime.today() - timedelta(days=n)
    time_delta = t.strftime("%d-%m-%y")
    if time_delta in fb_x: # if time_delta value is in fb_x array
        last_index = len(fb_x) - fb_x[::-1].index(time_delta) - 1 # get last (recent) value that corresponds to time_delta
        fb_x_fnl.append(fb_x[last_index])
        fb_y_fnl.append(fb_y[last_index])
        ig_y_fnl.append(ig_y[last_index])
    else: # if time_delta value is not in fb_x array
        first_date = datetime.strptime(fb_x[0], "%d-%m-%y")
        current_date = datetime.strptime(time_delta, "%d-%m-%y")
        if first_date <= current_date and len(fb_x_fnl) > 0: # if the time_delta is after the starting point time, but its value is not in array, then just continue with the values in fnl 
            fb_x_fnl.append(time_delta)
            fb_y_fnl.append(fb_y_fnl[-1])
            ig_y_fnl.append(ig_y_fnl[-1])
        elif first_date <= current_date and len(fb_x_fnl) == 0: # if fnl array is empty, then search the recent time value before time_delta that is in fb_x
            while t.strftime("%d-%m-%y") not in fb_x:
                t -= timedelta(days=1)
            t_to_string = t.strftime("%d-%m-%y")
            lst_index = len(fb_x) - fb_x[::-1].index(t_to_string) - 1
            fb_x_fnl.append(time_delta)
            fb_y_fnl.append(fb_y[lst_index])
            ig_y_fnl.append(ig_y[lst_index])
        else: # if the time value of time_delta was before the starting point
            fb_x_fnl.append(time_delta)
            fb_y_fnl.append(0)
            ig_y_fnl.append(0)





# No longer used
""" firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

def update_daily_views():
    #Updates total Views for Instagram and Facebook Daily
    db.child("Instagram").child("totalViews").update({datetime.today().strftime("%d-%m-%y"): insta_post.get_insta_account_reach_count()})
    db.child("Facebook").child("totalViews").update({datetime.today().strftime("%d-%m-%y"): fb_post_analytics.get_fb_daily_page_views_total()})


fb_views = db.child("Facebook").child("totalViews").get().val()
ig_views = db.child("Instagram").child("totalViews").get().val()

fb_x = []
fb_y = []

ig_y = []

for key,value in fb_views.items():
    fb_x.append(key)
    fb_y.append(value)

for key,value in ig_views.items(): 
    ig_y.append(value)
 """
#Obtained fb_data and ig_data as list of x,y pairs

#Schedule code to update
""" 
schedule.every().day.at("04:00").do(update_daily_views)
while True:
    schedule.run_pending()
    time.sleep(1) """

#update_daily_views()


            
