#!/usr/bin/env python
# coding: utf-8

# In[2]:


import yfinance as yf
import pandas as pd
import requests
import json
import string
from datetime import datetime
import glob
import os
import twitter
import time


# In[3]:


print("Cron job is running...The time is: %s" % datetime.now())


# In[259]:


tickers = ["ZNGA","EA","ATVI","TTWO","U","MSFT","KYYWF",
           "TM17.L","EMBRAC-B.ST","SF.ST","PDX.ST","OTGLF",
           "UBI.PA","ALFOC.PA","3659.T","1337.HK",
           "3635.T","SQNXF","CCOEY","NTDOY","SGAMY","9766.T",
           "7832.T","BILI","NTES","TCEHY","SNE","NVDA","LOGI"]


# In[262]:


### renvoie le nom court de la boite
def shortname(name):
    retour = name.split(" ")[0]
    if len(name.split(" "))>1:
        retour = retour + " " + name.split(" ")[1]
    return retour

### Retourne les plus fortes hausses / baisses sur une plage de valeurs données
def highandlow(tableau,freq,decimal=0):
    myserie = (tableau.iloc[-1]['Close']-tableau.iloc[freq]['Close'])*100/tableau.iloc[freq]['Close']
    myserie.dropna(inplace=True)
    myserie.sort_values(ascending=True, inplace = True)
    lowestticker_longname = shortname(yf.Ticker(myserie.index[0]).info["longName"])
    highestticker_longname = shortname(yf.Ticker(myserie.index[-1]).info["longName"])
    retour = lowestticker_longname + " " + adplus(str(myserie[0].round(decimal))) + "%"
    retour += " | " + highestticker_longname + " " + adplus(str(myserie[-1].round(decimal))) + "%"
    return retour

### Retourne la variation de tout le portefeuille sur une plage de valeurs données
def globalvariation(tableau,freq,decimal=0):
    myserie = (tableau.iloc[-1]['Close']-tableau.iloc[freq]['Close'])*100/tableau.iloc[freq]['Close']
    myserie.dropna(inplace=True)
    retour = adplus(str(myserie.mean().round(decimal)))+"%"
    return retour

###ajoute un + pour les variations positives
def adplus(stringedchiffre):
    if str(stringedchiffre)[0].isdigit():
        stringedchiffre = "+" + stringedchiffre
    return stringedchiffre


# In[278]:


### VARIATION CLOSING VEILLE VS AVANT VEILLE
now = datetime.today()
lastyear = datetime(now.year,now.month,now.day-10)
data = yf.download(tickers, interval="1d", start=lastyear.strftime('%Y-%m-%d'), end=now.strftime('%Y-%m-%d'))
data.interpolate(method='pad', limit=2,inplace = True)

tweet = "Portfolio daily var: "+globalvariation(data,-3,2)
tweet += "\n"+"Low & Highest daily var: "+highandlow(data,-3,2)


# In[279]:


### Tweet daily variations
CONSUMER_KEY ="Jd2Rt0XLJQBb8Ey8T2ebfg89b"
CONSUMER_SECRET = "4E1dK6ASh18MNXtXkFGdfRdxQ1ecng2JIZqZNYJ580RbBGpCiE"   
ACCESS_KEY = "1339971934394740737-WfLi8kR4kgNKfrvNBe2sHthQwJFQwi"    
ACCESS_SECRET = "vQCz1wntjbJV8XWhPfAQ4DtNPAsmAt767dzVjunRclNdG"
api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_KEY,
                      access_token_secret=ACCESS_SECRET)
api.PostUpdate(tweet)
time.sleep(5)


# In[277]:


### VARIATION CLOSING MoM,QoQ,YoY EVERY FRIDAY
now = datetime.today()

if now.weekday()==4:
    lastyear = datetime(now.year-1,now.month,now.day)
    data = yf.download(tickers, interval="1wk", start=lastyear.strftime('%Y-%m-%d'), end=now.strftime('%Y-%m-%d'))
    data.interpolate(method='pad', limit=2,inplace = True)

    tweet = "Portfolio var"
    tweet += "\n"+"1m: "+globalvariation(data,-5,1)
    tweet += "\n"+"3m: "+globalvariation(data,-13,1)
    tweet += "\n"+"12m: "+globalvariation(data,-53,1)
    tweet += "\n"
    tweet += "\n"+"Low & Highest var"
    tweet += "\n"+"1m: "+highandlow(data,-5)
    tweet += "\n"+"3m: "+highandlow(data,-13)
    tweet += "\n"+"12m: "+highandlow(data,-53)
    
    api.PostUpdate(tweet)


# In[280]:


lastyear = datetime(now.year-1,now.month,now.day)
data = yf.download(tickers, interval="1wk", start=lastyear.strftime('%Y-%m-%d'), end=now.strftime('%Y-%m-%d'))
data.interpolate(method='pad', limit=2,inplace = True)

data.to_csv("check.csv")

