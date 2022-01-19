from flask import Flask
from flask import render_template,request,session,url_for,jsonify
import investpy as inv
from matplotlib import lines
from werkzeug import datastructures
from app.trendlines  import *
from app.trendlines import PlotLines as ptrends
# from app.import trendlines.trends
from app.trendlines import trends
import pandas as pd
import json
import plotly
import plotly.express as px
from app import app
from collections import defaultdict
import numpy as np



@app.route('/', methods =["GET", "POST"])
def home():
    symbols2=['bitcoin',"XRP"]
    symbols = inv.crypto.get_cryptos()[:100]
    
    # print(symbols["name"])
    for s in symbols["name"]:
        print(s)

    return render_template("index.html",
                            symbols=symbols["name"])





@app.route("/results/<symbol>",methods=["GET","POST"])
def results(symbol):
    
    nlines = 20
    ncomponents = 4
    minangle = 0.005
    last,std,last_trend,dfjson ,uptrends,downtrends = ptrends.main(str(symbol))
    datajson = dfjson[['Date','Close']].to_dict(orient='list')

    return render_template("results.html",
                                symbol=symbol,
                                nlines=nlines,
                                ncomponents=ncomponents,
                                minangle=minangle,
                                last = last,
                                std=std,
                                last_trend=last_trend,
                                datajson = datajson,
                                linesXmin=uptrends,
                                linesXmax=downtrends)



