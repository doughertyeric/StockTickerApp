from __future__ import print_function
import sys
import os
import requests
import datetime
import pandas as pd
#from bokeh.io import output_notebook
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.embed import components
from flask import Flask, request, render_template
from flask import session

app_tdi_stock_ticker = Flask(__name__)
api_key = 'gw2NbPXKQYZkf46yfNQS'

@app_tdi_stock_ticker.route('/')
def pre_index():
    return render_template('index.html')

@app_tdi_stock_ticker.route('/index', methods=['GET', 'POST'])
def index_page():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        curr_date, prev_date = get_dates(request.form['StartDate'])

        url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=' + str(request.form['TickerName']) + '&date.gte=' + str(prev_date) + '&date.lte=' + str(curr_date) + '&api_key=' + str(api_key)
        
        df, temp, temp2, new_idx = plot_components(url)
        plot = create_plot(df, temp, temp2, new_idx)
    
        script, div = components(plot)
        return render_template('output.html', the_script=script, the_div=div)
        
@app_tdi_stock_ticker.route('/output', methods=['GET', 'POST'])
def output_page(): 

    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=' + str(request.form['TickerName']) + '&date.gte=' + str(prev_date) + '&date.lte=' + str(curr_date) + '&api_key=' + str(api_key)
    
    df, temp, temp2, new_idx = plot_components(url)
    plot = create_plot(df, temp, temp2, new_idx)
    
    script, div = components(plot)
    return render_template('output.html', the_script=script, the_div=div)

def get_dates(new_date):
    curr_date = datetime.datetime.strptime(new_date, '%Y-%m-%d').date()
    prev_date = curr_date - datetime.timedelta(days=30)
    return curr_date, prev_date

def plot_components(url):
    response = requests.get(url)
    meta_data = response.json()
    data = meta_data['datatable']
    data = data['data']
    df = pd.DataFrame(data)
    df.columns = ['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividend', 'Split_Ratio', 'Adj_Open', 'Adj_High', 'Adj_Low', 'Adj_Close', 'Adj_Volume']

    dates = pd.DataFrame(data).iloc[:,1]
    dates= pd.to_datetime(dates)
    temp = pd.DataFrame(data, index = dates)
    temp = temp.iloc[:,[1,5]]
    temp.columns = ['Date', 'Close']

    new_idx = pd.date_range(prev_date, curr_date, freq='D')
    temp2 = temp.reindex(new_idx)
    return df, temp, temp2, new_idx
        

def create_plot(df, temp, temp2, new_idx):
    source = ColumnDataSource(
                data=dict(
                    Date=pd.to_datetime(df['Date']),
                    Open=df['Open'][:],
                    High=df['High'][:],
                    Low=df['Low'][:],
                    Close=df['Close'][:],))
    
    p = figure(width=800, height=500, x_axis_type='datetime',
                title=str(df['Ticker'][0]) + ' Closing Prices between ' + \
                str(df['Date'][0]) + ' and ' + str(df['Date'][len(df)-1]))

    x1 = pd.to_datetime(temp['Date'])
    x2 = pd.to_datetime(new_idx)
    y1 = temp['Close'][:]
    y2 = temp2['Close'][:]
    p.line(x1, y1, line_width=1, alpha=0.5, color='grey')
    p.line(x2, y2, line_width=3)
    p.yaxis.axis_label = 'Price (USD)'
    p.xaxis.axis_label = 'Date'
    p.xaxis.major_label_orientation = 3.14159/4

    cr = p.circle('Date', 'Close', source=source, size=20,
                fill_color="grey", hover_fill_color="firebrick",
                fill_alpha=0, hover_alpha=0.6,
                line_color=None, hover_line_color=None)
    p.add_tools(HoverTool(tooltips=[("Price", "@Close")], renderers=[cr], mode='vline'))
    return p
    
if __name__ == '__main__':
    app_tdi_stock_ticker.secret_key = 'co8ryqw/oi~cg%wfk#jxycs*zg7lw48v0q$rc'
    port = int(os.environ.get('PORT', 5000))
    app_tdi_stock_ticker.run(host='0.0.0.0', port=port)
    #app_tdi_stock_ticker.run(debug=True)
