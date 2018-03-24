from flask import Flask,render_template,request,redirect
import datetime
import requests
import json
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file,save
app = Flask(__name__)

def closing_price(ticker,recorded_date):
    start_date = (datetime.datetime.strptime(recorded_date, '%Y-%m-%d') + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d') + datetime.timedelta(days=-29)).strftime('%Y-%m-%d')

    payload  = {'ticker':ticker,'date.gte':'2018-02-01','date.lte':start_date,'date.gte':end_date,
            'qopts.columns':'date,close','api_key':'ziajBSoqxbaJFebtsPPy'}
    r = requests.get('https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json', params = payload)
    json_data = r.json()

    share_data = pd.DataFrame(json_data['datatable']['data'],columns=['date','closingCost'])
    return share_data

def date_time(x):
    return np.array(x, dtype=np.datetime64)

def output_data(share_data,ticker):
    p = figure(x_axis_type="datetime", title="%s Stock Closing Prices" %[ticker])
    p.grid.grid_line_alpha=0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.line(date_time(share_data.date), share_data.closingCost, color='DarkBlue', legend=ticker)
    p.legend.location = "top_left"
    output_file("./templates/graph.html", title="closing cost plot") 
    save(p)

app.vars={}

@app.route('/index',methods=['GET','POST'])
def index(): 
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # request was a POST
        app.vars['ticker'] = request.form['ticker'] # get ticker
	recorded_date = (datetime.datetime.now().strftime('%Y-%m-%d')) # record the date of input
	share_data = closing_price(app.vars['ticker'],recorded_date) # get closing price for that ticker
        output_data(share_data,app.vars['ticker']) # create html plot using bokeh
        return redirect('/graph') # call that page

@app.route('/graph')
def graph():
    return render_template('graph.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
