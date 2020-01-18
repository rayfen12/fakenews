from flask import Flask, render_template,request,url_for
from flask_bootstrap import Bootstrap
import numpy as np
from twitter import *
import pandas as pd
import os
import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob,Word
import plotly.express as px
import plotly as py
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import os

port = int(os.environ.get('PORT', 5000))

pd.set_option('display.max_colwidth', -1)

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyse',methods=['POST'])
def analyze():
    select = request.form.get('comp_select')
    #get the raw text from the input box
    if request.method == 'POST' and select != "hdl":
        rawtext = request.form['rawtext']

        token = '1212463191910842368-l00ryMICeXQXXawl8w2zazEoFS7xDf'
        token_secret = 'hbzjFRq1r2ygkydPXfrwrhm5zTa54F3mYEm2wi7Q09DgA'
        consumer_key = 'g8V7jnF3dqMfg4LRhtobYB4Pl'
        consumer_secret = 'Y0SHSL0H9X9gCtuy07mJ3cp144DS2JhwX4Uvgda2ph8NvIUswJ'
        
    #Call Twitter API to request tweets with the $rawtext (using the $ for now for testing)
        t = Twitter(auth=OAuth(token, token_secret, consumer_key, consumer_secret))
        tweets= t.search.tweets(q=f'{str(select)}{rawtext}', include_rts=False, tweet_mode='extended',count=200)
    #Get the tweet text (tw1) and and the sentiment (tw2), appened them to lists
    #Also counted how many elements there are in each list to make sure they match
        m_dict = tweets['statuses']
        def device(tweet):
            if 'iPhone' in tweet['source'] or ('iOS' in tweet['source']):
                return 'iPhone'
            elif 'Android' in tweet['source']:
                return 'Android'
            elif 'Mobile' in tweet['source'] or ('App' in tweet['source']):
                return 'Mobile device'
            elif 'Mac' in tweet['source']:
                return 'Mac'
            elif 'Windows' in tweet['source']:
                return 'Windows'
            elif 'Bot' in tweet['source']:
                return 'Bot'
            elif 'Web' in tweet['source']:
                return 'Web'
            elif 'Instagram' in tweet['source']:
                return 'Instagram'
            elif 'Blackberry' in tweet['source']:
                return 'Blackberry'
            elif 'iPad' in tweet['source']:
                return 'iPad'
            else:
                return 'Other'
        tw_list_date = []
        tw_list_screen_name = []
        tw_list_text = []
        tw_list_retweet = []
        tw_list_likes = []
        tw_list_id = []
        tw_list_polarity = []
        for element in m_dict:
            tw_list_date.append(element['created_at'])
            tw_list_screen_name.append(element['user']['screen_name'])
            tw_list_text.append(element['full_text'])
            tw_list_retweet.append(element['retweet_count'])
            tw_list_likes.append(element['favorite_count'])
            tw_list_id.append(element['id'])
            analysis = TextBlob(element['full_text'])
            tw_list_polarity.append(analysis.sentiment.polarity)
        tw_df = pd.DataFrame(list(zip(tw_list_date, tw_list_screen_name, tw_list_text, tw_list_retweet, tw_list_likes, tw_list_polarity)), columns =['Date', 'Handle', 'Text', 'Retweets', 'Likes', 'Polarity'])
        sentiment_list = [] 
        for value in tw_df["Polarity"]: 
            if value == -1: 
                sentiment_list.append("Negative") 
            elif value > -1 and value < 0: 
                sentiment_list.append("Somewhat Negative")
            elif value == 0:
                sentiment_list.append('Neutral')
            elif value >= 0.1 and value <= 0.5:
                sentiment_list.append('Somewhat Postive')
            else: 
                sentiment_list.append("Positive") 
        # ================================================  
        tw_df['Sentiment'] = sentiment_list
        tw_df['Device'] = list(map(device, m_dict))
        tw_df1 = tw_df.loc[(tw_df['Retweets'] >= 1) & (tw_df['Retweets'] <= 70)]
        tw_html = tw_df1.to_html(classes=["table", "table-bordered", "table-striped", "table-hover"])
        tw_html2 = tw_html.replace('\n', '')
        # ================================================  
        average_sentiment = tw_df1["Polarity"].mean()
        fig2 = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = average_sentiment,
            mode = "gauge+number+delta",
            title = {'text': "Sentiment"},
            gauge = {'axis': {'range': [-1, 1]},
                    'bar': {'color': "white"},
                    'steps' : [
                        {"range":[-1,-0.9],"color":"#EB002E"},
                        {"range":[-0.9,-0.8],"color":"#E30C33"},
                        {"range":[-0.8,-0.7],"color":"#DC1838"},
                        {"range":[-0.7,-0.6],"color":"#D4243D"},
                        {"range":[-0.6,-0.5],"color":"#CD3143"},
                        {"range":[-0.5,-0.4],"color":"#CD3143"},
                        {"range":[-0.4,-0.3],"color":"#C53D48"},
                        {"range":[-0.3,-0.2],"color":"#B65652"},
                        {"range":[-0.2,-0.1],"color":"#AF6258"},
                        {"range":[-0.1,0],"color":"#A76E5D"},
                        {"range":[0,0.1],"color":"#988767"},
                        {"range":[0.1,0.2],"color":"#91936D"},
                        {"range":[0.2,0.3],"color":"#899F72"},
                        {"range":[0.3,0.4],"color":"#82AC77"},
                        {"range":[0.4,0.5],"color":"#7AB87C"},
                        {"range":[0.5,0.6],"color":"#73C482"},
                        {"range":[0.6,0.7],"color":"#6BD187"},
                        {"range":[0.7,0.8],"color":"#64DD8C"},
                        {"range":[0.8,0.9],"color":"#5CE991"},
                        {"range":[0.9,1],"color":"#55F697"}]}))
        fig3 = fig2.to_html()
        # ================================================  
        fig1 = px.scatter(tw_df1, x='Retweets', y='Polarity', hover_name="Handle", color = 'Sentiment')
        fig=fig1.to_html()
        # ================================================
        sorted_df= tw_df1.sort_values(by=['Polarity'],ascending = False).head(1)
        # best_tweet = sorted_df[sorted_df['polarity'] == sorted_df['polarity'].max()].head(1)
        best_tweet = sorted_df
        filtered_best_tweet = best_tweet.drop(columns=['Date', 'Retweets', 'Likes'])
        text1 = filtered_best_tweet.Text.tolist()
        name1 = filtered_best_tweet.Handle.tolist()
        pol1 = filtered_best_tweet.Polarity.tolist()
        sorted_df1= tw_df1.sort_values(by=['Polarity'],ascending = True).head(1)
        worst_tweet = sorted_df1
        # worst_tweet = sorted_df[sorted_df['polarity'] == sorted_df['polarity'].min()]
        filtered_worst_tweet = worst_tweet.drop(columns=['Date', 'Retweets', 'Likes'])
        text2 = filtered_worst_tweet.Text.tolist()
        name2 = filtered_worst_tweet.Handle.tolist()
        pol2 = filtered_worst_tweet.Polarity.tolist()
        # =======================================================
                        
        device_sum = tw_df1.Device.count()
        device_count = tw_df1.Device.value_counts()
        perc_of_device = device_count/device_sum*100
        perc_of_device = pd.DataFrame(device_count/device_sum*100)
        perc_of_device_reindex = perc_of_device.reset_index()
        perc_of_device2 = perc_of_device_reindex.rename(columns = {"index" : "Device Brand", "Device": "% of Device Brand used to create tweet" })
        fig6 = go.Figure(data=go.Bar(x=perc_of_device2['Device Brand'], y=perc_of_device2['% of Device Brand used to create tweet']))
        fig7=fig6.to_html()
        return render_template('index.html',wordfig1=fig7,pol1 = pol1[0],pol2 = pol2[0],name2 = name2[0], text2 = text2[0],name1= name1[0],text1=text1[0],rawtext=rawtext,tw_html2=tw_html2,fig=fig,fig3 = fig3,at="@",br="|")
    else:
        rawtext = request.form['rawtext']
        token = '1212463191910842368-l00ryMICeXQXXawl8w2zazEoFS7xDf'
        token_secret = 'hbzjFRq1r2ygkydPXfrwrhm5zTa54F3mYEm2wi7Q09DgA'
        consumer_key = 'g8V7jnF3dqMfg4LRhtobYB4Pl'
        consumer_secret = 'Y0SHSL0H9X9gCtuy07mJ3cp144DS2JhwX4Uvgda2ph8NvIUswJ'
        t = Twitter(auth=OAuth(token, token_secret, consumer_key, consumer_secret))
        tweets= t.statuses.user_timeline(screen_name=f'{rawtext}', count=100, include_rts=False, tweet_mode = 'extended')
    #Get the tweet text (tw1) and and the sentiment (tw2), appened them to lists
    #Also counted how many elements there are in each list to make sure they match
        tw_list_date = []
        tw_list_screen_name = []
        tw_list_text = []
        tw_list_retweet = []
        tw_list_likes = []
        tw_list_id = []
        tw_list_polarity = []
        for element in tweets:
            tw_list_date.append(element['created_at'])
            tw_list_screen_name.append(element['user']['screen_name'])
            tw_list_text.append(element['full_text'])
            tw_list_retweet.append(element['retweet_count'])
            tw_list_likes.append(element['favorite_count'])
            tw_list_id.append(element['id'])
            analysis = TextBlob(element['full_text'])
            tw_list_polarity.append(analysis.sentiment.polarity)
        tw_df = pd.DataFrame(list(zip(tw_list_date, tw_list_screen_name, tw_list_text, tw_list_retweet, tw_list_likes,  tw_list_polarity)), columns =['Date', 'Handle', 'Text', 'Retweets', 'Likes', 'Polarity'])
        sentiment_list = [] 
        for value in tw_df["Polarity"]: 
            if value == -1: 
                sentiment_list.append("Negative") 
            elif value > -1 and value < 0: 
                sentiment_list.append("Somewhat Negative")
            elif value == 0:
                sentiment_list.append('Neutral')
            elif value >= 0.1 and value <= 0.5:
                sentiment_list.append('Somewhat Postive')
            else: 
                sentiment_list.append("Positive") 
            
        # ================================================  
        tw_df['Sentiment'] = sentiment_list
        tw_df1 = tw_df.loc[(tw_df['Retweets'] >= 1) & (tw_df['Retweets'] <= 50000)]
        tw_html = tw_df1.to_html(classes=["table", "table-bordered", "table-striped", "table-hover"])
        tw_html2 = tw_html.replace('\n', '')
        # ================================================  
        average_sentiment = tw_df1["Polarity"].mean()
        fig2 = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = average_sentiment,
            mode = "gauge+number+delta",
            title = {'text': "Sentiment"},
            gauge = {'axis': {'range': [-1, 1]},
                    'bar': {'color': "white"},
                    'steps' : [
                        {"range":[-1,-0.9],"color":"#EB002E"},
                        {"range":[-0.9,-0.8],"color":"#E30C33"},
                        {"range":[-0.8,-0.7],"color":"#DC1838"},
                        {"range":[-0.7,-0.6],"color":"#D4243D"},
                        {"range":[-0.6,-0.5],"color":"#CD3143"},
                        {"range":[-0.5,-0.4],"color":"#CD3143"},
                        {"range":[-0.4,-0.3],"color":"#C53D48"},
                        {"range":[-0.3,-0.2],"color":"#B65652"},
                        {"range":[-0.2,-0.1],"color":"#AF6258"},
                        {"range":[-0.1,0],"color":"#A76E5D"},
                        {"range":[0,0.1],"color":"#988767"},
                        {"range":[0.1,0.2],"color":"#91936D"},
                        {"range":[0.2,0.3],"color":"#899F72"},
                        {"range":[0.3,0.4],"color":"#82AC77"},
                        {"range":[0.4,0.5],"color":"#7AB87C"},
                        {"range":[0.5,0.6],"color":"#73C482"},
                        {"range":[0.6,0.7],"color":"#6BD187"},
                        {"range":[0.7,0.8],"color":"#64DD8C"},
                        {"range":[0.8,0.9],"color":"#5CE991"},
                        {"range":[0.9,1],"color":"#55F697"}]}))
        fig3 = fig2.to_html()
        # ================================================  
        fig1 = px.scatter(tw_df1, x='Retweets', y='Polarity', hover_name="Handle", color = 'Sentiment')
        fig=fig1.to_html()
        # ================================================
        
        vect = TfidfVectorizer(ngram_range=(2,5), stop_words='english')
        summaries = "".join(tw_df1['Text'])
        ngrams_summaries = vect.build_analyzer()(summaries)
        word = Counter(ngrams_summaries).most_common(10)
        word_df = pd.DataFrame(word, columns=['common_words', 'word_count'])
        wordfig = px.bar(word_df,x='word_count',y='common_words', color = 'word_count',orientation = 'h',labels={'word_count':'Word Count', 'common_words': 'Common Words'}, height=400)
        wordfig1 = wordfig.to_html()
        # ========================================================
        sorted_df= tw_df1.sort_values(by=['Polarity'],ascending = False).head(1)
        # best_tweet = sorted_df[sorted_df['polarity'] == sorted_df['polarity'].max()].head(1)
        best_tweet = sorted_df
        filtered_best_tweet = best_tweet.drop(columns=['Date', 'Retweets', 'Likes'])
        text1 = filtered_best_tweet.Text.tolist()
        name1 = filtered_best_tweet.Handle.tolist()
        pol1 = filtered_best_tweet.Polarity.tolist()
        sorted_df1= tw_df1.sort_values(by=['Polarity'],ascending = True).head(1)
        worst_tweet = sorted_df1
        # worst_tweet = sorted_df[sorted_df['polarity'] == sorted_df['polarity'].min()]
        filtered_worst_tweet = worst_tweet.drop(columns=['Date', 'Retweets', 'Likes'])
        text2 = filtered_worst_tweet.Text.tolist()
        name2 = filtered_worst_tweet.Handle.tolist()
        pol2 = filtered_worst_tweet.Polarity.tolist()
        return render_template('index.html',pol1 = pol1[0],pol2 = pol2[0],name2 = name2[0], text2 = text2[0],name1= name1[0],text1=text1[0],wordfig1=wordfig1,rawtext=rawtext,tw_html2=tw_html2,fig=fig,fig3 = fig3,at="@",br="|")
if __name__ == '__main__':
    app.run()