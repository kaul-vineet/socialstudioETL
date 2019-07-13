import requests
import datacon
from flask import Flask, render_template, request, Response
import pprint 
import simplejson as json
import pandas as pd
import arrow
import os
import time as time

app=Flask(__name__)

@app.route('/viz')
def index():
    return render_template('interactive.html')

@app.route("/viz-data")
def viz_data():
    df = datacon.create_dataset()
    
    #Below renames the columns
    df1= df.rename(columns={0: 'CASE_ID', 1: 'HEADLINE',
                            2: 'AUTHOR',3: 'CONTENT',4: 'MEDIA_PROVIDER',
                            5: 'PUBLISH_DATE', 6: 'CLASSIFICATION'})
    df1.sort_values(by=['PUBLISH_DATE'], inplace=True, ascending=False)
    TIME, MEDIA_PROVIDER, POST_FREQUENCY = [],[],[]
    TIME = df1['PUBLISH_DATE']
    MEDIA_PROVIDER = df1['MEDIA_PROVIDER']
    df_timeseries = pd.DataFrame([TIME,MEDIA_PROVIDER]).T
    df_timeseries['PUBLISH_DATE'] = pd.to_datetime(df_timeseries['PUBLISH_DATE'])
    df_timeseries['PUBLISH_DATE'] = df_timeseries['PUBLISH_DATE'].values.astype('<M8[m]')
    df_timeseries = df_timeseries.groupby(['PUBLISH_DATE','MEDIA_PROVIDER'])['MEDIA_PROVIDER'].count()
    df_timeseries = df_timeseries.unstack().fillna(value=0)
    print(df_timeseries.head(100))
    def generate_random_data():
        for index, row in df_timeseries.iterrows():
            json_data = json.dumps({'time': index.strftime('%H:%M:%S'), 'value': row['TWITTER']})
            #print(row['TWITTER'])
            #{'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': random.random() * 100}
            #data:{"time": "2019-07-13 00:31:44", "value": 74.03604913808967}
            yield f"data:{json_data}\n\n"
            time.sleep(4)
    return Response(generate_random_data(), mimetype='text/event-stream')

@app.route("/")
def show_tables():
    df = datacon.create_dataset()
    #Below renames the columns
    df1= df.rename(columns={0: 'CASE_ID', 1: 'HEADLINE',
                            2: 'AUTHOR',3: 'CONTENT',4: 'MEDIA_PROVIDER',
                            5: 'PUBLISH_DATE', 6: 'CLASSIFICATION'})
    df1.sort_values(by=['PUBLISH_DATE'], inplace=True, ascending=False)
    print(df1.unstack().fillna(value=0).head())
    #Below code will produce a timestamp of when the API data was requested
    #utc = arrow.utcnow()
    #df['PullTime'] = utc.to('US/Pacific')
    
    df1 = df1[df1.MEDIA_PROVIDER != 'TWITTER'].head(10)
    return render_template('view.html',tables=[df1.to_html(classes='female')],
    titles = ['na', 'SOCIAL CASES'])

if __name__ == "__main__":
    app.run(debug=True)
