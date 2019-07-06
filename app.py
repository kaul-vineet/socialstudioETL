import requests
from flask import Flask, render_template, request
import pprint 
import simplejson as json
import http.client
import pandas as pd
from time import time, mktime
from datetime import datetime, date, timedelta, time
import arrow
import os

app=Flask(__name__)

@app.route("/")


def show_tables():

    pd.set_option('display.max_colwidth', -1)

    if os.getenv('VIRTUAL_ENV'):
        print('Using Virtualenv')
        data = {'grant_type': 'password', 
        'client_id': 'mcxxb09790ab6c4b41c99d56a29a55142bbb', 
        'client_secret': 'caf59c1728ec47f2aceeed68d61f81c8', 
        'username': 'r6-vkaul', 
        'password': 'Tutakhamen@1234'}
        topic_profile = 1340413
    else:
        print('Not using Virtualenv')
        data = {'grant_type': 'password', 
        'client_id': os.environ['client_id'], 
        'client_secret': os.environ['client_secret'], 
        'username': os.environ['username'], 
        'password': os.environ['password']}
        topic_profile = os.environ['topic_profile']
        
    result = requests.post('https://api.socialstudio.radian6.com/oauth/token', data=data)   
    load = json.loads(result.content)
    key = load['access_token']
    print ('LOGIN SUCCESS: ' + key)

    #create a midnight timestamp based on today's date:
    midnight = datetime.combine(date.today(), time.min)
    #create a time stamp value for yesterday at 00:00:00 hours:
    yesterday_midnight = midnight - timedelta(days=1)
    #create a time stamp value for yesterday at 23:59:00 hours, before midnight hits:
    yesterday_beforemidnight = midnight - timedelta(minutes=1)

    #below variable converts 'yesterday_midnight' into unix time
    sec_since_epochy = mktime(yesterday_midnight.timetuple()) + yesterday_midnight.microsecond/1000000.0
    #below code converts the 'sec_since_epochy' into epoch milliseconds, since it's the only timestamp social studio accepts
    startDate = int(sec_since_epochy * 1000)

    #below variable converts 'yesterday_beforemidnight' into unix time
    sec_since_epochb = mktime(yesterday_beforemidnight.timetuple()) + yesterday_beforemidnight.microsecond/1000000.0
    #below code converts the 'sec_since_epochb' into epoch milliseconds, since it's the only timestamp social studio accepts
    endDate = int(sec_since_epochb * 1000)

    #startDate and endDate are converted into strings wich is the only datatype the query string accepts
    startDate = str(startDate)
    endDate = str(endDate)

    headers = {"access_token": key}
    #we integrated the python variable strings startDate and endDate into the http query string below to query data 
    #from the previous dat in an automated fashion
    url = 'https://api.socialstudio.radian6.com/v3/posts?topics=' + str(topic_profile) + '&\
    startDate=' + startDate + '&endDate=' + endDate + '&limit=1000'
    #as you can see, the http query string below has epoch milliseconds as a startDate and endDate
    #url = 'https://api.socialstudio.radian6.com/v3/posts?topics=1135449&startDate=1506927600000&endDate=1507013940000&limit=1000'
    resp = requests.get(url, headers=headers)
    Json = json.loads(resp.content)

    TOPICS,ASSIGNED_USER,ARTICLE_ID,EXTERNAL_ID,HEADLINE,AUTHOR,\
    CONTENT,ARTICLE_URL,MEDIA_PROVIDER,REGION,LANGUAGE,POST_STATUS,\
    PUBLISH_DATE,HARVESTED_DATE,CLASSIFICATION,TAGS=\
    [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]


    for data in Json['data']:
        ARTICLE_ID.append(data['id']),
        HEADLINE.append(data['title']),
        AUTHOR.append(data['author']['title']),
        CONTENT.append(data['content']),
        MEDIA_PROVIDER.append(data['mediaProvider']['title']),
        PUBLISH_DATE.append(data['publishedDate']),
        CLASSIFICATION.append(data['classification'])
        
    df = pd.DataFrame([ARTICLE_ID,HEADLINE,AUTHOR,CONTENT,
                       MEDIA_PROVIDER,PUBLISH_DATE,CLASSIFICATION]).T

    #Below code will produce a timestamp of when the API data was requested
    #utc = arrow.utcnow()
    #df['PullTime'] = utc.to('US/Pacific')


    #Below renames the columns
    df1= df.rename(columns={0: 'CASE_ID', 1: 'HEADLINE',
                            2: 'AUTHOR',3: 'CONTENT',4: 'MEDIA_PROVIDER',
                            5: 'PUBLISH_DATE', 6: 'CLASSIFICATION'})
    df1.sort_values(by=['PUBLISH_DATE'], inplace=True, ascending=False)
    df1 = df1[df1.MEDIA_PROVIDER != 'TWITTER'].head(8)
    
    return render_template('view.html',tables=[df1.to_html(classes='female')],
    titles = ['na', 'SOCIAL CASES'])

if __name__ == "__main__":
    app.run(debug=True)
