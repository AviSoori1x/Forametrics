import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, json, session
#For the app context issue
from flask import Flask
#------------------------------
from flask_login import current_user, login_required
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, FeedEnterForm, SmartPostForm, analyticsForm
from app.models import User, Post, FeedItem, Feeds, Bestdicts, FacebookAnalytics, TwitterAnalytics, Twittertokens, Facebooktokens
from app.main import bp
#from celery import Celery
import dateutil.parser as dateparser
import time
#from credentials import*
import tweepy
#This is the difficult part
#from app import celery
import os
import json
import gc
#This was imported as facebook, changed it to 'import facebook as fb'
#import facebook as fb
import requests
#import feedparser
#from celery.task.schedules import crontab
#from celery.decorators import periodic_task
from dateutil import tz
from random import randint
import numpy as np
from collections import defaultdict
import calendar
from collections import Counter
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
import ast
import random
import pandas as pd
import io
import re
from collections import OrderedDict
from jinja2 import Template

from bokeh.embed import components
from bokeh.models import Range1d
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.browser import view
from bokeh.sampledata.iris import flowers
import vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#------Flask-Dance libraries and shit
from flask import redirect, url_for
#from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
#from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#---Facebook oauth-------
# Credentials you get from registering a new application
from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth, OAuthException
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from rauth import OAuth1Service, OAuth2Service
#from flask_oauth import OAuth
from rasa_nlu.model import Metadata, Interpreter
import geopy.geocoders
from geopy.geocoders import Nominatim
import certifi
import ssl
import parsedatetime as pdt
import twitter_text
import operator
from operator import itemgetter
from word2number import w2n
from nltk.tokenize import TweetTokenizer
from dateutil import rrule
import re
import psutil

consumer_key   = '**'
consumer_secret = '**'
# A function for computing lexical diversity
def lexical_diversity(tokens):
    return len(set(tokens))/len(tokens)
# A function for computing the average number of words per tweet
def average_words(statuses):
    total_words = sum([ len(s.split()) for s in statuses ])
    return total_words/len(statuses)

def endstart_dates(start_date_string, end_date_string):
    cal = pdt.Calendar()
    now = datetime.datetime.now()
    start_date = cal.parseDT(start_date_string, now)[0]

    cal = pdt.Calendar()
    now = datetime.datetime.now()
    end_date = cal.parseDT(end_date_string, now)[0]
    return start_date, end_date


#Analytics functions Twitter--------------------------------------------------------

def TwitEngPlot(start_date, end_date, handle, types, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    intent = 'engagement_Twitter_type'
    #-----------------------------
    dates_dict_urls = {}
    dates_dict_hashtags = {}
    dates_dict_usermentions = {}
    dates_dict_symbols = {}
    dates_dict_plaintext = {}
    for dt in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
        dates_dict_urls[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_hashtags[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_usermentions[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_symbols[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_plaintext[dt.strftime('%Y-%m-%d')] = 0
    #-----------------------------
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]


    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0

    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []

    urlsEng = []
    hashtagsEng = []
    symbolsEng = []
    plainTextEng = []
    userMentionsEng = []
    #------
    page = 1
    while True:
        statuses = api.user_timeline(handle, page=page, wait_on_rate_limit = True)
        if statuses:
            for status in statuses:
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                if (created_naive >= start_date) and (created_naive <= end_date):
                    status_list.append(status)
                    dates_list.append(created_naive)

                else:
                    pass
        else:
            break
        page += 1  # next page
    if len(dates_list) == 0:
        return {}, ['Sorry, No activity was registered during that time period to analyze']
    else:
        new_start_date = dates_list[0]
        new_end_date = dates_list[-1]
        inter_date = new_start_date

        while inter_date <= new_end_date:
            engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
            inter_date += datetime.timedelta(days=1)
        engagement_text = []

        for status in status_list:
            txt = status.text
            ex = twitter_text.Extractor(txt)

            number += 1
            created_time = status.created_at
            created_datetime = created_time
            created_naive = created_datetime.replace(tzinfo=None)
            dates_list.append(created_naive)

            #difference = (naive-created_naive).days
            #if difference < 21:
            if (created_naive >= start_date) and (created_naive <= end_date):

                datekey = created_naive.strftime('%Y-%m-%d')
                #print(key)
                #key  = created_naive
                text = status.text
                #retweets


                #favorites
                favorites_num = status.favorite_count
                #print("Number of favorites is: {}".format(favorites_num))

                #engagement
                firstTwo = list(text)[:2]
                #Now figure out a way to see which ones are real retweets, not some coupon or something
                #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
                n_tweets +=1
                n_favorites += status.favorite_count
                if firstTwo == ['R','T']:
                    n_retweets += 0

                    retweet_num = 0
                    #print("Number of retweets is: {}".format(retweet_num))
                    engagement_num = (status.favorite_count)

                    n_engagement +=  engagement_num

                    if (len(status.entities['urls']) !=0  or len(ex.extract_urls()) != 0):
                        urls_eng += engagement_num
                        dates_dict_urls[datekey] += engagement_num
                    if (len(status.entities['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                        hashtags_eng += engagement_num
                        dates_dict_hashtags[datekey] += engagement_num
                    if (len(status.entities['user_mentions']) !=0  or len(ex.extract_mentioned_screen_names()) != 0):
                        user_mentions_eng += engagement_num
                        dates_dict_usermentions[datekey] += engagement_num
                    if len(status.entities['symbols']) !=0:
                        symbols_eng += engagement_num
                        dates_dict_symbols[datekey] += engagement_num

                    if ((len(status.entities['urls']) ==0  or len(ex.extract_urls()) == 0) and (len(status.entities['hashtags']) ==0  or len(ex.extract_hashtags()) == 0) and (len(status.entities['user_mentions']) ==0  or len(ex.extract_mentioned_screen_names()) == 0) and len(status.entities['symbols']) ==0):
                        plain_text_eng += engagement_num
                        dates_dict_plaintext[datekey] += engagement_num
                    #if (('media' in status.entities) or ('symbol' in status.entities) or (len(ex.extract_urls()) != 0) or (len(ex.extract_hashtags()) != 0) or (len(ex.extract_mentioned_screen_names()) != 0)):
                    #    plain_text_eng += engagement_num
                else:
                    n_retweets += status.retweet_count

                    retweet_num = status.retweet_count
                    #print("Number of retweets is: {}".format(retweet_num))
                    engagement_num = (status.favorite_count + status.retweet_count)
                    n_engagement += engagement_num

                    if (len(status.entities['urls']) !=0  or len(ex.extract_urls()) != 0):
                        urls_eng += engagement_num
                        dates_dict_urls[datekey] += engagement_num
                    if (len(status.entities['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                        hashtags_eng += engagement_num
                        dates_dict_hashtags[datekey] += engagement_num
                    if (len(status.entities['user_mentions']) !=0  or len(ex.extract_mentioned_screen_names()) != 0):
                        user_mentions_eng += engagement_num
                        dates_dict_usermentions[datekey] += engagement_num
                    if len(status.entities['symbols']) !=0:
                        symbols_eng += engagement_num
                        dates_dict_symbols[datekey] += engagement_num
                    if ((len(status.entities['urls']) ==0  or len(ex.extract_urls()) == 0) and (len(status.entities['hashtags']) ==0  or len(ex.extract_hashtags()) == 0) and (len(status.entities['user_mentions']) ==0  or len(ex.extract_mentioned_screen_names()) == 0) and len(status.entities['symbols']) ==0):
                        plain_text_eng += engagement_num
                        dates_dict_plaintext[datekey] += engagement_num
                    #if (('media' in status.entities) or ('symbol' in status.entities) or (len(ex.extract_urls()) != 0) or (len(ex.extract_hashtags()) != 0) or (len(ex.extract_mentioned_screen_names()) != 0)):
                        #plain_text_eng += engagement_num
            else:
                pass



    engbytype_dict = {'hashtags':hashtags_eng,'urls': urls_eng, 'user mentions':user_mentions_eng, 'plain text':plain_text_eng}
    if n_engagement != 0 :
        engtypepercent = {'hashtags': (hashtags_eng*100)/n_engagement,'urls': (urls_eng*100)/n_engagement, 'user mentions':(user_mentions_eng*100)/n_engagement, 'plain text':(plain_text_eng*100)/n_engagement}
    else:
        engtypepercent = {'hashtags': 0,'urls': 0, 'user mentions':0, 'plain text':0}


    result = 'The engagement for tweets with {} is {}, which is {}% of all engagements on {}. '.format(types, engbytype_dict[types], round(engtypepercent[types],2), handle)
    dateDicts = {'urls': dates_dict_urls, 'hashtags': dates_dict_hashtags, 'user mentions': dates_dict_usermentions, 'symbols': dates_dict_symbols, 'plain text': dates_dict_plaintext}

    #return intent, plot_list[types], result
    return dateDicts[types], result

def ongoing():
    return 'return status'

def TwitCompareEngType(start_date, end_date, handle1, handle2, types, consumer_key, consumer_secret):
    try:
        engagement_dict, result1 = TwitEngPlot(start_date, end_date, handle1, types, consumer_key, consumer_secret)
        engagement_dict2, result2 = TwitEngPlot(start_date, end_date, handle2, types, consumer_key, consumer_secret)
        result = [result1, result2]
        handle1_string = 'engagement for {} (tweets with {})'.format(handle1, types)
        handle2_string = 'engagement for {} (tweets with {})'.format(handle2, types)
        intent = 'TwitterEngagement'
        title_list = [['dates',handle1_string, handle2_string]]
        final_dates = sorted(set(list(engagement_dict.keys())+ list(engagement_dict2.keys())))
        intent ='eng_comparison'
        plot = []
        for date in final_dates:
            if date in engagement_dict.keys() and date in engagement_dict2.keys():
                plot.append([date, engagement_dict[date], engagement_dict2[date]])
            elif date not in engagement_dict.keys() and date in engagement_dict2.keys():
                plot.append([date, 0 ,engagement_dict2[date]])
            elif date in engagement_dict.keys() and date not in engagement_dict2.keys():
                plot.append([date, engagement_dict[date] ,0])
            else:
                plot.append([date, 0,0])
        plot.pop()
        return intent, plot, result
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']


def TwitterEngagementComparison(start_date, end_date, handle1, handle2, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    ts = time.time()
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]
    username  = api.me().screen_name

    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0
    n_engagement2 = 0

    number =0
    number2= 0
    engagement_dict = {}
    dates_list = []
    status_list = []

    engagement_dict2 = {}
    dates_list2 = []
    status_list2 = []
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(handle1, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page

        page = 1
        while True:
            statuses2 = api.user_timeline(handle2, page=page, wait_on_rate_limit = True)
            if statuses2:
                for status in statuses2:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list2.append(status)
                        dates_list2.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page

        if len(dates_list) == 0 and len(dates_list2) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date

            while inter_date <= end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []
            for status in status_list:

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list.append(created_naive)

                #difference = (naive-created_naive).days
                #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):

                    key = created_naive.strftime('%Y-%m-%d')
                    #print(key)
                    #key  = created_naive
                    text = status.text
                    #retweets


                    #favorites
                    favorites_num = status.favorite_count
                    #print("Number of favorites is: {}".format(favorites_num))

                    #engagement
                    firstTwo = list(text)[:2]
                    #Now figure out a way to see which ones are real retweets, not some coupon or something
                    #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
                    n_tweets +=1
                    n_favorites += status.favorite_count
                    if firstTwo == ['R','T']:
                        n_retweets += 0

                        retweet_num = 0
                        engagement_num = (status.favorite_count)

                        n_engagement +=  engagement_num


                    else:
                        n_retweets += status.retweet_count

                        retweet_num = status.retweet_count
                        engagement_num = (status.favorite_count + status.retweet_count)
                        n_engagement += engagement_num


                    if key in engagement_dict.keys():
                        engagement_dict[key] += engagement_num
                    else:
                        engagement_dict[key] = engagement_num

                else:
                    pass
                first_item = itemgetter(0)
                new_list = sorted(engagement_text, key = first_item)

                statuses_n = []
                reversed_list = new_list[::-1]
                i=0
                while i<10:
                    try:
                        statuses_n.append(reversed_list[i])
                    except:
                        break
                    i +=1

            for status in status_list2:

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list2.append(created_naive)

                #difference = (naive-created_naive).days
                #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):

                    key = created_naive.strftime('%Y-%m-%d')
                    #print(key)
                    #key  = created_naive
                    text = status.text
                    #retweets


                    #favorites
                    favorites_num = status.favorite_count
                    #print("Number of favorites is: {}".format(favorites_num))

                    #engagement
                    firstTwo = list(text)[:2]
                    #Now figure out a way to see which ones are real retweets, not some coupon or something
                    #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
                    n_tweets +=1
                    n_favorites += status.favorite_count
                    if firstTwo == ['R','T']:
                        n_retweets += 0

                        retweet_num = 0
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count)
                        #print("Engagement for tweet: {}".format(engagement_num))

                        n_engagement2 +=  engagement_num


                    else:
                        n_retweets += status.retweet_count

                        retweet_num = status.retweet_count
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count + status.retweet_count)
                        n_engagement2 += engagement_num


                    if key in engagement_dict2.keys():
                        engagement_dict2[key] += engagement_num
                    else:
                        engagement_dict2[key] = engagement_num
                else:
                    pass

        handle1_string = 'engagement for {}'.format(handle1)
        handle2_string = 'engagement for {}'.format(handle2)

        eng_string = 'The engagement for {} from {} to {} was: {}'.format(handle1, start_date, end_date, n_engagement)
        eng_string2 = 'The engagement for {} from {} to {} was: {}'.format(handle2, start_date, end_date, n_engagement2)
        comparison = [eng_string, eng_string2]

        title_list = [['dates',handle1_string, handle2_string]]
        final_dates = sorted(set(list(engagement_dict.keys())+ list(engagement_dict2.keys())))
        plot = []
        for date in final_dates:
            if date in engagement_dict.keys() and date in engagement_dict2.keys():
                plot.append([date, engagement_dict[date], engagement_dict2[date]])
            elif date not in engagement_dict.keys() and date in engagement_dict2.keys():
                plot.append([date, 0 ,engagement_dict2[date]])
            elif date in engagement_dict.keys() and date not in engagement_dict2.keys():
                plot.append([date, engagement_dict[date] ,0])
            else:
                plot.append([date, 0,0])

        final_dict = title_list + plot
        te = time.time()
        duration  = te-ts
        intent = 'eng_comparison'
        return intent, final_dict, comparison
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']

def wordydiversityOwn(start_date, end_date, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]



    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)


    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    n = 0
    total_diversity = 0
    total_words = 0
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(username, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date
            tknzr = TweetTokenizer()

            for status in status_list:
                txt = status.text
                if (created_naive >= start_date) and (created_naive <= end_date):
                    n +=1
                    words = tknzr.tokenize(tweet)
                    total_diversity += lexical_diversity(words)
                    total_words += len(words)


        diversity = total_diversity/n
        word_average = total_words/n
        statement = 'The lexical diversity of the tweets during that time period was {} and average number of words per status was {}. Higher lexical diversity indicates the use of a rich vocabulary in expressing ideas or news, and is usually a good sign.'.format(diversity, word_average)
        intent = 'wordydiversity'
        return intent, statement
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']

def wordydiversityOther(start_date, end_date, handle, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]


    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)


    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    n = 0
    total_diversity = 0
    total_words = 0
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(handle, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date
            tknzr = TweetTokenizer()

            for status in status_list:
                txt = status.text
                if (created_naive >= start_date) and (created_naive <= end_date):
                    n +=1
                    words = tknzr.tokenize(tweet)
                    total_diversity += lexical_diversity(words)
                    total_words += len(words)


        diversity = total_diversity/n
        word_average = total_words/n
        statement = 'The lexical diversity of the tweets during that time period was {} and average number of words per status was {}.Higher lexical diversity indicates that the use of a rich vocabulary in expressing ideas or news, and is usually a good sign.'.format(diversity, word_average)
        intent = 'wordydiversity'
        return intent, statement
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']

def TwitOwnEngbyTypePlot(start_date, end_date,types, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)

    #-----------------------------
    dates_dict_urls = {}
    dates_dict_hashtags = {}
    dates_dict_usermentions = {}
    dates_dict_symbols = {}
    dates_dict_plaintext = {}
    for dt in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
        dates_dict_urls[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_hashtags[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_usermentions[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_symbols[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_plaintext[dt.strftime('%Y-%m-%d')] = 0
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]


    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0

    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []

    urlsEng = []
    hashtagsEng = []
    symbolsEng = []
    plainTextEng = []
    userMentionsEng = []
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(username, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date

            while inter_date <= new_end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            for status in status_list:
                txt = status.text
                ex = twitter_text.Extractor(txt)

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list.append(created_naive)

                #difference = (naive-created_naive).days
                #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):

                    datekey = created_naive.strftime('%Y-%m-%d')
                    #print(key)
                    #key  = created_naive
                    text = status.text
                    #retweets


                    #favorites
                    favorites_num = status.favorite_count
                    #print("Number of favorites is: {}".format(favorites_num))

                    #engagement
                    firstTwo = list(text)[:2]
                    #Now figure out a way to see which ones are real retweets, not some coupon or something
                    #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
                    n_tweets +=1
                    n_favorites += status.favorite_count
                    if firstTwo == ['R','T']:
                        n_retweets += 0

                        retweet_num = 0
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count)

                        n_engagement +=  engagement_num

                        if (len(status.entities['urls']) !=0  or len(ex.extract_urls()) != 0):
                            urls_eng += engagement_num
                            dates_dict_urls[datekey] += engagement_num
                        if (len(status.entities['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                            hashtags_eng += engagement_num
                            dates_dict_hashtags[datekey] += engagement_num
                        if (len(status.entities['user_mentions']) !=0  or len(ex.extract_mentioned_screen_names()) != 0):
                            user_mentions_eng += engagement_num
                            dates_dict_usermentions[datekey] += engagement_num
                        if len(status.entities['symbols']) !=0:
                            symbols_eng += engagement_num
                            dates_dict_symbols[datekey] += engagement_num

                        if ((len(status.entities['urls']) ==0  or len(ex.extract_urls()) == 0) and (len(status.entities['hashtags']) ==0  or len(ex.extract_hashtags()) == 0) and (len(status.entities['user_mentions']) ==0  or len(ex.extract_mentioned_screen_names()) == 0) and len(status.entities['symbols']) ==0):
                            plain_text_eng += engagement_num
                            dates_dict_plaintext[datekey] += engagement_num
                        #if (('media' in status.entities) or ('symbol' in status.entities) or (len(ex.extract_urls()) != 0) or (len(ex.extract_hashtags()) != 0) or (len(ex.extract_mentioned_screen_names()) != 0)):
                        #    plain_text_eng += engagement_num
                    else:
                        n_retweets += status.retweet_count

                        retweet_num = status.retweet_count
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count + status.retweet_count)
                        n_engagement += engagement_num

                        if (len(status.entities['urls']) !=0  or len(ex.extract_urls()) != 0):
                            urls_eng += engagement_num
                            dates_dict_urls[datekey] += engagement_num
                        if (len(status.entities['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                            hashtags_eng += engagement_num
                            dates_dict_hashtags[datekey] += engagement_num
                        if (len(status.entities['user_mentions']) !=0  or len(ex.extract_mentioned_screen_names()) != 0):
                            user_mentions_eng += engagement_num
                            dates_dict_usermentions[datekey] += engagement_num
                        if len(status.entities['symbols']) !=0:
                            symbols_eng += engagement_num
                            dates_dict_symbols[datekey] += engagement_num
                        if ((len(status.entities['urls']) ==0  or len(ex.extract_urls()) == 0) and (len(status.entities['hashtags']) ==0  or len(ex.extract_hashtags()) == 0) and (len(status.entities['user_mentions']) ==0  or len(ex.extract_mentioned_screen_names()) == 0) and len(status.entities['symbols']) ==0):
                            plain_text_eng += engagement_num
                            dates_dict_plaintext[datekey] += engagement_num
                        #if (('media' in status.entities) or ('symbol' in status.entities) or (len(ex.extract_urls()) != 0) or (len(ex.extract_hashtags()) != 0) or (len(ex.extract_mentioned_screen_names()) != 0)):
                            #plain_text_eng += engagement_num
                else:
                    pass

        engbytype_dict = {'hashtags eng':hashtags_eng,'urls eng': urls_eng, 'user_mentions eng':user_mentions_eng, 'plain text eng':plain_text_eng}
        if n_engagement != 0 :
            engtypepercent = {'hashtags': (hashtags_eng*100)/n_engagement,'urls': (urls_eng*100)/n_engagement, 'user mentions':(user_mentions_eng*100)/n_engagement, 'plain text':(plain_text_eng*100)/n_engagement}
        else:
            engtypepercent = {'hashtags': 0,'urls': 0, 'user mentions':0, 'plain text':0}


        te = time.time()
        duration  = te-ts

        for key, value in dates_dict_urls.items():
            urlsEng.append([key,value])

        for key, value in dates_dict_hashtags.items():
            hashtagsEng.append([key,value])

        for key, value in dates_dict_usermentions.items():
            userMentionsEng.append([key,value])

        for key, value in dates_dict_symbols.items():
            symbolsEng.append([key,value])

        for key, value in dates_dict_plaintext.items():
            plainTextEng.append([key,value])

        #print('Total engagement is: {}'.format(n_engagement*n_followers))
        url_title_list = [['dates','url engagement']]
        url_final_list = url_title_list + urlsEng

        hashtags_title_list = [['dates','hashtags engagement']]
        hashtags_final_list = hashtags_title_list + hashtagsEng

        userMentions_title_list = [['dates','User Mentions engagement']]
        userMentions_final_list = userMentions_title_list + userMentionsEng

        symbols_title_list = [['dates','symbols engagement']]
        symbols_final_list = symbols_title_list + symbolsEng

        plainText_title_list = [['dates','plain text engagement']]
        plainText_final_list = plainText_title_list + plainTextEng

        plot_list =  {'hashtags':hashtags_final_list,'urls': url_final_list, 'user mentions':userMentions_final_list, 'plain text':plainText_final_list}

        engbytype_dict = {'hashtags':hashtags_eng,'urls': urls_eng, 'user mentions':user_mentions_eng, 'plain text':plain_text_eng}
        if n_engagement != 0 :
            engtypepercent = {'hashtags': (hashtags_eng*100)/n_engagement,'urls': (urls_eng*100)/n_engagement, 'user mentions':(user_mentions_eng*100)/n_engagement, 'plain text':(plain_text_eng*100)/n_engagement}
        else:
            engtypepercent = {'hashtags': 0,'urls': 0, 'user mentions':0, 'plain text':0}


        result = 'The engagement for tweets with {} is {}, which is {}% of all engagements'.format(types, engbytype_dict[types], round(engtypepercent[types], 2))
        intent = 'engagement_Twitter_type'
        return intent, plot_list[types], result
        #return url_final_list, hashtags_final_list, userMentions_final_list, symbols_final_list, plainText_final_list

    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']


def TwitOtherEngbyTypePlot(start_date, end_date, handle, types, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)

    #-----------------------------
    dates_dict_urls = {}
    dates_dict_hashtags = {}
    dates_dict_usermentions = {}
    dates_dict_symbols = {}
    dates_dict_plaintext = {}
    for dt in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
        dates_dict_urls[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_hashtags[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_usermentions[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_symbols[dt.strftime('%Y-%m-%d')] = 0
        dates_dict_plaintext[dt.strftime('%Y-%m-%d')] = 0
    #-----------------------------
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0

    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []

    urlsEng = []
    hashtagsEng = []
    symbolsEng = []
    plainTextEng = []
    userMentionsEng = []
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(handle, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date

            while inter_date <= new_end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            for status in status_list:
                txt = status.text
                ex = twitter_text.Extractor(txt)

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list.append(created_naive)

                #difference = (naive-created_naive).days
                #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):

                    datekey = created_naive.strftime('%Y-%m-%d')
                    #print(key)
                    #key  = created_naive
                    text = status.text
                    #retweets


                    #favorites
                    favorites_num = status.favorite_count
                    #print("Number of favorites is: {}".format(favorites_num))

                    #engagement
                    firstTwo = list(text)[:2]
                    #Now figure out a way to see which ones are real retweets, not some coupon or something
                    #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
                    n_tweets +=1
                    n_favorites += status.favorite_count
                    if firstTwo == ['R','T']:
                        n_retweets += 0

                        retweet_num = 0
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count)

                        n_engagement +=  engagement_num

                        if (len(status.entities['urls']) !=0  or len(ex.extract_urls()) != 0):
                            urls_eng += engagement_num
                            dates_dict_urls[datekey] += engagement_num
                        if (len(status.entities['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                            hashtags_eng += engagement_num
                            dates_dict_hashtags[datekey] += engagement_num
                        if (len(status.entities['user_mentions']) !=0  or len(ex.extract_mentioned_screen_names()) != 0):
                            user_mentions_eng += engagement_num
                            dates_dict_usermentions[datekey] += engagement_num
                        if len(status.entities['symbols']) !=0:
                            symbols_eng += engagement_num
                            dates_dict_symbols[datekey] += engagement_num

                        if ((len(status.entities['urls']) ==0  or len(ex.extract_urls()) == 0) and (len(status.entities['hashtags']) ==0  or len(ex.extract_hashtags()) == 0) and (len(status.entities['user_mentions']) ==0  or len(ex.extract_mentioned_screen_names()) == 0) and len(status.entities['symbols']) ==0):
                            plain_text_eng += engagement_num
                            dates_dict_plaintext[datekey] += engagement_num
                        #if (('media' in status.entities) or ('symbol' in status.entities) or (len(ex.extract_urls()) != 0) or (len(ex.extract_hashtags()) != 0) or (len(ex.extract_mentioned_screen_names()) != 0)):
                        #    plain_text_eng += engagement_num
                    else:
                        n_retweets += status.retweet_count

                        retweet_num = status.retweet_count
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count + status.retweet_count)
                        n_engagement += engagement_num

                        if (len(status.entities['urls']) !=0  or len(ex.extract_urls()) != 0):
                            urls_eng += engagement_num
                            dates_dict_urls[datekey] += engagement_num
                        if (len(status.entities['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                            hashtags_eng += engagement_num
                            dates_dict_hashtags[datekey] += engagement_num
                        if (len(status.entities['user_mentions']) !=0  or len(ex.extract_mentioned_screen_names()) != 0):
                            user_mentions_eng += engagement_num
                            dates_dict_usermentions[datekey] += engagement_num
                        if len(status.entities['symbols']) !=0:
                            symbols_eng += engagement_num
                            dates_dict_symbols[datekey] += engagement_num
                        if ((len(status.entities['urls']) ==0  or len(ex.extract_urls()) == 0) and (len(status.entities['hashtags']) ==0  or len(ex.extract_hashtags()) == 0) and (len(status.entities['user_mentions']) ==0  or len(ex.extract_mentioned_screen_names()) == 0) and len(status.entities['symbols']) ==0):
                            plain_text_eng += engagement_num
                            dates_dict_plaintext[datekey] += engagement_num
                        #if (('media' in status.entities) or ('symbol' in status.entities) or (len(ex.extract_urls()) != 0) or (len(ex.extract_hashtags()) != 0) or (len(ex.extract_mentioned_screen_names()) != 0)):
                            #plain_text_eng += engagement_num
                else:
                    pass

        engbytype_dict = {'hashtags eng':hashtags_eng,'urls eng': urls_eng, 'user_mentions eng':user_mentions_eng, 'plain text eng':plain_text_eng}
        if n_engagement != 0 :
            engtypepercent = {'hashtags': (hashtags_eng*100)/n_engagement,'urls': (urls_eng*100)/n_engagement, 'user mentions':(user_mentions_eng*100)/n_engagement, 'plain text':(plain_text_eng*100)/n_engagement}
        else:
            engtypepercent = {'hashtags': 0,'urls': 0, 'user mentions':0, 'plain text':0}



        for key, value in dates_dict_urls.items():
            urlsEng.append([key,value])

        for key, value in dates_dict_hashtags.items():
            hashtagsEng.append([key,value])

        for key, value in dates_dict_usermentions.items():
            userMentionsEng.append([key,value])

        for key, value in dates_dict_symbols.items():
            symbolsEng.append([key,value])

        for key, value in dates_dict_plaintext.items():
            plainTextEng.append([key,value])

        #print('Total engagement is: {}'.format(n_engagement*n_followers))
        url_title_list = [['dates','url engagement']]
        url_final_list = url_title_list + urlsEng

        hashtags_title_list = [['dates','hashtags engagement']]
        hashtags_final_list = hashtags_title_list + hashtagsEng

        userMentions_title_list = [['dates','User Mentions engagement']]
        userMentions_final_list = userMentions_title_list + userMentionsEng

        symbols_title_list = [['dates','symbols engagement']]
        symbols_final_list = symbols_title_list + symbolsEng

        plainText_title_list = [['dates','plain text engagement']]
        plainText_final_list = plainText_title_list + plainTextEng

        plot_list =  {'hashtags':hashtags_final_list,'urls': url_final_list, 'user mentions':userMentions_final_list, 'plain text':plainText_final_list}

        engbytype_dict = {'hashtags':hashtags_eng,'urls': urls_eng, 'user mentions':user_mentions_eng, 'plain text':plain_text_eng}
        if n_engagement != 0 :
            engtypepercent = {'hashtags': (hashtags_eng*100)/n_engagement,'urls': (urls_eng*100)/n_engagement, 'user mentions':(user_mentions_eng*100)/n_engagement, 'plain text':(plain_text_eng*100)/n_engagement}
        else:
            engtypepercent = {'hashtags': 0,'urls': 0, 'user mentions':0, 'plain text':0}

        result = 'The engagement for tweets with {} is {}, which is {}% of all engagements on {}. '.format(types, engbytype_dict[types], round(engtypepercent[types],2), handle)
        intent = 'engagement_Twitter_type'
        return intent, plot_list[types], result

    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']


def FollowerCountsOther(handle, consumer_key, consumer_secret):
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        user = api.get_user(handle)
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

    friends = user.friends_count
    followers = user.followers_count
    result1 = 'while {} has a total of {} friends. '.format(handle, friends)
    result2 = ' There are a total of {} followers following {},'.format(followers,handle)
    result3 = result2+' '+result1
    intent = "Twit_follower_count"
    title_list = [['Category','Count']]#just like dates and engagement
    list_of_lists = [['Followers', followers],['Friends', friends]]
    final_dict = title_list + list_of_lists

    try:
        return [intent, result3, final_dict]
    except:
        return [intent, 'There was an error in answering your query. Could you please rephrase your question with all the required information?']

def FollowerCountsOwn(consumer_key, consumer_secret):
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

    user = api.get_user(username)
    friends = user.friends_count
    followers = user.followers_count
    result1 = 'Your account has a total of {} friends and'.format(friends)
    result2 = '{} followers'.format(followers)
    result3 = result1+' '+result2
    intent = "Twit_follower_count"
    title_list = [['Category','Count']]#just like dates and engagement
    list_of_lists = [['Followers', followers],['Friends', friends]]
    final_dict = title_list + list_of_lists

    try:
        return [intent, result3, final_dict]
    except:
        return [intent, 'There was an error in answering your query. Could you please rephrase your question with all the required information?']

def TopTweetsOther(start_date, end_date, n, handle, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    ts = time.time()
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0

    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(handle, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date

            while inter_date <= end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            for status in status_list:
                txt = status.text
                ex = twitter_text.Extractor(txt)

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list.append(created_naive)

                #difference = (naive-created_naive).days
                #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):

                    key = created_naive.strftime('%Y-%m-%d')
                    #print(key)
                    #key  = created_naive
                    text = status.text
                    #retweets


                    #favorites
                    favorites_num = status.favorite_count
                    #print("Number of favorites is: {}".format(favorites_num))

                    #engagement
                    firstTwo = list(text)[:2]
                    #Now figure out a way to see which ones are real retweets, not some coupon or something
                    #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
                    n_tweets +=1
                    n_favorites += status.favorite_count
                    if firstTwo == ['R','T']:
                        n_retweets += 0

                        retweet_num = 0
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count)
                        #print("Engagement for tweet: {}".format(engagement_num))

                        n_engagement +=  engagement_num


                    else:
                        n_retweets += status.retweet_count

                        retweet_num = status.retweet_count
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count + status.retweet_count)
                        n_engagement += engagement_num

                    engagement_text.append([status.text,' total engagement: ',engagement_num])
                else:
                    pass
                first_item = itemgetter(2)
                new_list = sorted(engagement_text, key = first_item)

                statuses_n = []
                reversed_list = new_list[::-1]
                i=0
                while i<n:
                    try:
                        statuses_n.append(reversed_list[i])
                    except:
                        break
                    i +=1

        intent = 'tophashcomments'
        return intent, statuses_n
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']

def TopTweetsOwn(start_date, end_date, n, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    ts = time.time()
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]


    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0

    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(username, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date

            while inter_date <= end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            for status in status_list:
                txt = status.text
                ex = twitter_text.Extractor(txt)

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list.append(created_naive)

                #difference = (naive-created_naive).days
                #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):

                    key = created_naive.strftime('%Y-%m-%d')
                    #print(key)
                    #key  = created_naive
                    text = status.text
                    #retweets


                    #favorites
                    favorites_num = status.favorite_count
                    #print("Number of favorites is: {}".format(favorites_num))

                    #engagement
                    firstTwo = list(text)[:2]
                    #Now figure out a way to see which ones are real retweets, not some coupon or something
                    #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
                    n_tweets +=1
                    n_favorites += status.favorite_count
                    if firstTwo == ['R','T']:
                        n_retweets += 0

                        retweet_num = 0
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count)
                        #print("Engagement for tweet: {}".format(engagement_num))

                        n_engagement +=  engagement_num


                    else:
                        n_retweets += status.retweet_count

                        retweet_num = status.retweet_count
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count + status.retweet_count)
                        n_engagement += engagement_num

                    engagement_text.append([status.text,' total engagement: ',engagement_num])
                else:
                    pass
                first_item = itemgetter(2)
                new_list = sorted(engagement_text, key = first_item)

                statuses_n = []
                reversed_list = new_list[::-1]
                i=0
                while i<n:
                    try:
                        statuses_n.append(reversed_list[i])
                    except:
                        break
                    i +=1

        intent = 'tophashcomments'
        return intent, statuses_n
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']

def get_hashtags(place, consumer_key, consumer_secret):
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx

    geolocator = Nominatim(scheme='http', user_agent="specify_your_app_name_here")

    location = geolocator.geocode(place, timeout=10)
    lat, long = location.latitude, location.longitude

    try:
        try:
            token, token_secret = session['token']
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(token, token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
        except:
            return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

        trend_loc = api.trends_closest(lat, long)

        woeid =  trend_loc[0]['woeid']
        trends1 = api.trends_place(woeid)
        trends = []
        hashtags = []
        for trend in trends1[0]['trends']:
            if trend['name'][0] == '#':
                trends.append(trend['name'])
        trends = ' ,  '.join(trends)
        intent = 'hashtagfind'

        return intent, trends
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']
#-----------------------------------------------------------------------------------
def TwitterEngagement(start_date, end_date, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    ts = time.time()
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0

    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    #------
#    try:
    page = 1
    while True:
        statuses = api.user_timeline(username, page=page, wait_on_rate_limit = True)
        if statuses:
            for status in statuses:
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                if (created_naive >= start_date) and (created_naive <= end_date):
                    status_list.append(status)
                    dates_list.append(created_naive)

                else:
                    pass
        else:
            break
        page += 1  # next page
    if len(dates_list) == 0:
        return ['Sorry, No activity was registered during that time period to analyze']
    else:
        new_start_date = dates_list[0]
        new_end_date = dates_list[-1]
        inter_date = new_start_date

        while inter_date <= end_date:
            engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
            inter_date += datetime.timedelta(days=1)
        engagement_text = []

        for status in status_list:
            txt = status.text
            ex = twitter_text.Extractor(txt)

            number += 1
            created_time = status.created_at
            created_datetime = created_time
            created_naive = created_datetime.replace(tzinfo=None)
            dates_list.append(created_naive)

            #difference = (naive-created_naive).days
            #if difference < 21:
            if (created_naive >= start_date) and (created_naive <= end_date):

                key = created_naive.strftime('%Y-%m-%d')
                #print(key)
                #key  = created_naive
                text = status.text
                #retweets


                #favorites
                favorites_num = status.favorite_count
                #print("Number of favorites is: {}".format(favorites_num))

                #engagement
                firstTwo = list(text)[:2]
                #Now figure out a way to see which ones are real retweets, not some coupon or something
                #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
                n_tweets +=1
                n_favorites += status.favorite_count
                if firstTwo == ['R','T']:
                    n_retweets += 0

                    retweet_num = 0
                    #print("Number of retweets is: {}".format(retweet_num))
                    engagement_num = (status.favorite_count)
                    #print("Engagement for tweet: {}".format(engagement_num))

                    n_engagement +=  engagement_num


                else:
                    n_retweets += status.retweet_count

                    retweet_num = status.retweet_count
                    #print("Number of retweets is: {}".format(retweet_num))
                    engagement_num = (status.favorite_count + status.retweet_count)
                    n_engagement += engagement_num


                if key in engagement_dict.keys():
                    engagement_dict[key] += engagement_num
                else:
                    engagement_dict[key] = engagement_num

                engagement_text.append([engagement_num, status.text])
            else:
                pass
            first_item = itemgetter(0)
            new_list = sorted(engagement_text, key = first_item)

            statuses_n = []
            reversed_list = new_list[::-1]
            i=0
            while i<10:
                try:
                    statuses_n.append(reversed_list[i])
                except:
                    break
                i +=1



        #print(engagement_list)

    sorted_x = sorted(engagement_dict.items(), key=operator.itemgetter(0))
    list_of_lists = [list(elem) for elem in sorted_x]
    title_list = [['dates','engagement']]
    final_dict = title_list + list_of_lists
    eng_string = 'The engagement for {} from {} to {} was: {}'.format(username, start_date, end_date, n_engagement)

    te = time.time()
    duration  = te-ts
    intent = 'TwitterEngagement'
    return intent, final_dict, eng_string


def TwitterOtherEngagement(start_date, end_date, handle, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    ts = time.time()
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]


    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0

    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(handle, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date

            while inter_date <= end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            for status in status_list:
                txt = status.text
                ex = twitter_text.Extractor(txt)

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list.append(created_naive)

                #difference = (naive-created_naive).days
                #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):

                    key = created_naive.strftime('%Y-%m-%d')
                    #print(key)
                    #key  = created_naive
                    text = status.text
                    #retweets


                    #favorites
                    favorites_num = status.favorite_count
                    #print("Number of favorites is: {}".format(favorites_num))

                    #engagement
                    firstTwo = list(text)[:2]
                    #Now figure out a way to see which ones are real retweets, not some coupon or something
                    #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
                    n_tweets +=1
                    n_favorites += status.favorite_count
                    if firstTwo == ['R','T']:
                        n_retweets += 0

                        retweet_num = 0
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count)
                        #print("Engagement for tweet: {}".format(engagement_num))

                        n_engagement +=  engagement_num


                    else:
                        n_retweets += status.retweet_count

                        retweet_num = status.retweet_count
                        #print("Number of retweets is: {}".format(retweet_num))
                        engagement_num = (status.favorite_count + status.retweet_count)
                        n_engagement += engagement_num


                    if key in engagement_dict.keys():
                        engagement_dict[key] += engagement_num
                    else:
                        engagement_dict[key] = engagement_num

                    engagement_text.append([engagement_num, status.text])
                else:
                    pass
                first_item = itemgetter(0)
                new_list = sorted(engagement_text, key = first_item)

                statuses_n = []
                reversed_list = new_list[::-1]
                i=0
                while i<10:
                    try:
                        statuses_n.append(reversed_list[i])
                    except:
                        break
                    i +=1



        #print(engagement_list)

        sorted_x = sorted(engagement_dict.items(), key=operator.itemgetter(0))
        list_of_lists = [list(elem) for elem in sorted_x]
        title_list = [['dates','engagement']]
        final_dict = title_list + list_of_lists
        eng_string = 'The engagement for {} from {} to {} was: {}'.format(handle, start_date, end_date, n_engagement)

        te = time.time()
        duration  = te-ts
        intent = 'TwitterEngagement'
        return intent, final_dict, eng_string
        #print('Total engagement is: {}'.format(n_engagement*n_followers))
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']
        #print('Total engagement is: {}'.format(n_engagement*n_followers))
#except:
#    return 'There was an error in answering your query. Could you please rephrase your question with all the required information?'
#@bp.route('/facebook_login')
#@login_required
#def fbauth():
#    facebook = OAuth2Session(client_id, redirect_uri=redirect_uri)
#    facebook = facebook_compliance_fix(facebook)
#    authorization_url, state = facebook.authorization_url(authorization_base_url)
#    return redirect(authorization_url)

#@bp.route('/facebook_login/authorized')
#@login_required
#def fbauth2():
#    facebook.fetch_token(token_url, client_secret=client_secret,authorization_response=redirect_uri)
#    r = facebook.get('https://graph.facebook.com/me?')
#    return redirect('/f_app')

def TopHashtagsOwn(start_date, end_date, n, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    ts = time.time()
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]


    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0

    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    hashtags = []
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(username, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date

            while inter_date <= new_end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            for status in status_list:
                txt = status.text
                ex = twitter_text.Extractor(txt)

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list.append(created_naive)

                #difference = (naive-created_naive).days
                #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):

                    if (len(status.entities['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                        #print(status.entities['hashtags'])
                        for tag in status.entities['hashtags']:
                            #print(tag['text'])
                            hashtags.append(tag['text'])
                        #hashtags.append(status.entities['hashtags'][0]['text'])



                else:
                    pass

            final_list = Counter(hashtags)
            withcounts = final_list.most_common(n)
            withcounts = ['Hashtag followed by the frequency of the hashtag'] + withcounts
            #top_n = [item[0] for item in withcounts]
        intent = 'tophashcomments'

        #return intent, withcounts, top_n
        return intent, withcounts
        #print('Total engagement is: {}'.format(n_engagement*n_followers))
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information? to collect myself']


def tweetsearchTimed(keyword, consumer_key, consumer_secret):

    positive = 0
    negative = 0
    neutral = 0
    senti_dict = {}
    cum_sent = 0
    my_tweet = []
    status_list = []
    runtime = 220

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    class MyStreamListener(tweepy.StreamListener):
        def __init__(self,api=None, time_limit=180):
            super(MyStreamListener, self).__init__()
            self.start_time = time.time()
            self.limit = time_limit

        def on_data(self, data):
            if (time.time() - self.start_time) < self.limit:
                tweet = json.loads(data)
                tweet_text = tweet['text']
                my_tweet.append(tweet_text)
                status_list.append(tweet)
                return True
            else:
                return False


    #try:
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
    myStream.filter(track=[keyword], async=True)
    #myStream.filter(track=[keyword])
    time.sleep(runtime) #halts the control for runtime seconds
    myStream.disconnect()
    analyzer = SentimentIntensityAnalyzer()
    positives = []
    neutrals = []
    negatives = []
    if len(my_tweet) != 0:
        for status in status_list:
            txt = status['text']
            ex = twitter_text.Extractor(txt)
            vs = analyzer.polarity_scores(txt)
            gensent = vs['compound']
            if gensent >= 0.05:
                positives.append(txt)
                positive +=1
            elif gensent <= -0.05:
                negatives.append(txt)
                negative +=1
            else:
                neutrals.append(txt)
                neutral +=1
            senti_dict[txt] = gensent
            cum_sent += gensent
            if (len(status['entities']['urls']) !=0  or len(ex.extract_urls()) != 0):
                urls += 1
            if (len(status['entities']['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                hashtags += 1
            if (len(status['entities']['user_mentions']) !=0  or len(ex.extract_mentioned_screen_names()) != 0):
                user_mentions += 1
            if len(status['entities']['symbols']) !=0:
                symbols += 1
            if ((len(status['entities']['urls']) ==0  or len(ex.extract_urls()) == 0) and (len(status['entities']['hashtags']) ==0  or len(ex.extract_hashtags()) == 0) and (len(status['entities']['user_mentions']) ==0  or len(ex.extract_mentioned_screen_names()) == 0) and len(status['entities']['symbols']) ==0):
                plain_text += 1
        av_sent = cum_sent/len(my_tweet)
        labels = ['positive', 'negative', 'neutral']
        data = [positive, negative, neutral]
        title = ['Some of the tweets matching the query are as follows: ']
        my_tweet = title+my_tweet
        intent = 'Twitter_searchAI'
        av_sent = 'Based on a random sampling of tweets collected in a 3 minute period, the average sentiment of tweets with the query: {}, is {}, on a scale with +1 to -1, with +1 being positive, 0 being neutral and -1 being negative'.format(keyword, round(av_sent,2))
        total_media = hashtags + urls + user_mentions + symbols + plain_text
        media = {'hashtags':hashtags,'urls': urls, 'user mentions':user_mentions, 'plain text':plain_text}
        if total_media != 0:
            media_percents = {'hashtags':(hashtags*100)/total_media,'urls': (urls*100)/total_media, 'user mentions':(user_mentions*100)/total_media,'symbols':(symbols*100)/total_media ,'plain text':(plain_text*100)/total_media}
        else:
            results = 'There was no activity registered during that time period. No conent was tweeted.'
        labels = ['positive', 'negative', 'neutral']
        labels1 = ['hashtags', 'urls', 'user mentions', 'plain text']
        label2 = [['entity type', 'count']]
        data2 = [[label, media[label]] for label in labels1]
        final_list = label2 + data2
        textcontent = [av_sent,' ', 'Some of the positive tweets corresponding to search term: ']
        for tweet in positives[:3]:
            textcontent.append(tweet)
        textcontent.append(' ')
        textcontent.append(' ')
        textcontent.append('Some of the neutral tweets corresponding to search term: ')
        for tweet in neutrals[:3]:
            textcontent.append(tweet)

        textcontent.append(' ')
        textcontent.append(' ')
        textcontent.append('Some of the negative tweets corresponding to search term: ')
        for tweet in negatives[:3]:
            textcontent.append(tweet)
        print(final_list)
        return intent, labels, data, av_sent, final_list, textcontent
    else:
        return ['We were unable to match your search term to any tweet tweeted during the past few minutes']
    #except:
    #    return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']
def tweetsearchTimedcompare(keyword, keyword2,consumer_key, consumer_secret):
    positive = 0
    negative = 0
    neutral = 0
    senti_dict = {}
    cum_sent = 0
    my_tweet = []
    my_tweet2 = []
    status_list = []
    runtime = 220

    positive2 = 0
    negative2 = 0
    neutral2 = 0
    senti_dict2 = {}
    cum_sent2 = 0
    status_list2 = []

    class MyStreamListener(tweepy.StreamListener):
        def __init__(self,api=None, time_limit=180):
            super(MyStreamListener, self).__init__()
            self.start_time = time.time()
            self.limit = time_limit

        def on_data(self, data):
            if (time.time() - self.start_time) < self.limit:
                tweet = json.loads(data)
                tweet_text = tweet['text']
                if keyword.lower() in tweet_text.lower():
                    my_tweet.append(tweet_text)
                    status_list.append(tweet)
                elif keyword2.lower() in tweet_text.lower():
                    my_tweet2.append(tweet_text)
                    status_list2.append(tweet)
                else:
                    pass

                return True
            else:
                return False


    #try:
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
    myStream.filter(track=[keyword, keyword2], async=True)
    #myStream.filter(track=[keyword])
    time.sleep(runtime) #halts the control for runtime seconds
    myStream.disconnect()
    analyzer = SentimentIntensityAnalyzer()
    positives = []
    neutrals = []
    negatives = []
    positives2 = []
    neutrals2 = []
    negatives2 = []
    if len(my_tweet) != 0 or len(my_tweet2) != 0:
        if len(my_tweet) != 0:
            for status in status_list:
                txt = status['text']
                ex = twitter_text.Extractor(txt)
                vs = analyzer.polarity_scores(txt)
                gensent = vs['compound']
                if gensent >= 0.05:
                    positives.append(txt)
                    positive +=1
                elif gensent <= -0.05:
                    negatives.append(txt)
                    negative +=1
                else:
                    neutrals.append(txt)
                    neutral +=1
                senti_dict[txt] = gensent
                cum_sent += gensent

        if len(my_tweet2) != 0:
            for status in status_list2:
                txt = status['text']
                ex = twitter_text.Extractor(txt)
                vs = analyzer.polarity_scores(txt)
                gensent = vs['compound']
                if gensent >= 0.05:
                    positives2.append(txt)
                    positive2 +=1
                elif gensent <= -0.05:
                    negatives2.append(txt)
                    negative2 +=1
                else:
                    neutrals2.append(txt)
                    neutral2 +=1
                senti_dict2[txt] = gensent
                cum_sent2 += gensent
            final_list = [['sentiment',keyword, keyword2],['positives',positive, positive2],['neutrals', neutral, neutral2],['negatives',negative, negative2]]
            av_sent = cum_sent/len(my_tweet)
            av_sent2 = cum_sent2/len(my_tweet2)

            intent = 'Twitter_searchAI_compare'
            av_sent = 'Based on a random sampling of tweets collected in a 3 minute period, the average sentiment of tweets with the term: {}, is {}, and the average sentiment for tweets with the term:  {}, is {}, on a scale with +1 to -1, with +1 being positive, 0 being neutral and -1 being negative'.format(keyword, round(av_sent,2), keyword2, round(av_sent2,2))

            textcontent = [av_sent,' ', 'Some of the positive tweets corresponding to search term, {}: '.format(keyword)]
            for tweet in positives[:3]:
                textcontent.append(tweet)
            textcontent.append(' ')
            textcontent.append(' ')
            textcontent.append('Some of the neutral tweets corresponding to search term, {}: '.format(keyword))
            for tweet in neutrals[:3]:
                textcontent.append(tweet)
            textcontent.append(' ')
            textcontent.append(' ')
            textcontent.append('Some of the negative tweets corresponding to search term, {}: '.format(keyword))
            for tweet in negatives[:3]:
                textcontent.append(tweet)
            textcontent.append(' ')
            textcontent.append(' ')
            textcontent.append('Some of the positive tweets corresponding to search term, {}: '.format(keyword2))
            for tweet in positives2[:3]:
                textcontent.append(tweet)
            textcontent.append(' ')
            textcontent.append(' ')
            textcontent.append('Some of the neutral tweets corresponding to search term, {}: '.format(keyword2))
            for tweet in neutrals2[:3]:
                textcontent.append(tweet)

            textcontent.append(' ')
            textcontent.append(' ')
            textcontent.append('Some of the negative tweets corresponding to search term, {}: '.format(keyword2))
            for tweet in negatives2[:3]:
                textcontent.append(tweet)

            print(final_list)
            return intent, av_sent, final_list, textcontent
    else:
        return ['We were unable to match your search term to any tweet tweeted during the past few minutes']
    #except:
    #    return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']


def TopHashtagsOther(start_date, end_date, handle, n, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    ts = time.time()
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0

    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    hashtags = []
    #------
    try:
            #-------
        page = 1
        while True:
            statuses = api.user_timeline(handle, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date

            while inter_date <= new_end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            for status in status_list:
                txt = status.text
                ex = twitter_text.Extractor(txt)

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list.append(created_naive)

                    #difference = (naive-created_naive).days
                    #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):

                    if (len(status.entities['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                        #print(status.entities['hashtags'])
                        #print(status.entities['hashtags'][0])
                        for tag in status.entities['hashtags']:
                            #print(tag['text'])
                            hashtags.append(tag['text'])
                        #hashtags.append(status.entities['hashtags'][0]['text'])



                else:
                    pass

            final_list = Counter(hashtags)
            withcounts = final_list.most_common(n)
            withcounts = ['Hashtag followed by the frequency of the hashtag'] + withcounts
            #top_n = [item[0] for item in withcounts]

        intent = 'tophashcomments'

        #return intent, withcounts, top_n
        return intent, withcounts
            #print('Total engagement is: {}'.format(n_engagement*n_followers))
        #-------
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']

#Get the percentage of different kinds of media for a third party account
def TwitOtherPercentEntity(start_date, end_date, handle, entity_type, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

    intent = "mediaTwitter"

    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0



    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(handle, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return intent, [], ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date

            while inter_date <= end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            for status in status_list:
                txt = status.text
                ex = twitter_text.Extractor(txt)

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list.append(created_naive)

                #difference = (naive-created_naive).days
                #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):
                    #-------
                    if (len(status.entities['urls']) !=0  or len(ex.extract_urls()) != 0):
                        urls += 1
                    if (len(status.entities['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                        hashtags += 1
                    if (len(status.entities['user_mentions']) !=0  or len(ex.extract_mentioned_screen_names()) != 0):
                        user_mentions += 1
                    if len(status.entities['symbols']) !=0:
                        symbols += 1
                    if ((len(status.entities['urls']) ==0  or len(ex.extract_urls()) == 0) and (len(status.entities['hashtags']) ==0  or len(ex.extract_hashtags()) == 0) and (len(status.entities['user_mentions']) ==0  or len(ex.extract_mentioned_screen_names()) == 0) and len(status.entities['symbols']) ==0):
                        plain_text += 1

        total_media = hashtags + urls + user_mentions + symbols + plain_text
        media = {'hashtags':hashtags,'urls': urls, 'user mentions':user_mentions, 'plain text':plain_text}
        if total_media != 0:
            media_percents = {'hashtags':(hashtags*100)/total_media,'urls': (urls*100)/total_media, 'user mentions':(user_mentions*100)/total_media,'symbols':(symbols*100)/total_media ,'plain text':(plain_text*100)/total_media}
            percents = 'The total number of {} is {}, with a percentage of {}% of all entities present in tweets over the period you requested.'.format(entity_type, media[entity_type],round(media_percents[entity_type],2))
            #percents = """The percentage of tweets with hashtags was: {}%, percentage of tweets with urls was: {}%,  percentage of tweets with user mentions was: {}%, percentage of tweets with symbols was: {}%, percentage of tweets with only text was: {}%'.
            #The number of tweets with hashtags was: {}, number of tweets with urls was: {},  number of tweets with user mentions was: {}, number of tweets with symbols was: {},number of tweets with only text was: {}""".format(media_percents['hashtags'], media_percents['urls'], media_percents['user_mentions'], media_percents['symbols'],media_percents['plain text'],hashtags, urls, user_mentions, symbols, plain_text)

        else:
            results = 'There was no activity registered during that time period. No conent was tweeted.'
        labels = ['hashtags', 'urls', 'user mentions', 'plain text']
        data = [media[label] for label in labels]

        intent = "mediaTwitter"
        #return intent, data, labels
        print(data)
        print(labels)
        return intent, labels, data, percents
        #print('Total engagement is: {}'.format(n_engagement*n_followers))
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']

#This is a comprehensive view of one's own Twitter Profile
def TwitOwnPercentEntity(start_date, end_date, entity_type, consumer_key, consumer_secret):
    #increment the end_date by 1
    end_date = end_date + datetime.timedelta(days=1)
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]

    intent = "mediaTwitter"

    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0



    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(username, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return intent,[],['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date

            while inter_date <= end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            for status in status_list:
                txt = status.text
                ex = twitter_text.Extractor(txt)

                number += 1
                created_time = status.created_at
                created_datetime = created_time
                created_naive = created_datetime.replace(tzinfo=None)
                dates_list.append(created_naive)

                #difference = (naive-created_naive).days
                #if difference < 21:
                if (created_naive >= start_date) and (created_naive <= end_date):
                    #-------
                    if (len(status.entities['urls']) !=0  or len(ex.extract_urls()) != 0):
                        urls += 1
                    if (len(status.entities['hashtags']) !=0  or len(ex.extract_hashtags()) != 0):
                        hashtags += 1
                    if (len(status.entities['user_mentions']) !=0  or len(ex.extract_mentioned_screen_names()) != 0):
                        user_mentions += 1
                    if len(status.entities['symbols']) !=0:
                        symbols += 1
                    if ((len(status.entities['urls']) ==0  or len(ex.extract_urls()) == 0) and (len(status.entities['hashtags']) ==0  or len(ex.extract_hashtags()) == 0) and (len(status.entities['user_mentions']) ==0  or len(ex.extract_mentioned_screen_names()) == 0) and len(status.entities['symbols']) ==0):
                        plain_text += 1

        #print(engagement_list)
        total_media = hashtags + urls + user_mentions + symbols + plain_text
        media = {'hashtags':hashtags,'urls': urls, 'user mentions':user_mentions, 'plain text':plain_text}
        if total_media != 0:
            media_percents = {'hashtags':(hashtags*100)/total_media,'urls': (urls*100)/total_media, 'user mentions':(user_mentions*100)/total_media,'symbols':(symbols*100)/total_media ,'plain text':(plain_text*100)/total_media}
            percents = 'The total number of {} is {}, with a percentage of {}% of all entities present in tweets over the period you requested.'.format(entity_type, media[entity_type],media_percents[entity_type])
            #percents = """The percentage of tweets with hashtags was: {}%, percentage of tweets with urls was: {}%,  percentage of tweets with user mentions was: {}%, percentage of tweets with symbols was: {}%, percentage of tweets with only text was: {}%'.
            #The number of tweets with hashtags was: {}, number of tweets with urls was: {},  number of tweets with user mentions was: {}, number of tweets with symbols was: {},number of tweets with only text was: {}""".format(media_percents['hashtags'], media_percents['urls'], media_percents['user_mentions'], media_percents['symbols'],media_percents['plain text'],hashtags, urls, user_mentions, symbols, plain_text)
        else:
            results = 'There was no activity registered during that time period. No conent was tweeted.'
        labels = ['hashtags', 'urls', 'user mentions', 'plain text']
        data = [media[label] for label in labels]

        intent = "mediaTwitter"
        #return intent, data, labels
        print(data)
        print(labels)
        return intent, labels, data, percents
        #print('Total engagement is: {}'.format(n_engagement*n_followers))
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']

#Sentiment analysis on tweets in third party pages
def TweetSentimentOther(start_date, end_date, handle, consumer_key, consumer_secret):
    #increment the end_date by 1
    tknzr = TweetTokenizer()
    end_date = end_date + datetime.timedelta(days=1)
    ts = time.time()
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]


    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0
    total_diversity = 0
    total_words = 0
    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    hashtags = []
    senti_dict = {}
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(handle, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date
            positive = 0
            negative = 0
            neutral = 0
            while inter_date <= new_end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            analyzer = SentimentIntensityAnalyzer()
            cum_sent = 0
            for status in status_list:
                txt = status.text
                vs = analyzer.polarity_scores(txt)
                gensent = vs['compound']
                if gensent >= 0.05:
                    positive +=1
                elif gensent <= -0.05:
                    negative +=1
                else:
                    neutral +=1
                senti_dict[txt] = gensent
                cum_sent += gensent
                words = tknzr.tokenize(txt)
                total_diversity += lexical_diversity(words)
                total_words += len(words)

        n = len(status_list)
        diversity = total_diversity/n
        word_average = total_words/n
        statement = 'The lexical diversity of the tweets during that time period was {} (maximum possible Lexical diversity is 1) and average number of words per status was {}. Higher lexical diversity indicates the use of a rich vocabulary in expressing ideas or news, and is usually a good sign.'.format(diversity, word_average)
        av_sent = cum_sent/len(status_list)
        number_tweets = 'A total of {} tweets were tweeted out from this handle during this period'.format(n)
        overview = 'The average sentiment over the period is {}, on a scale with +1 being positive, 0 being neutral and -1 being negative'.format(round(av_sent,2))
        result = [number_tweets, overview, statement]
        labels = ['positive', 'negative', 'neutral']
        data = [positive, negative, neutral]
        intent = 'Twitter_sentiment'
        return intent, labels, data, result
    #print('Total engagement is: {}'.format(n_engagement*n_followers))
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information? to collect myself']

def TweetSentimentOwn(start_date, end_date, consumer_key, consumer_secret):
    #increment the end_date by 1
    tknzr = TweetTokenizer()
    end_date = end_date + datetime.timedelta(days=1)
    ts = time.time()
    #initial time
    try:
        token, token_secret = session['token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        username  = api.me().screen_name
    except:
        return ["Please authorize Fora to mine Twitter by clicking the 'Authorize Twitter' button in the navigation bar at the very top"]



    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    engarray = []
    n_engagement = 0

    urls = 0
    hashtags = 0
    user_mentions = 0
    symbols = 0
    plain_text = 0

    urls_eng = 0
    hashtags_eng = 0
    user_mentions_eng = 0
    symbols_eng = 0
    plain_text_eng = 0
    total_diversity = 0
    total_words = 0

    number =0
    engagement_dict = {}
    dates_list = []
    status_list = []
    hashtags = []
    senti_dict = {}
    #------
    try:
        page = 1
        while True:
            statuses = api.user_timeline(username, page=page, wait_on_rate_limit = True)
            if statuses:
                for status in statuses:
                    created_time = status.created_at
                    created_datetime = created_time
                    created_naive = created_datetime.replace(tzinfo=None)
                    if (created_naive >= start_date) and (created_naive <= end_date):
                        status_list.append(status)
                        dates_list.append(created_naive)

                    else:
                        pass
            else:
                break
            page += 1  # next page
        if len(dates_list) == 0:
            return ['Sorry, No activity was registered during that time period to analyze']
        else:
            new_start_date = dates_list[0]
            new_end_date = dates_list[-1]
            inter_date = new_start_date
            positive = 0
            negative = 0
            neutral = 0

            while inter_date <= new_end_date:
                engagement_dict[inter_date.strftime('%Y-%m-%d')] = 0
                inter_date += datetime.timedelta(days=1)
            engagement_text = []

            analyzer = SentimentIntensityAnalyzer()
            cum_sent = 0
            for status in status_list:
                txt = status.text
                vs = analyzer.polarity_scores(txt)
                gensent = vs['compound']
                if gensent >= 0.05:
                    positive +=1
                elif gensent <= -0.05:
                    negative +=1
                else:
                    neutral +=1
                senti_dict[txt] = gensent
                cum_sent += gensent
                words = tknzr.tokenize(txt)
                total_diversity += lexical_diversity(words)
                total_words += len(words)

        n = len(status_list)
        diversity = total_diversity/n
        word_average = total_words/n
        statement = 'The lexical diversity of the tweets during that time period was {} (maximum possible Lexical diversity is 1) and average number of words per status was {}. Higher lexical diversity indicates the use of a rich vocabulary in expressing ideas or news, and is usually a good sign.'.format(diversity, word_average)
        av_sent = cum_sent/len(status_list)
        number_tweets = 'A total of {} tweets were tweeted out from this handle during this period'.format(n)
        overview = 'The average sentiment over the period is {}, on a scale with +1 being positive, 0 being neutral and -1 being negative'.format(round(av_sent,2))
        result = [number_tweets, overview, statement]
        labels = ['positive', 'negative', 'neutral']
        data = [positive, negative, neutral]
        intent = 'Twitter_sentiment'
        return intent, labels, data, result
    #print('Total engagement is: {}'.format(n_engagement*n_followers))
    except:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information? to collect myself']

#------------------------
consumer_key = '79DkJ5kXIDuOir05XoTE0GYWJ'
consumer_secret = 'VohjomRHuXONbJpNwIaRGY0sEwMRTVImRXWiVYAa3gC2PiJLnL'
callback = 'https://127.0.0.1:5000/twitter_login/twitter/authorized'
#callback = 'https://forametrics.herokuapp.com/twitter_login/twitter/authorized'


@bp.route('/twitter_login')
@login_required
def auth():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    url = auth.get_authorization_url()
    session['request_token'] = auth.request_token
    return redirect(url)


@bp.route('/twitter_login/twitter/authorized')
@login_required
def twitter_callback():
    request_token = session['request_token']

    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
        auth.request_token = request_token
        verifier = request.args.get('oauth_verifier')
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        #flash("Please click 'Authorize app' if you want to authorize Twitter inorder to proceed to use Fora.")
        return redirect('/twitter_login')

    session['token'] = (auth.access_token, auth.access_token_secret)
    flash('You have authorized Fora to analyze Twitter data streams for you ')
    return redirect('/index')

#This is to store tokens later for the scheduling part. Strengthen password requirements before
#Including this feature
@bp.route('/app')
@login_required
def request_twitter():
    token, token_secret = session['token']
    print(token)
    print(token_secret)

    #auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    #auth.set_access_token(token, token_secret)
    #api = tweepy.API(auth)
    #-------Putting it all in the database
    #insert_dic = Twittertokens(user_id =current_user.id, token = token, token_secret=token_secret)
    #db.session.add(insert_dic)
    #db.session.commit()
    #-------------------------------------
    #api.update_status("Hey guys I'm doing it. ")
    return "You are @{screen_name} on Twitter".format(screen_name = api.me().screen_name)

#-------------------------------------------------------------

def twittersentiment(consumer_key, consumer_secret):
        # Consumer:
    days = 21
    token, token_secret = session['token']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    username  = api.me().screen_name

    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    n_engagement = 0
    for status in tweepy.Cursor(api.user_timeline).items():
        created_time = status.created_at
        created_datetime = created_time
        created_naive = created_datetime.replace(tzinfo=None)
        difference = (naive-created_naive).days
        if difference < 21:
            text = status.text
            print(text)
            #retweets


            #favorites
            favorites_num = status.favorite_count
            print("Number of favorites is: {}".format(favorites_num))

            #engagement

            firstTwo = list(text)[:2]
            #Now figure out a way to see which ones are real retweets, not some coupon or something
            #First make the rest of this
            #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
            n_tweets +=1
            n_favorites += status.favorite_count
            if firstTwo == ['R','T']:
                n_retweets += 0

                retweet_num = 0
                print("Number of retweets is: {}".format(retweet_num))
                engagement_num = (status.favorite_count)/n_followers
                print("Engagement for tweet: {}".format(engagement_num))

                n_engagement += status.favorite_count
            else:
                n_retweets += status.retweet_count
                n_engagement += status.favorite_count + n_retweets

                retweet_num = status.retweet_count
                print("Number of retweets is: {}".format(retweet_num))
                engagement_num = (status.favorite_count + n_retweets)/n_followers
                print("Engagement for tweet: {}".format(engagement_num))

            print('-----------------------------------------------------------------')

        else:
            pass



#@periodic_task(run_every=(crontab(minute='*/5')),name= "Twenter", ignore_result=True)
def twenter():
    #Do this as a loop. Get tokens from database and enter this.
        # Consumer:

    # Access:
    #ACCESS_TOKEN  = '397951660-oprjKCCP1xBMi4OMShY4OvFWctmPvC1MPuo9YKfC'
    #ACCESS_SECRET = 'SIcm6oeSI6q8cNAePFcauQ121Ye1IfuzvujYV0yvNqz4V'
    days = 21

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    username  = api.me().screen_name

    datetime_now = datetime.datetime.utcnow()
    naive = datetime_now.replace(tzinfo=None)
    n_tweets = 0
    n_retweets = 0
    n_followers = api.me().followers_count
    n_favorites = 0
    n_engagement = 0
    for status in tweepy.Cursor(api.user_timeline).items():
        created_time = status.created_at
        created_datetime = created_time
        created_naive = created_datetime.replace(tzinfo=None)
        difference = (naive-created_naive).days
        if difference < 21:
            text = status.text
            firstTwo = list(text)[:2]
            #Now figure out a way to see which ones are real retweets, not some coupon or something
            #First make the rest of this
            #if first two characters are RT, then dont count retweets but count towards favorites, comments and tweets
            n_tweets +=1
            n_favorites += status.favorite_count
            if firstTwo == ['R','T']:
                n_retweets += 0
                n_engagement += status.favorite_count
            else:
                n_retweets += status.retweet_count
                n_engagement += status.favorite_count + n_retweets

        else:
            pass

    add_row = TwitterAnalytics(u_username = 'Fora', n_followers = n_followers, n_favorites = n_favorites, n_retweets = n_retweets, n_tweets = n_tweets, n_engagement = n_engagement)
    db.session.add(add_row)
    db.session.commit()


#-------------------------------------------------------------------------------------------------------
#Function to convert utc datetime object to local datetime object
def utc_to_local(datetimeobject):
    #the utc_zone
    utc_zone = tz.tzutc()
    local_zone = tz.tzlocal()
    utc = datetimeobject.replace(tzinfo=utc_zone)
    central = utc.astimezone(local_zone)
    return central

#@celery.task
def Twitter_optimal_hours_2(uname):
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

#@periodic_task(run_every=datetime.timedelta(days=1))
#@periodic_task(run_every=(crontab(minute='*/60')),name= "enterfeeds", ignore_result=True)
def enterfeeds():
    feeds = Feeds.query.all()
    item_list = FeedItem.query.all()
    title_list = [item.title for item in item_list]
    for row in feeds:
        feed = feedparser.parse(row.feedlink)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            if title not in title_list:
                title_list.append(title)
                feedItem = FeedItem(link = link, title = title, industry = row.industry)
                db.session.add(feedItem)
                db.session.commit()
            else:
                pass

def datetime_convert(d_str):
  f = '%Y-%m-%d %H:%M:%S'
  dtimeobj = datetime.datetime.strptime(d_str, f)
  return dtimeobj

def schedtime_calc_dt(dtobj):
    nowtime = datetime.datetime.now()
    delta = dtobj-nowtime
    schedtime = datetime.datetime.utcnow() + delta
    return schedtime

def schedtime_calc(d_str):
    #f = "%d/%m/%Y "
    f = '%Y-%m-%d %H:%M:%S'
    dtimeobj = datetime.datetime.strptime(d_str, f)
    nowtime = datetime.datetime.now()
    delta = dtimeobj-nowtime
    schedtime = datetime.datetime.utcnow() + delta
    return schedtime

#The first one is the valid one, the current is just a check



#@celery.task
def feedlinkparse(feedlink, ind):
    feed = feedparser.parse(feedlink)
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        feedItem = FeedItem(link = link, title = title, industry = ind)
        db.session.add(feedItem)
        db.session.commit()


#Celery task to see the best times to tweet, throw an if else here for less than
#100 follower use case


#@bp.before_app_first_request
def FeedItem_wload():
    enterfeeds.apply_async()
    #fbenter.apply_async()
    twenter.apply_async()

    #Move this thing somewhere before it fucks up




#Implement shared task to allow for retries in a bit
#The celery part has to be configured with application factory
#@celery.task
def schedule_tweet_task(message,consumer_key, consumer_secret, callback,token, token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)
    try:
        api.update_status(message)
        #print(post.body)

        #So the problem is that it tweets again and again, so just a minor tweak and we'll all be good
    except tweepy.TweepError as e:
        #print("Didn't work"+post_time)
        print('Twitter error: ', e.response.text)


#This celery task posts content to social media at time of highest activity
#So minute has to be added for posting purposes
def time_return(dt, day_hour_dict):
    while True:
        hour_list = [int(hour) for hour in day_hour_dict[calendar.day_name[dt.weekday()]]]
        for hour_i in hour_list:
            if int(hour_i) > dt.hour:
                hour = hour_i
                return dt, hour
        dt = datetime.datetime.now() + datetime.timedelta(days=1)

def day_post_hour_calc(dt,socialnetwork, identity):
    posts = Post.query.filter_by(user_id=identity, socialnetwork = socialnetwork).all()
    day_posts = []
    day_post_hours = []
    for post in posts:
        if post.year == dt.year and post.month ==dt.month and post.day == dt.day:
            day_posts.append(post)
            if post.ampm == 'PM' and post.hour==12:
                hour = 12
            elif post.ampm == 'PM' and post.hour <12:
                hour = post.hour +12
            elif post.ampm == 'AM' and post.hour ==12:
                hour = 0
            else:
                    hour = post.hour

            #day_post_hours.append(post.hour)
            day_post_hours.append(hour)
    return day_post_hours

def time_return_unique(dt, day_hour_dict, socialnetwork, identity):
    #Returns times where social media posts have not been made
    while True:
        #new function to define day_post_hours
        day_post_hours = day_post_hour_calc(dt, socialnetwork, identity)
        hour_list = list(np.setdiff1d([int(hour) for hour in day_hour_dict[calendar.day_name[dt.weekday()]]],day_post_hours))
        for hour_i in hour_list:
            if int(hour_i) > dt.hour:
                hour = hour_i
                return dt, hour
        dt = datetime.datetime.now() + datetime.timedelta(days=1)




#@celery.task
def smart_post_task(message, socialnetwork, identity, userName):

    posts = Post.query.filter_by(user_id=identity).all()

    if socialnetwork == 'Facebook':
        #This is where day hourdict query is worked out
        day_hour_dicts = Bestdicts.query.filter_by(user_username = userName, socialnetwork = 'Facebook').all()
        l = len(day_hour_dicts)
        day_hour = day_hour_dicts[l-1]
        day_hour_dict = ast.literal_eval(day_hour.hourdic)
    elif socialnetwork == 'Twitter':
        day_hour_dicts = Bestdicts.query.filter_by(user_username = userName, socialnetwork = 'Twitter').all()
        l = len(day_hour_dicts)
        day_hour = day_hour_dicts[l-1]
        day_hour_dict = ast.literal_eval(day_hour.hourdic)
    else:
        pass

    daily_post_frequency = {
    'Facebook': 2,
    'Twitter': 15,
    'LinkedIn': 1}

    n = daily_post_frequency[socialnetwork]
    dt = datetime.datetime.now()
    weekday = calendar.day_name[datetime.datetime.now().weekday()]

    while True:
        day_posts = []
        day_post_hours = []
        for post in posts:
            if post.year == dt.year and post.month ==dt.month and post.day == dt.day:
                day_posts.append(post)
                if post.ampm == 'PM' and post.hour==12:
                    hour = 12
                elif post.ampm == 'PM' and post.hour <12:
                    hour = post.hour +12
                elif post.ampm == 'AM' and post.hour ==12:
                    hour = 0
                else:
                    hour = post.hour

                #day_post_hours.append(post.hour)
                day_post_hours.append(hour)
        #Fix the hours here so they are on 24 hour clock
        if len(day_posts) == 0:
            minute = randint(10, 55)
            #Loop through the hour list, for each check if hour is greater than now time, else next. If goes to end, add datetime
            #then keep looping. Do this for the next as well.

            #--------Fall back code--------------------
            #hour = day_hour_dict[weekday][0]

            #------------------New code----------------
            #do a while True
            dt, hour = time_return(dt, day_hour_dict)

            #-------------------------------------------------------------------



            if int(hour) > 12:
                post_hour = int(hour)-12
                ampm = 'PM'
            elif int(hour) == 12:
                post_hour = int(hour)
                ampm = 'PM'
            elif int(hour) == 0:
                post_hour = int(hour)
                ampm = 'AM'
            else:
                post_hour = int(hour)
                ampm = 'AM'

            d_str = str(dt.day)+'/'+str(dt.month)+'/'+str(dt.year)+' '+str(hour)+':'+str(minute)+':'+'00'
            schedtime = schedtime_calc(d_str)
            if socialnetwork == 'Facebook':
                post = Post(body=message, user_id=identity, socialnetwork = socialnetwork, ampm = ampm,\
                 hour=int(hour), minute = int(minute), day = int(dt.day), month = int(dt.month), year = int(dt.year))
                db.session.add(post)
                db.session.commit()
                schedule_fbpost_task.apply_async(args=[message], eta=schedtime)

                break
            else:
                post = Post(body=message, user_id=identity, socialnetwork = socialnetwork, ampm = ampm,\
                 hour=int(hour), minute = int(minute), day = int(dt.day), month = int(dt.month), year = int(dt.year))
                db.session.add(post)
                db.session.commit()
                token, token_secret = session['token']
                schedule_tweet_task.apply_async(args=[message, consumer_key, consumer_secret, callback,token, token_secret], eta=schedtime)
                break

        elif len(day_posts) < n:
            dt, hour  = time_return_unique(dt, day_hour_dict, socialnetwork, identity)
            minute = randint(10, 55)
            if int(hour) > 12:
                post_hour = int(hour)-12
                ampm = 'PM'
            elif int(hour) == 12:
                post_hour = int(hour)
                ampm = 'PM'
            elif int(hour) == 0:
                post_hour = int(hour)
                ampm = 'AM'
            else:
                post_hour = int(hour)
                ampm = 'AM'
            d_str = str(dt.day)+'/'+str(dt.month)+'/'+str(dt.year)+' '+str(hour)+':'+str(minute)+':'+'00'
            schedtime = schedtime_calc(d_str)
            if socialnetwork == 'Facebook':
                post = Post(body=message, user_id=identity, socialnetwork = socialnetwork, ampm = ampm,\
                 hour=int(hour), minute = int(minute), day = int(dt.day), month = int(dt.month), year = int(dt.year))
                db.session.add(post)
                db.session.commit()
                schedule_fbpost_task.apply_async(args=[message], eta=schedtime)
                break
            else:
                post = Post(body=message, user_id=identity, socialnetwork = socialnetwork, ampm = ampm,\
                 hour=int(hour), minute = int(minute), day = int(dt.day), month = int(dt.month), year = int(dt.year))
                db.session.add(post)
                db.session.commit()
                #schedule_tweet_task.apply_async(args=[message], eta=schedtime)
                break

        else:
            dt = datetime.datetime.now() + datetime.timedelta(days=1)



def get_tweets(username):
    tweets = tweepy_api.user_timeline(screen_name=username)
    return
#posts = current_user.followed_posts()
#https://networklore.com/start-task-with-flask/
#Partially implemented: yields the error : AttributeError: 'NoneType' object has no attribute 'followed_posts'

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        db.session.commit()

#    g.locale = str(get_locale())





#-------------------------------------------------------------------
#@bp.route('/explore')
#@login_required
#def explore():
#    page = request.args.get('page', 1, type=int)
#    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
#        page, current_app.config['POSTS_PER_PAGE'], False)
#    next_url = url_for('main.explore', page=posts.next_num) \
#        if posts.has_next else None
#    prev_url = url_for('main.explore', page=posts.prev_num) \
#        if posts.has_prev else None
#    return render_template('index.html', title=_('Explore'),
#                           posts=posts.items, next_url=next_url,
#                           prev_url=prev_url)
#--------------------------------------------------------------------
#If this doesn't work, use @bp.route('/user/<username>')
@bp.route('/<username>')
@login_required
def user(username):
    #This is the option for the RadioField
    #form = socialnetworkForm()
    user = User.query.filter_by(username = username).first_or_404()
    socialnetwork = request.args.get("socialnetwork")
    #page = request.args.get('page', 1, type=int)
    if socialnetwork == 'Facebook':
        #posts = Post.query.filter_by(socialnetwork = 'Facebook')
        posts = current_user.followed_posts().filter_by(socialnetwork = 'Facebook')
    elif socialnetwork == 'Twitter':
            posts = current_user.followed_posts().filter_by(socialnetwork = 'Twitter')
        #posts = current_user.followed_posts().query.filter_by(socialnetwork = Twitter).all()
    else:
        posts = current_user.followed_posts()
    return render_template('user.html', user = user, posts = posts, form = socialnetwork)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        #current_user.username = form.username.data
        current_user.businessName = form.businessName.data
        current_user.coreService = form.coreService.data
        current_user.services = form.services.data
        #Take out username and add zip and email
        current_user.email = form.email.data
        current_user.zip_code = form.zip_code.data
        db.session.commit()
        flash('Your changes have been saved. ')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        #form.username.data = current_user.username
        form.businessName.data = current_user.businessName
        form.coreService.data = current_user.coreService
        form.services.data = current_user.services
        form.email.data = current_user.email
        form.zip_code.data = current_user.zip_code
    return render_template('edit_profile.html', title='Update Information',
                           form=form)
#@bp.route('/feed_manage', methods=['GET', 'POST'])
#@login_required
def feed_manage():
    form = FeedEnterForm()
    if form.validate_on_submit():
        feeds = Feeds.query.all()
        feed_list = [item.feedlink for item in feeds]
        if form.feedlink.data not in feed_list:
            feeds = Feeds(feedlink=form.feedlink.data, industry=form.industry.data)
            db.session.add(feeds)
            db.session.commit()
            #Add the feeditems as well, don't check for again because redundant
            feedlinkparse.apply_async(args=[form.feedlink.data, form.industry.data ])
            flash('Your feed has been added.')
            return redirect(url_for('main.feed_manage'))
        else:
            flash('Feed already present')
            return redirect(url_for('main.feed_manage'))
    else:
        pass
    return render_template('feed_manage.html', title='Add feed',
                           form=form)


#-----Chatbot code-------------------------------------

def translate(text):
    try:
        gc.collect()
        #intentEntityDict = {'engagement':['period','socialnetwork'],
        #        'sentiment':['period','socialnetwork'],
        #        'hashtagfind':['location'],
        #        'plot':['statistical entity','socialnetwork', 'period']}
        intentEntityDict = {'greet': [],
                            'reach':[],
                            'impressions':[],
                            'error_handle': [],
                            'hashtagfind':['location'],
                            'engagement_Twitter_plain': ['end date', 'start date'],
                            'top_hashtags':['end date', 'start date','count'],
                            'top_tweets':['end date', 'start date','count'],
                            'twitter_percent_type':['end date', 'start date','type'],
                            'eng_comparison':['end date', 'start date'],
                            'Twitter_sentiment':['end date', 'start date'],
                            'Twit_follower_count':[],
                            'total_picture_twitter':['social network','start date', 'end date'],
                            #remove keyword or more correctly search term from here and get it in compute using re
                            'Twitter_searchAI' :['search term'],
                            'Activity_timeline':['social network','start date', 'end date']}

        interpreter = Interpreter.load('./models/nlu/default/foranlu')
        nluObj = (interpreter.parse(text))
        intent = nluObj['intent']['name']
        entityDict = {}
        available_entities_dic = {}
        missing_ents = []

        process = psutil.Process(os.getpid())
        print(process.memory_info().rss)
        #See if handle is in the text, if it is and it isn't in the parsed entities, add it to the known entities
        arrayedText = list(text)
        if arrayedText[-1] == '?':
            arrayedText.pop()
        else:
            pass
        text = ''.join(arrayedText)
        handle_list = re.findall(r'(?<!\w)(?<!@)(@\w{1,15})(?=\s|$)\b' ,text)
        handle = 0
        if intent == 'eng_comparison':
            if len(handle_list) >= 2:
                available_entities_dic['handle1'] = handle_list[0]
                available_entities_dic['handle2'] = handle_list[1]
            elif len(handle_list) == 1:
                available_entities_dic['handle1'] = handle_list[0]
                #pull handle from database and assign here
                available_entities_dic['handle2'] = 'BubbleUnder1'
            else:
                missing_ents.append('handle1')
                missing_ents.append('handle2')
        else:
            if len(handle_list) != 0:
                available_entities_dic['handle'] = handle_list[0]
    #How to get all the entities present in the returned nluObj
        for entity in nluObj['entities']:
            entityDict[entity['entity']] = entity['value']
        required_entities = intentEntityDict[intent]
        #available_entities =list(entityDict.keys())


#check this if right
        if intent == 'Twitter_searchAI':
            queryitem = re.findall(r"#(\w+)", text)
            queryitem2 = re.findall(r"\$([^ ]+)", text)
            takenwords= ['#'+item for item in queryitem]+['$'+item for item in queryitem2]
            words = text.split()
            resultwords  = [word for word in words if word not in takenwords]
            result = ' '.join(resultwords)
            queryitem3 = takenwords+re.findall(r"(?<!\.\s)(?!^)\b([A-Z]\w*(?:\s+[A-Z]\w*)*)", result)
            if len(queryitem3) != 0:
                search_term = queryitem3
                #search_term ='#'+queryitem[0]
                available_entities_dic['search term'] = search_term
            else:
                available_entities_dic = {}


        for entity in nluObj['entities']:
            available_entities_dic[entity['entity']] = entity['value']

        #if handle != 0:
        #    if 'handle' not in available_entities_dic.keys():
        #        available_entities_dic['handle'] = handle
        #else:
        #    pass

        available_entities =list(available_entities_dic.keys())
        #missing_ents = []
        for entity in required_entities:
            if entity not in available_entities:
                missing_ents.append(entity)
                #New Stuff-------
        print('intent :', intent)
        print('available_entities_dic before: ',available_entities_dic)
        print('missing_ents before: ',missing_ents)

        if  intent == 'engagement_Twitter_plain' or intent == 'top_hashtags' or intent == 'top_tweets' or intent == 'twitter_percent_type' or intent == 'Twitter_sentiment' or intent == 'eng_comparison' :
            if 'date' in list(available_entities_dic.keys()):
                available_entities_dic['start date'] = available_entities_dic['date']
                #remove date key
                available_entities_dic['end date'] = datetime.datetime.now().strftime("%b %d %Y")
                try:
                    missing_ents.remove('start date')
                except:
                    pass

                try:
                    missing_ents.remove('end date')
                except:
                    pass
                #Add start date key with start date value
                #Reove start date for missing ent value
            else:
                try:
                    missing_ents.remove('date')
                except:
                    pass
                #remove date from missing_ents


    #New Stuff--------
        print('available_entities_dic after: ',available_entities_dic)
        print('missing_ents after: ',missing_ents)
        if len(missing_ents) !=0:
            #Available entities should send entity values and entity names, this is a dictionary.
            #This is so that the client side script could send another request to the final function once all required
            #Information is present
            #reTranslate = [intent,missing_ents, available_entities_dic]
            reTranslate = {'intent': intent,'missing_ents': missing_ents,'available_entities_dic': available_entities_dic}

            gc.collect()

            return json.dumps(reTranslate)
        else:
            #This should direct to the corresponding function to yield a result
            #Available entities should send entity values and entity names, this is a dictionary.
            reTranslate = {'intent': intent,'missing_ents': missing_ents,'available_entities_dic': available_entities_dic}
            #free shit

            gc.collect()

            return json.dumps(reTranslate)
    except:
        reTranslate = {'intent': 'error_handle','missing_ents': [],'available_entities_dic': {}}
        #free shit

        gc.collect()

        return json.dumps(reTranslate)


def compute(text):
    #try:
    gc.collect()
    #Cap the duration of compute function in routes to 210 seconds
    greetings = ['Hello, just enter any query on Twitter data.', "I am feeling well.", "All systems good to go. ", "I am doing great", "Hi, let my artificial intelligence help your human intelligence :)"]
    statement = json.loads(text)
    #----All this is the processing steps
    intent = statement[0]
    missing = statement[1]
    available = statement[2]

    data_final = missing.copy()   # start with x's keys and values
    data_final.update(available)
    data_return = {'intent':intent, 'entities': data_final}

    #print(data_final)
    #data_final['intent'] = intent
    #----------processing over-------------

    print(data_final)
    if intent == 'hashtagfind':
        place = data_final['location']
        trends = get_hashtags(place, consumer_key, consumer_secret)
        process = psutil.Process(os.getpid())
        print(process.memory_info().rss)
        gc.collect()
        return trends
    if intent == 'greet':
        gc.collect()
        return [random.choice(greetings)]
    elif intent == 'Twit_follower_count':
        if 'handle' in list(data_final.keys()):
            handle = data_final['handle']
            follower_counts = FollowerCountsOther(handle, consumer_key, consumer_secret)
        else:
            follower_counts = FollowerCountsOwn(consumer_key, consumer_secret)
        process = psutil.Process(os.getpid())
        print(process.memory_info().rss)
        gc.collect()
        return follower_counts
    elif intent == 'eng_comparison':
        start_date_string = data_final['start date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        start_date = cal.parseDT(start_date_string, now)[0]

        end_date_string = data_final['end date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        handle1 = data_final['handle1']
        handle2 = data_final['handle2']
        end_date = cal.parseDT(end_date_string, now)[0]
        if 'type' in list(data_final.keys()):
            types = data_final['type']
            comparison = TwitCompareEngType(start_date, end_date, handle1, handle2, types, consumer_key, consumer_secret)
        else:
            comparison = TwitterEngagementComparison(start_date, end_date, handle1, handle2, consumer_key, consumer_secret)
        process = psutil.Process(os.getpid())
        print(process.memory_info().rss)
        gc.collect()
        return comparison


    elif intent == 'engagement_Twitter_plain':
        start_date_string = data_final['start date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        start_date = cal.parseDT(start_date_string, now)[0]

        end_date_string = data_final['end date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        end_date = cal.parseDT(end_date_string, now)[0]
        if 'type' not in list(data_final.keys()):
            if 'handle' in list(data_final.keys()):
                handle = data_final['handle']
                engagement = TwitterOtherEngagement(start_date, end_date, handle, consumer_key, consumer_secret)
            else:
                engagement = TwitterEngagement(start_date, end_date, consumer_key, consumer_secret)
        else:
            types = data_final['type']
            if 'handle' in list(data_final.keys()):
                handle = data_final['handle']
                engagement = TwitOtherEngbyTypePlot(start_date, end_date, handle, types, consumer_key, consumer_secret)
            else:
                engagement = TwitOwnEngbyTypePlot(start_date, end_date,types, consumer_key, consumer_secret)
        process = psutil.Process(os.getpid())
        print(process.memory_info().rss)
        gc.collect()
        return engagement

    #This is error handling for top hashtags vs top tweets confusion
    #f intent is top hashtags or top tweets:
	#if posts in entity dict:
		#top tweets
	#else:
        #top hashtags
    elif intent == 'Twitter_sentiment':
        start_date_string = data_final['start date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        start_date = cal.parseDT(start_date_string, now)[0]

        end_date_string = data_final['end date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        end_date = cal.parseDT(end_date_string, now)[0]
        if 'handle' in list(data_final.keys()):
            handle = data_final['handle']
            sentiment = TweetSentimentOther(start_date, end_date, handle, consumer_key, consumer_secret)
        else:
            sentiment = TweetSentimentOwn(start_date, end_date, consumer_key, consumer_secret)
        process = psutil.Process(os.getpid())
        print(process.memory_info().rss)
        gc.collect()
        return sentiment
    elif intent == 'Twitter_searchAI':
        search_term = data_final['search term']
        process = psutil.Process(os.getpid())
        print(process.memory_info().rss)
        gc.collect()
        if len(search_term) == 1:
            search_term = search_term[0]
            return tweetsearchTimed(search_term, consumer_key, consumer_secret)
        elif len(search_term) >= 2:
            keyword = search_term[0]
            keyword2 = search_term[1]
            return tweetsearchTimedcompare(keyword, keyword2,consumer_key, consumer_secret)
        else:
            return 'You did not provide a search term'


    elif intent == 'twitter_percent_type':
        start_date_string = data_final['start date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        start_date = cal.parseDT(start_date_string, now)[0]

        #Just to get the type string
        entity_type = data_final['type']

        end_date_string = data_final['end date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        end_date = cal.parseDT(end_date_string, now)[0]
        if 'handle' in list(data_final.keys()):
            handle = data_final['handle']
            twitbytype = TwitOtherPercentEntity(start_date, end_date, handle, entity_type, consumer_key, consumer_secret)

        else:
            twitbytype = TwitOwnPercentEntity(start_date, end_date, entity_type, consumer_key, consumer_secret)
        process = psutil.Process(os.getpid())
        print(process.memory_info().rss)
        gc.collect()
        return twitbytype


    elif intent == 'top_hashtags':
        start_date_string = data_final['start date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        start_date = cal.parseDT(start_date_string, now)[0]
        #Maybe switch this to an IF else statement

        number = data_final['count']
        try:
            n = int(number)
        except:
            n = w2n.word_to_num(number)
        print(n)

        end_date_string = data_final['end date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        end_date = cal.parseDT(end_date_string, now)[0]
        if 'posts' in data_final.keys():
            if 'handle' in list(data_final.keys()):
                handle = data_final['handle']
                toptweets = TopTweetsOther(start_date, end_date, n, handle, consumer_key, consumer_secret)
            else:
                toptweets = TopTweetsOwn(start_date, end_date, n, consumer_key, consumer_secret)
            print(toptweets)
            process = psutil.Process(os.getpid())
            print(process.memory_info().rss)
            gc.collect()
            return toptweets
        else:
            if 'handle' in list(data_final.keys()):
                handle = data_final['handle']
                tophashtags = TopHashtagsOther(start_date, end_date, handle, n, consumer_key, consumer_secret)
            else:
                tophashtags = TopHashtagsOwn(start_date, end_date, n, consumer_key, consumer_secret)
            print(tophashtags)
            process = psutil.Process(os.getpid())
            print(process.memory_info().rss)
            gc.collect()
            return tophashtags


    elif intent == 'top_tweets':
        start_date_string = data_final['start date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        start_date = cal.parseDT(start_date_string, now)[0]
        #Maybe switch this to an IF else statement

        number = data_final['count']
        try:
            n = int(number)
        except:
            n = w2n.word_to_num(number)
        print(n)

        end_date_string = data_final['end date']
        cal = pdt.Calendar()
        now = datetime.datetime.now()
        end_date = cal.parseDT(end_date_string, now)[0]
        if 'posts' in data_final.keys():
            if 'handle' in list(data_final.keys()):
                handle = data_final['handle']
                toptweets = TopTweetsOther(start_date, end_date, n, handle, consumer_key, consumer_secret)
            else:
                toptweets = TopTweetsOwn(start_date, end_date, n, consumer_key, consumer_secret)
            print(toptweets)
            process = psutil.Process(os.getpid())
            print(process.memory_info().rss)
            gc.collect()
            return [toptweets]
        else:
            if 'handle' in list(data_final.keys()):
                handle = data_final['handle']
                tophashtags = TopHashtagsOther(start_date, end_date, handle, n, consumer_key, consumer_secret)
            else:
                tophashtags = TopHashtagsOwn(start_date, end_date, n, consumer_key, consumer_secret)
            print(tophashtags)
            process = psutil.Process(os.getpid())
            print(process.memory_info().rss)
            gc.collect()
            return tophashtags

    elif intent == 'reach':

        return ['Fora is unable to provide statistics pertaining to reach as of this moment due to limitations in the data mining capabilities Twitter allows. In the upcoming iterations (primarily paid versions), we will include reach data. Thank you for being understanding']
    elif intent == 'impressions':
        return ['Fora is unable to provide statistics pertaining to impressions as of this moment due to limitations in the data mining capabilities Twitter allows. In the upcoming iterations (primarily paid versions), we will include impressions data. Thank you for being understanding']


    else:
        return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']
    #except:
    #    return ['There was an error in answering your query. Could you please rephrase your question with all the required information?']

#The problem is with the compute function
@bp.route('/compute', methods=['POST'])
@login_required
def compute_text():
    return jsonify({'text': compute(request.form['text'])})



@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    return render_template("index.html", title='Home Page' )

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    #throw in a redis function call here that spits out 'stuff' to terminal every 15 seconds for 6 minutes
    return jsonify({'text': translate(request.form['text'])})




#-------------------Calendar-------------------
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar():
    return render_template("calendar.html", title='Schedule' )
#----------------------------------------------

def sched_maker(increment, repeat_no, date_out):
    schedtimes = []
    post_date = datetime_convert(date_out)
    for i in range(0,repeat_no):
      post_date += datetime.timedelta(days=increment)*i
      schedtimes.append(schedtime_calc_dt(post_date))
    return schedtimes


#@bp.route('/post_stuff', methods=['GET', 'POST'])
#@login_required
def post_stuff():
    #All the variables
    Facebookbox = request.args.get('Facebook')
    Twitterbox = request.args.get('Twitter')
    GooglePlusbox = request.args.get('GooglePlus')
    FacebookMessage = request.args.get('FacebookMessage')
    TwitterMessage = request.args.get('TwitterMessage')
    GoogleMessage = request.args.get('GoogleMessage')
    GoogleImage = request.args.get('GoogleImage')
    Repeat = request.args.get('Repeat')
    NoRepeat = request.args.get('NoRepeat')
    frequency = request.args.get('frequency')
    repeats = request.args.get('repeats')
    dates= request.args.get("datetime")

    date_in = dates
    date_out = str(datetime.datetime(*[int(v) for v in date_in.replace('T', '-').replace(':', '-').split('-')]))
    #if request.method == 'GET':
    if request.method == 'GET':
        #Twitter, get these tokens from a database query. Use current user id as it is faster
        Twitter_record_last = Twittertokens.query.filter_by(user_id = current_user.id).order_by(Twittertokens.id.desc()).first()
        token = Twitter_record_last.token
        token_secret = Twitter_record_last.token_secret

        Facebook_record_last = Facebooktokens.query.filter_by(user_id = current_user.id).order_by(Facebooktokens.id.desc()).first()
        access_token_fb = Facebook_record_last.access_token_fb
        #-----------Essential legacy code------------------------------------
        #token, token_secret = session['token']
        #Facebook, really need to get this from backend, otherwise cant test simultaneously
        #access_token_fb = session['facebook_oauth_token']['access_token']
        graph = fb.GraphAPI(access_token=access_token_fb, version=2.7)
        pages = graph.get_object("me/accounts")
        page_selected =  pages['data'][0]['id']
        token_page = pages['data'][0]['access_token']
        #------------------------------------------------------------------
        if request.args.get('Submit')== 'Schedule':
            if Repeat == 'no':
                schedtime = schedtime_calc(date_out)
                if Twitterbox != None and TwitterMessage != None:
                    schedule_tweet_task.apply_async(args=[TwitterMessage, consumer_key, consumer_secret, callback,token, token_secret], eta = schedtime)
                if Facebookbox != None and FacebookMessage != None:
                    schedule_fbpost_task.apply_async(args=[FacebookMessage, token_page, page_selected], eta=schedtime)
            else:
                if frequency == 'daily':
                    #Make a function called repeated schedule
                    repeat_no = int(repeats)
                    increment = 1
                    schedtimes_all = sched_maker(increment, repeat_no, date_out)
                    for schedtime in schedtimes_all:
                        if Twitterbox != None and TwitterMessage != None:
                            schedule_tweet_task.apply_async(args=[TwitterMessage, consumer_key, consumer_secret, callback,token, token_secret], eta= schedtime)
                        if Facebookbox != None and FacebookMessage != None:
                            schedule_fbpost_task.apply_async(args=[FacebookMessage, token_page, page_selected], eta=schedtime)
                if frequency == 'weekly':
                    repeat_no = int(repeats)
                    increment = 7
                    schedtimes_all = sched_maker(increment, repeat_no, date_out)
                    for schedtime in schedtimes_all:
                        if Twitterbox != None and TwitterMessage != None:
                            schedule_tweet_task.apply_async(args=[TwitterMessage, consumer_key, consumer_secret, callback,token, token_secret], eta= schedtime)
                        if Facebookbox != None and FacebookMessage != None:
                            schedule_fbpost_task.apply_async(args=[FacebookMessage, token_page, page_selected], eta=schedtime)


                if frequency == 'monthly':
                    repeat_no = int(repeats)
                    increment = 28
                    schedtimes_all = sched_maker(increment, repeat_no, date_out)
                    for schedtime in schedtimes_all:
                        if Twitterbox != None and TwitterMessage != None:
                            schedule_tweet_task.apply_async(args=[TwitterMessage, consumer_key, consumer_secret, callback,token, token_secret], eta= schedtime)
                        if Facebookbox != None and FacebookMessage != None:
                            schedule_fbpost_task.apply_async(args=[FacebookMessage, token_page, page_selected], eta=schedtime)


        elif request.args.get('Submit') == 'ShareNow':
            if Twitterbox != None and TwitterMessage != None:
                schedule_tweet_task.apply_async(args=[TwitterMessage, consumer_key, consumer_secret, callback,token, token_secret])
            if Facebookbox != None and FacebookMessage != None:
                schedule_fbpost_task.apply_async(args=[FacebookMessage, token_page, page_selected])

        else:
            pass
    return redirect('/index')
#--------------------------

@bp.route('/smart_post', methods=['GET', 'POST'])
@login_required
def smart_post():
    return render_template('smart_post.html', title='Smart Post', feeds = FeedItem.query.all())

#-----------------------------------------------
@bp.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    form = analyticsForm()
    #-----------

    #------Bokeh

    if form.validate_on_submit():
        flash('Fora is yet to go live.')
        return redirect(url_for('main.analytics'))
    else:
        pass
    return render_template('analytics.html', title='Ask Fora',
                           form=form)



colors = {
    'Black': '#000000',
    'Red':   '#FF0000',
    'Green': '#00FF00',
    'Blue':  '#0000FF',
}

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

@bp.route('/bokeh', methods=['GET', 'POST'])
@login_required
def bokeh():
    """ Very simple embedding of a polynomial chart

    """

    # Grab the inputs arguments from the URL
    args = request.args

    # Get all the form arguments in the url with defaults
    color = getitem(args, 'color', 'Black')
    _from = int(getitem(args, '_from', 0))
    to = int(getitem(args, 'to', 10))

    # Create a polynomial line graph with those arguments
    x = list(range(_from, to + 1))
    fig = figure(title="Polynomial")
    fig.toolbar.logo = None

    fig.line(x, [i ** 2 for i in x], color=colors[color], line_width=2)

    resources = INLINE.render()

    script, div = components(fig)
    html = render_template(
        'bokeh.html',
        plot_script=script,
        plot_div=div,
        resources=resources,
        color=color,
        _from=_from,
        to=to
    )
    return encode_utf8(html)

from bokeh.sampledata.iris import flowers
from bokeh.models import HoverTool

@bp.route('/twitter', methods=['GET', 'POST'])
@login_required
def twitter():
    return redirect('/twitter_login')

    # Grab the inputs arguments from the URL
    #return render_template("twitter.html", title='Authorize Twitter' )

@bp.route('/bokeh2', methods=['GET', 'POST'])
@login_required
def bokeh2():
    """ Very simple embedding of a scatter plot

    """
    hover = HoverTool(tooltips = None, mode = 'hline')

    plot = figure(title = 'Iris Plot', tools = [hover, 'pan','wheel_zoom','crosshair'])

    plot.circle(flowers['petal_length'],
                flowers['sepal_length'],
                size =10,alpha =0.5, hover_color  = 'red')
    plot.toolbar.logo = None
    resources = INLINE.render()

    script, div = components(plot)
    html = render_template(
        'bokeh2.html',
        plot_script=script,
        plot_div=div,
        resources=resources,
    )
    return encode_utf8(html)

#---------
@bp.route('/bokeh3', methods=['GET', 'POST'])
@login_required
def bokeh3():
    """ Very simple embedding of a bar chart

    """
    hover = HoverTool(tooltips = None, mode = 'hline')
    fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']

    p = figure(x_range=fruits, plot_height=250, title="Fruit Counts", tools  = [hover, 'pan','wheel_zoom','crosshair', 'save', 'reset'])
    p.vbar(x=fruits, top=[50, 23, 14, 28, 42, 65], width=0.9, alpha =0.5, color = random.sample(color_s, len(fruits)))

    p.xgrid.grid_line_color = None
    p.y_range.start = 0


    #plot = figure(title = 'Iris Plot', tools = [hover, 'crosshair'])

    #plot.circle(flowers['petal_length'],
    #            flowers['sepal_length'],
    #            size =10,alpha =0.5, hover_color  = 'red')
    p.toolbar.logo = None
    resources = INLINE.render()

    script, div = components(p)
    html = render_template(
        'bokeh3.html',
        plot_script=script,
        plot_div=div,
        resources=resources,
    )
    return encode_utf8(html)

def post_data():
    users = User.query.all()
    names = [user.username for user in users]
    id_s = [user.id for user in users]
    post_num = [len(Post.query.filter_by(user_id=id).all()) for id in id_s]
    return names, post_num

color_s = ['Pink', 'HotPink', 'DeepPink', 'MediumVioletRed',
        'Salmon', 'DarkSalmon', 'LightCoral', 'IndianRed', 'Crimson', 'FireBrick', 'DarkRed', 'Red',
        'OrangeRed', 'Tomato', 'Coral', 'DarkOrange', 'Orange','Yellow',  'LemonChiffon', 'PapayaWhip',
        'Moccasin', 'PeachPuff',  'Khaki', 'DarkKhaki', 'Gold',
        'Cornsilk', 'BlanchedAlmond', 'Bisque', 'Wheat', 'BurlyWood', 'Tan',
        'DarkOliveGreen', 'Olive', 'OliveDrab', 'YellowGreen', 'LimeGreen', 'Lime', 'LawnGreen',
         'PowderBlue', 'SkyBlue',  'DeepSkyBlue', 'DodgerBlue',
        'Lavender', 'Thistle', 'Plum', 'Violet', 'Orchid', 'Fuchsia', 'Magenta', 'MediumOrchid']

@bp.route('/bokeh4', methods=['GET', 'POST'])
@login_required
def bokeh4():
    """ Very simple embedding of a polynomial chart

    """
    names, post_num = post_data()
    hover = HoverTool(tooltips = None, mode = 'hline')

    p = figure(x_range=names, plot_height=250, title="Post Counts", tools  = [hover, 'pan','wheel_zoom','crosshair', 'save', 'reset'])
    p.vbar(x=names, top=post_num, width=0.9, alpha =0.9, color = random.sample(color_s, len(names)))

    p.xgrid.grid_line_color = None
    p.y_range.start = 0


    #plot = figure(title = 'Iris Plot', tools = [hover, 'crosshair'])

    #plot.circle(flowers['petal_length'],
    #            flowers['sepal_length'],
    #            size =10,alpha =0.5, hover_color  = 'red')
    p.toolbar.logo = None
    resources = INLINE.render()

    script, div = components(p)
    html = render_template(
        'bokeh4.html',
        plot_script=script,
        plot_div=div,
        resources=resources,
    )
    return encode_utf8(html)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following %(username)s!', username=username)
    return redirect(url_for('main.user', username=username))

#This is a redundant function, however I will place this so that code doesn't break
@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %(username)s not found.', username=username)
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %(username)s.', username=username)
    return redirect(url_for('main.user', username=username))
