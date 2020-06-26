# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 

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

#################################################################
##for debugging import data manually
with open("Quizo_chat.txt", encoding="utf8") as file_in:
    chat = []
    for line in file_in:
        chat.append(line)
#################################################################

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
st.text(df['Name'].unique())


#2 show date range 

st.header("What is the Date Range? ")
st.text(df['DateTimeString'].head(1).to_list())
st.text(df['DateTimeString'].tail(1).to_list())

#3 Show Monthy messages Chart 
st.header("How Often Do you message? ")
dw  = pd.DataFrame(df.groupby(['DateYM','Name'])['Content'].count())
dw = dw.reset_index()
option = st.multiselect( 'Who do you want to see?', dw['Name'].unique())


line = alt.Chart(dw[dw.Name.isin(option)]).mark_line().encode(
    x='DateYM',
    y='Content',
    color='Name' 
).properties(
    width=700,
    height=400 )
st.altair_chart(line)

#4 Show Monthy average words per message Chart
st.header("Average words Per Message over Time? ")
dw  = pd.DataFrame(df.groupby(['DateYM','Name'])['WordCount'].mean())
dw = dw.reset_index()


line = alt.Chart(dw[dw.Name.isin(option)]).mark_line().encode(
    x='DateYM',
    y='WordCount',
    color='Name' 
).properties(
    width=700,
    height=400 )
st.altair_chart(line)

#######################################################3
#Create word counts splits and N-amount of data frames.
  #to display N - amount of clouds 
  #Minimum is to show only the selected one 
  #best is to show n about and alow to quicly compare. 

from spacy.lang.en.stop_words import STOP_WORDS
import collections
import itertools
stopwords = set(STOP_WORDS) 

List_of_names =list(df['Name'].unique()) ## list to iterate through
len(List_of_names)
 ## total iterations
#for each we need dfAs for graph // comment_words_A for word cloud


###Create function for Comment WORDS (lIST OF WORDS SPEARTLY)
def FuncComWords(NAMEVAR):
    comment_words = '' 
    for val in df.loc[df['Name'] == NAMEVAR]['text_clean']: 
      
    # typecaste each val to string 
        val = str(val) 
  
    # split the value 
        tokens = val.split() 
      
    # Converts each token into lowercase 
        for i in range(len(tokens)): 
            tokens[i] = tokens[i].lower() 
      
        comment_words += " ".join(tokens)+" "
    BigCW['Name'].append(NAMEVAR)
    BigCW['comment_words'].append(comment_words)
  ## return(comment_words)
        
####end of function ##################################### 

#Populate the dictionary by parsing all the names into the function 

BigCW={'Name':[],'comment_words':[]}
for n in range(len(List_of_names)):
   nn=''
   nn=List_of_names[n]
   FuncComWords(nn)
   print(nn)

ndf=pd.DataFrame(BigCW)

##len(ndf)
##ndf['Name'].unique()
##ndf.iloc[5]
#ndf.iloc[1]['Name']
#ndf.iloc[1]['comment_words']
#
##Tables created used later   
#
##INTO A LIST 
#comment_words_A=ndf.iloc[1]['comment_words']
##SPLITS INTO INDIVIDULA WORDS
#z=comment_words_A.split()
#
##Not sure what this does
#all_words_no_urls = list(itertools.chain(z))
#
##Does a count of each word 
#counts_no_urls = collections.Counter(all_words_no_urls)
#
##all words 
#dfA = pd.DataFrame(counts_no_urls.most_common(),
#                             columns=['words', 'count'])
#
##smaller version of top 50 words
#dfAs = pd.DataFrame(counts_no_urls.most_common(50),
#                             columns=['words', 'count'])

##############################################################
#Create a table that has the Name of person , words , word count and top 50 or not 

#Big Split of words 

d = pd.DataFrame()


def SplitFunction(NAMEVAR):
    BigSW={'Word':[], 'Value':[]}
    temp = []
    global d
    for val in ndf.loc[ndf['Name'] == NAMEVAR]['comment_words']:
         #print(val) 
         z=val.split()
         #print(z)
         all_words_no_urls = list(itertools.chain(z))
         #print(all_words_no_urls)
         counts_no_urls = dict(collections.Counter(all_words_no_urls))
         #k=list(counts_no_urls.keys())
         #v=list(counts_no_urls.values())
         for key in list(counts_no_urls.keys()):
             aKey = key
             #print(key)
             BigSW['Word'].append(aKey)
         for key in list(counts_no_urls.values()):
             aKey = key
             #print(key)
             BigSW['Value'].append(aKey)
         dfall=pd.DataFrame(BigSW)
         dfall['Name'] = NAMEVAR
         if len(dfall)==0 :
            d=dfall
         else :
           temp=dfall
           d = pd.concat([d,temp])
     
        
for n in range(len(List_of_names)):
        nn=''
        nn=List_of_names[n]
        SplitFunction(nn)
        print(nn)

#print(d)

#######Add the counter 1 is most popular 

#d['Rank'] = d.groupby(by=['Name'])['Value'].transform(lambda x: x.rank())
#d['Rank'] = df.groupby(['ticker'])['Word']\
#                        .rank(pct=True)
#
#d['Rank'] = d.sort_values(['Value'], ascending=[False]) \
#             .groupby(['Name']) \
#             .cumcount() + 1
#
#dfAs=d[d.Name.isin(['Emile'])]
#dfAs.sort_values(by='Rank', ascending=False)
        
######Charting ###########################################################
        
st.header('Most Frequent Words' )
option2 = st.radio(
    'Who do you want to see?',
     List_of_names)

val = st.slider('Minimum frequency of Words')

dfAs=d[d.Name.isin([option2]) & (d.Value>val)]


# Plot horizontal bar graph
st.header("Bar Chart of Top Words")
fig, ax = plt.subplots(figsize=(8, 8))

dfAs.sort_values(by='Value').plot.barh(x='Word',
                      y='Value',
                      ax=ax,
                      color="purple")
st.pyplot()

st.header("Word Cloud ")

#Word Cloud 
dfAs_l=dfAs['Word'].str.cat(sep=' ')


wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = stopwords, 
                min_font_size = 10).generate(dfAs_l) 
                      
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
st.pyplot()

