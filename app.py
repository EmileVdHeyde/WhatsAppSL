# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 10:29:05 2020

@author: EmileVDH
"""

#streamlit run wapp.py

#All Packages Needed 
import pandas as pd
import streamlit as st
import os
import datetime as datetime
import numpy as np
import re 
import datetime
import emoji
import altair as alt
from wordcloud import WordCloud, STOPWORDS 
import matplotlib.pyplot as plt 
#Main Heading
st.title("WhatsApp Analysis Tool")

st.header("Welcome Let do some cool stuff ")
st.markdown("To begin up load your chat file")
#link to how to upload chat file

#Widget to upload file
uploaded_file = st.file_uploader("Choose a txt file", type="txt")

#Py code to transform to data frame
chat = []
for line in uploaded_file:
    chat.append(line)


###shome kind of data cache
#@st.cache
#def load_data(nrows):


def extract_emojis(s):
  return ''.join(c for c in s if c in emoji.UNICODE_EMOJI)

W_dict={'Date':[],'Time':[],'Name':[],'Content':[],'Emoji':[],'WordCount':[]}

for k in range(len(chat)):
    res = re.findall(r'\[.*?\]', chat[k])
    if len(res)==0 :
          continue
    if chat[k].count(':') <3 :
          continue
    res2=res[0].strip('[]')
    date=res2.split(',')[0]
    time=res2.split(',')[1]
    #timefinal=datetime.strftime("%H:%M:%S")  ##strptime(time, '%I:%M%p')
    W_dict['Date'].append(date)
    W_dict['Time'].append(time)
    name = re.findall(r'\].*?\:', chat[k]) 
    name2=re.findall(r"(?i)\b[a-z]+\b", name[0])
    namefinal=''.join(name2)
    W_dict['Name'].append(namefinal)
    body=re.findall(r'\:.*?\n' ,chat[k]) 
    bodyfinal=body[0].split(':')[3].strip()
    W_dict['Content'].append(bodyfinal)
    em = extract_emojis(bodyfinal)
    W_dict['Emoji'].append(em)
    if len(bodyfinal)<2 :
        wc=0
    else: 
        wc=len(re.findall(r'\w+', bodyfinal)) 
    W_dict['WordCount'].append(wc)

df=pd.DataFrame.from_dict(W_dict)

#clean out the numberslinks and other elements

def clean_text(df, text_field, new_text_field_name):
    df[new_text_field_name] = df[text_field].str.lower()
    df[new_text_field_name] = df[new_text_field_name].apply(lambda elem: re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", elem))  
    # remove numbers
    df[new_text_field_name] = df[new_text_field_name].apply(lambda elem: re.sub(r"\d+", "", elem))
    
    return df

df = clean_text(df, "Content", "text_clean")

#Remove Stop Words

stop = [ "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "it", "it's", "its", "itself", "let's", "me", "more", "most", "my", "myself", "nor", "of", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "she'd", "she'll", "she's", "should", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "we'd", "we'll", "we're", "we've", "were", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "would", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves","image","omitted","im","u",""]
df['text_clean'] = df['text_clean'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))

df['DateTimeString'] = df['Date'].str.cat(df['Time'],sep=" ")
df['DateTime'] = df['DateTimeString'].apply(lambda x: datetime.datetime.strptime(x, '%Y/%m/%d %I:%M:%S %p'))
df['Day_name'] = df['DateTime'].dt.day_name()
df['DateYM'] = df['DateTime'].dt.strftime('%Y%m')
df['Previous_Any_lagged_DT'] = df['DateTime'].shift(1)
df['Response_Time'] = df['DateTime'] - df['Previous_Any_lagged_DT']

#display dataframe       
#st.dataframe(df.tail())

#1 show unique plates names
st.header("Who is in this Data? ")
#st.dataframe(df['Name'].unique())
a=list(df['Name'].unique())

st.write(a[0] )
st.write(a[1] )

#2 show date range 
st.header("What is the Date Range? ")
st.text(df['DateTimeString'].head(1))
st.text(df['DateTimeString'].tail(1))

#3 Show Monthy messages Chart 
st.header("How Often Do you message? ")
dw  = pd.DataFrame(df.groupby(['DateYM','Name'])['Content'].count())
dw = dw.reset_index()
line = alt.Chart(dw).mark_line().encode(
    x='DateYM',
    y='Content',
    color='Name'
)
st.altair_chart(line)


#4 Show Monthy average words per message Chart
st.header("Average words Per Message over Time? ")
dw  = pd.DataFrame(df.groupby(['DateYM','Name'])['WordCount'].mean())
dw = dw.reset_index()
line = alt.Chart(dw).mark_line().encode(
    x='DateYM',
    y='WordCount',
    color='Name'
)
st.altair_chart(line)


#Create word counts splits and TWO data frames Data Frames

from spacy.lang.en.stop_words import STOP_WORDS
import collections
import itertools

stopwords = set(STOP_WORDS) 

comment_words = '' 
for val in df.loc[df['Name'] == a[0] ]['text_clean']: 
      
    # typecaste each val to string 
    val = str(val) 
  
    # split the value 
    tokens = val.split() 
      
    # Converts each token into lowercase 
    for i in range(len(tokens)): 
        tokens[i] = tokens[i].lower() 
      
    comment_words += " ".join(tokens)+" "
 
comment_words_A=comment_words
z=comment_words.split()
all_words_no_urls = list(itertools.chain(z))
counts_no_urls = collections.Counter(all_words_no_urls)

dfA = pd.DataFrame(counts_no_urls.most_common(),
                             columns=['words', 'count'])


dfAs = pd.DataFrame(counts_no_urls.most_common(50),
                             columns=['words', 'count'])

comment_words = '' 
for val in df.loc[df['Name'] == a[1] ]['text_clean']: 
      
    # typecaste each val to string 
    val = str(val) 
  
    # split the value 
    tokens = val.split() 
      
    # Converts each token into lowercase 
    for i in range(len(tokens)): 
        tokens[i] = tokens[i].lower() 
      
    comment_words += " ".join(tokens)+" "

comment_words_B=comment_words
z=comment_words.split()
all_words_no_urls = list(itertools.chain(z))
counts_no_urls = collections.Counter(all_words_no_urls)

dfB = pd.DataFrame(counts_no_urls.most_common(),
                             columns=['words', 'count'])


dfBs = pd.DataFrame(counts_no_urls.most_common(50),
                             columns=['words', 'count'])

### Bar Charts Top 50
fig, ax = plt.subplots(figsize=(8, 8))
st.header('Top 50 words of : ' + a[0] )
#st.dataframe(dfA.head())
# Plot horizontal bar graph
dfAs.sort_values(by='count').plot.barh(x='words',
                      y='count',
                      ax=ax,
                      color="purple")
st.pyplot()

st.header('Top 50 words of : ' + a[1] )
#st.dataframe(dfB.head())
fig, ax = plt.subplots(figsize=(8, 8))
dfBs.sort_values(by='count').plot.barh(x='words',
                      y='count',
                      ax=ax,
                      color="cyan")
st.pyplot()



#Word Cloud 

st.header('WordCloud of : ' + a[0] )
wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = stopwords, 
                min_font_size = 10).generate(comment_words_A) 
  
# plot the WordCloud image                        
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
st.pyplot()

st.header('Word Cloud of : ' + a[1] )
wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = stopwords, 
                min_font_size = 10).generate(comment_words_B) 
  
# plot the WordCloud image                        
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
st.pyplot()
