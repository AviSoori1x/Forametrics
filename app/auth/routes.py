from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email
#new stuff------------------------------------------------------
from app.models import  Post, FeedItem, Feeds, Bestdicts
import tweepy
#from credentials import*
import os
import json
#import facebook
import requests
#import feedparser
from dateutil import tz
from random import randint
import numpy as np
from collections import defaultdict
import calendar
from collections import Counter
import ast
import time
import datetime

#Flask dance stuff
#from flask_dance.contrib.twitter import make_twitter_blueprint, twitter

#import app

#scheduler = Scheduler(connection = Redis.from_url('redis://'))



def utc_to_local(datetimeobject):
    #the utc_zone
    utc_zone = tz.tzutc()
    local_zone = tz.tzlocal()
    utc = datetimeobject.replace(tzinfo=utc_zone)
    central = utc.astimezone(local_zone)
    return central

#@periodic_task(run_every=(crontab(minute='*/3')),name= "Twitter_optimal_hours" ,ignore_result=True)
#@celery.task
def Twitter_optimal_hours(uname):
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        tweepy_api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = tweepy_api.me().screen_name
        #These hours are utc
        follower_list = []
        #note that this username is a temporary fix while we have no oauth
        for user in tweepy.Cursor(tweepy_api.followers, screen_name=username).items():
            follower_list.append(user.screen_name)

        #Pick a hundred of these
        if len(follower_list)>100:
            nfollower_list = np.random.choice(follower_list, 100, replace=False)
        else:
            nfollower_list = follower_list
        #get a list of dates of the followers selected above
        date_list = []

        for name in nfollower_list:
            j = 0

            for status in tweepy.Cursor(tweepy_api.user_timeline, screen_name = name).items():
                if j< 3200:
                    date_list.append(utc_to_local(datetime.datetime.strptime((status._json['created_at']),'%a %b %d %H:%M:%S %z %Y')))
                    j += 1
                else:
                    break

            #Graceful handling? idk
        dates_dict = defaultdict(list)
        day_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
        for date in date_list:
            for day in day_list:
                if calendar.day_name[date.weekday()]== day:
                    dates_dict[day].append(date.hour)
        #Daily hour default dict
        Dhour_dict = defaultdict(list)
        for day in day_list:
            if len(set(dates_dict[day]))>=15:
                Dhour_dict[day]= [hour for hour, hour_count in Counter(dates_dict[day]).most_common(15)]
            else:
                Dhour_dict[day]= [hour for hour, hour_count in Counter(dates_dict[day]).most_common(len(set(dates_dict[day])))]


        sdict = str(dict(Dhour_dict))

        #insert_dic = Bestdicts(hourdic = str(sdict), socialnetwork = 'Twitter', user_id= username)
        insert_dic = Bestdicts(hourdic = str(sdict), socialnetwork = 'Twitter', user_username = uname)
        db.session.add(insert_dic)
        db.session.commit()
    except:
        dfdict = "{'Monday': [12, 17, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 9, 10, 11], 'Tuesday': [12, 17, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 9, 10, 11], 'Wednesday': [12, 17, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 9, 10, 11], 'Thursday': [12, 17, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 9, 10, 11], 'Friday': [12, 17, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 9, 10, 11], 'Saturday': [12, 17, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 9, 10, 11], 'Sunday': [12, 17, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 9, 10, 11]}"
        insert_dic = Bestdicts(hourdic = dfdict, socialnetwork = 'Twitter', user_username= uname)
        db.session.add(insert_dic)
        db.session.commit()
#try to closely replicate posts author and try ast with defaultdict
#------------------------------------------------------------------------------------------
#@periodic_task(run_every=(crontab(minute='*/2')),name= "Facebook_optimal_hours", ignore_result=True)
#@celery.task
def Facebook_optimal_hours(uname):
    try:
        token = 'EAAMHsSZAlbb0BAEBNsvuEmZBJ62fyNxjhpnhTupKh1pQGz5SdEkxNbL6Fih3eM8J9GDpXaW1jnHQMasxqZBhoKJAB3RgyVduCiBqsu8tFPjJdcmaBe6bHvQthrZAjY64qER3pNUS2m5674ujuPXrSZCgKPGC6XoG66OWQVhrsr2SM36bU5Q7w2xZAjFPeQkwwZD'
        graph = facebook.GraphAPI(access_token=token, version=2.7)
        all_fields = ['id','message','created_time','shares','likes.summary(true)','comments.summary(true)']
        all_fields = ','.join(all_fields)
        posts_page = graph.get_connections('1914278155313892', 'posts', fields=all_fields)
        #Get a breakdown of posts according to the hour of the day and the number of interractions
        dates_dict = defaultdict(list)
        day_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
        posts = []
        for post in posts_page['data']:
            #print(post['created_time'])
            date_utc = datetime.datetime.strptime((post['created_time']),'%Y-%m-%dT%H:%M:%S%z')
           #Local date
            date = utc_to_local(date_utc)
            days = calendar.day_name[date.weekday()]
            try:
                count_number = post['likes']['summary']['total_count']+post['comments']['summary']['total_count']+post['shares']['count']
            except:
                count_number = post['likes']['summary']['total_count']+post['comments']['summary']['total_count']
            for day in day_list:
                if calendar.day_name[date.weekday()]==day:
                    dates_dict[day].append(date.hour)
                    for i in range(count_number):
                        dates_dict[day].append(date.hour)

        hour_dict = defaultdict(list)
        for day in day_list:
            if len(set(dates_dict[day]))>=2:
                hour_dict[day]= [hour for hour, hour_count in Counter(dates_dict[day]).most_common(2)]
            else:
                hour_dict[day]= [hour for hour, hour_count in Counter(dates_dict[day]).most_common(1)]

        sdict = str(dict(hour_dict))

        insert_dic = Bestdicts(hourdic = str(sdict), socialnetwork = 'Facebook', user_username= uname)
        db.session.add(insert_dic)
        db.session.commit()
    except:
        dfdict = "{'Monday': [15, 13], 'Tuesday': [15, 13], 'Wednesday': [15, 13], 'Thursday': [15, 13], 'Friday': [15, 13], 'Saturday': [15, 13], 'Sunday': [15, 13]}"
        insert_dic = Bestdicts(hourdic = dfdict, socialnetwork = 'Facebook', user_username= uname)
        db.session.add(insert_dic)
        db.session.commit()
#------------------------------------------------------------------------------------------
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        #return redirect(next_page)
        return redirect('/twitter_login')
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #Twitter_optimal_hours.apply_async(args=[form.username.data])
        #Facebook_optimal_hours.apply_async(args=[form.username.data])
        user = User(username=form.username.data, email=form.email.data)
        #user = User(username=form.username.data, email=form.email.data, zip_code = form.zip_code.data,\
        #businessName=form.businessName.data, coreService=form.coreService.data,services=form.services.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
