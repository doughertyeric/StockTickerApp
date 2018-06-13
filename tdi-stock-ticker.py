from __future__ import print_function
import sys
import os
import requests
import datetime
import pandas as pd
#from bokeh.io import output_notebook
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.tools import HoverTool
from bokeh.embed import components
from flask import Flask, request, render_template
from flask import session

app_tdi_stock_ticker = Flask(__name__)
api_key = api_key=os.environ.get('QUANDL_KEY')

@app_tdi_stock_ticker.route('/')
def pre_index():
    return render_template('index.html')

@app_tdi_stock_ticker.route('/index', methods=['GET', 'POST'])
def index_page():
    if request.method == 'GET':
        return render_template('index.html')
        
@app_tdi_stock_ticker.route('/output', methods=['GET', 'POST'])
def output_page(): 
    
    form_dict = {'ticker': request.form['TickerName'],
                 'date': request.form['EndDate'],
                 'period': request.form['Period'],
                 'metric': request.form['Metric']}

    curr_date, prev_date = get_dates(form_dict['date'], form_dict['period'])
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=' + str(form_dict['ticker']) + '&date.gte=' + str(prev_date) + '&date.lte=' + str(curr_date) + '&api_key=' + str(api_key)
    
    df, temp, temp2, new_idx = plot_components(url, curr_date, prev_date)
    plot = create_plot(df, temp, temp2, new_idx, form_dict['metric'])
    
    script, div = components(plot)
    return render_template('output.html', the_script=script, the_div=div)

##################################################################

def get_dates(new_date, window_button):
    curr_date = datetime.datetime.strptime(new_date, '%Y-%m-%d').date()
    if window_button == 'one_month':
        prev_date = curr_date - datetime.timedelta(days=30)
    elif window_button == 'six_months':
        prev_date = curr_date - datetime.timedelta(days=30.5*6)
    else:
        prev_date = curr_date - datetime.timedelta(days=365)
    return curr_date, prev_date

def plot_components(url, curr_date, prev_date):
    response = requests.get(url)
    meta_data = response.json()
    data = meta_data['datatable']
    data = data['data']
    df = pd.DataFrame(data)
    df.columns = ['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividend', 'Split_Ratio', 'Adj_Open', 'Adj_High', 'Adj_Low', 'Adj_Close', 'Adj_Volume']

    dates = pd.DataFrame(data).iloc[:,1]
    dates= pd.to_datetime(dates)
    temp = pd.DataFrame(data, index = dates)
    temp = temp.iloc[:,[1,5,2,4,3]]
    temp.columns = ['Date', 'Close', 'Open', 'Low', 'High']

    new_idx = pd.date_range(prev_date, curr_date, freq='D')
    temp2 = temp.reindex(new_idx)
    return df, temp, temp2, new_idx

def create_plot(df, temp, temp2, new_idx, metric):
    source = ColumnDataSource(
                data=dict(
                    Date=pd.to_datetime(df['Date']),
                    Open=df['Open'][:],
                    High=df['High'][:],
                    Low=df['Low'][:],
                    Close=df['Close'][:],))
    source2 = ColumnDataSource(
                data=dict(
                    Date=pd.to_datetime(new_idx),
                    Open=temp2['Open'][:],
                    High=temp2['High'][:],
                    Low=temp2['Low'][:],
                    Close=temp2['Close'][:],))
    
    if metric == 'range':
        x = pd.to_datetime(new_idx)
        y1 = temp2['Low'][:]
        y2 = temp2['High'][:]
        min_val = y1.min()
        max_val = y2.max()
        
        p = figure(width=800, height=500, x_axis_type='datetime',
                title=str(df['Ticker'][0]) + ' Intra-day Ranges between ' + \
                str(df['Date'][0]) + ' and ' + str(df['Date'][len(df)-1]))
        
        p.yaxis.axis_label = 'Price (USD)'
        p.xaxis.axis_label = 'Date'
        p.xaxis.major_label_orientation = 3.14159/4
        p.y_range = Range1d(min_val - (0.02*min_val), max_val + (0.02*min_val))
        
        cr = p.vbar(x, top=y2, bottom=y1, source=source2, width=(16*3600*1000), 
                    fill_color="#E08E79", hover_fill_color="#F2583E",
                    fill_alpha=0.8, hover_alpha=1,
                    line_color="white", hover_line_color = "black")
        p.add_tools(HoverTool(tooltips=[("High", "@High"), ("Low", "@Low")], renderers=[cr], mode='mouse'))
    elif metric == 'open':
        x1 = pd.to_datetime(temp['Date'])
        x2 = pd.to_datetime(new_idx)
        y1 = temp['Open'][:]
        y2 = temp2['Open'][:]
        
        p = figure(width=800, height=500, x_axis_type='datetime',
                title=str(df['Ticker'][0]) + ' Opening Prices between ' + \
                str(df['Date'][0]) + ' and ' + str(df['Date'][len(df)-1]))
        
        p.line(x1, y1, line_width=1, alpha=0.5, color='grey')
        p.line(x2, y2, line_width=3)
        p.yaxis.axis_label = 'Price (USD)'
        p.xaxis.axis_label = 'Date'
        p.xaxis.major_label_orientation = 3.14159/4

        cr = p.circle('Date', 'Open', source=source, size=20,
                    fill_color="grey", hover_fill_color="firebrick",
                    fill_alpha=0, hover_alpha=0.6,
                    line_color=None, hover_line_color=None)
        p.add_tools(HoverTool(tooltips=[("Price", "@Open")], renderers=[cr], mode='mouse'))
    else:
        x1 = pd.to_datetime(temp['Date'])
        x2 = pd.to_datetime(new_idx)
        y1 = temp['Close'][:]
        y2 = temp2['Close'][:]
        
        p = figure(width=800, height=500, x_axis_type='datetime',
                title=str(df['Ticker'][0]) + ' Closing Prices between ' + \
                str(df['Date'][0]) + ' and ' + str(df['Date'][len(df)-1]))
            
        p.line(x1, y1, line_width=1, alpha=0.5, color='grey')
        p.line(x2, y2, line_width=3)
        p.yaxis.axis_label = 'Price (USD)'
        p.xaxis.axis_label = 'Date'
        p.xaxis.major_label_orientation = 3.14159/4

        cr = p.circle('Date', 'Close', source=source, size=20,
                    fill_color="grey", hover_fill_color="firebrick",
                    fill_alpha=0, hover_alpha=0.6,
                    line_color=None, hover_line_color=None)
        p.add_tools(HoverTool(tooltips=[("Price", "@Close")], renderers=[cr], mode='mouse'))
        
    return p
    
if __name__ == '__main__':
    app_tdi_stock_ticker.secret_key = 'co8ryqw/oi~cg%wfk#jxycs*zg7lw48v0q$rc'
    port = int(os.environ.get('PORT', 5000))
    app_tdi_stock_ticker.run(host='0.0.0.0', port=port)
    #app_tdi_stock_ticker.run(debug=True)
