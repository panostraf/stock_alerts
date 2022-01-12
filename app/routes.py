from flask import Flask
from flask import render_template,request,session,url_for,jsonify
import investpy as inv
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
    fig,last,std,last_trend,dfjson  = ptrends.main(str(symbol))

    graphJSON =  json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # #print(graphJSON)
    # fig.write_image("static/imgs/fig1.jpeg")
    symbols = inv.crypto.get_cryptos()[:10]

    datajson = dfjson[['Date','Close']].to_json(orient="records")
    # print(dfjson.to_dict('columns'))

    return render_template("results.html",
                                symbol=symbol,
                                nlines=nlines,
                                ncomponents=ncomponents,
                                minangle=minangle,
                                last = last,
                                graphJSON=graphJSON,
                                std=std,
                                last_trend=last_trend,
                                datajson = datajson
                                )


@app.route("/resultsParams",methods=["GET","POST"])
def trendParams():
    if request.method=="POST":
        minangle = request.form['min_angle']
        ncomponents = request.form['ncomponents']
        nlines = request.form['nlines']
        
        try:
            nlines = int(nlines)
            #print(nlines)
        except ValueError:
            #print("error")
            nlines = 20
            # session.pop('nlines')
        
        try:
            ncomponents = int(ncomponents)
            #print(ncomponents)
        except ValueError:
            #print("error")
            ncomponents = 4
            # session.pop('ncomponents')

        try:
            minangle = float(minangle)
            #print(minangle)
        except ValueError:
            #print("error")
            minangle = 0.005
            # session.pop('min_angle')
            


        # ncomponents = int(ncomponents)
        # minangle = float(minangle)
        #print("\n\n\n\n")
        #print("nlines",nlines,"type",type(nlines))

        fig, last = trends.main(str(session['symbol']),maxnLines=nlines,n=ncomponents,minAngle=minangle)
        graphJSON =  json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        #print(minangle,nlines,ncomponents)
        # fig.write_image("static/imgs/fig1.jpeg")
        fig.config()
        symbols = inv.crypto.get_cryptos()[:10]
    return render_template("results.html",
                            symbol=session['symbol'],
                            nlines=nlines,
                            ncomponents=ncomponents,
                            minangle=minangle,
                            last = last,
                            graphJSON=graphJSON,
                            symbols=symbols["name"])


if __name__=='__main__':
    app.run(debug=True,host="0.0.0.0",port="8080") 