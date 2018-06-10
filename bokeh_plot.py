from __future__ import print_function
import sys
import os
import requests
import datetime
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput
from bokeh.models.tools import HoverTool
from bokeh.plotting import figure
from bokeh.embed import components

# Set up data
api_key = 'gw2NbPXKQYZkf46yfNQS'
url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=GOOG&date.gte=2016-01-02&date.lte=2016-02-03&api_key=' + str(api_key)

    response = requests.get(url)
    meta_data = response.json()
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

    new_idx = pd.date_range(prev_month, curr_date, freq='D')
    temp2 = temp.reindex(new_idx)
 
source = ColumnDataSource(
                data=dict(
                    x1=pd.to_datetime(temp['Date']),
                    x2 = pd.to_datetime(new_idx),
                    y1 = temp['Close'][:],
                    y2 = temp2['Close'][:]))
 
# Set up plot    
p = figure(width=800, height=500, x_axis_type='datetime',
            title=str(df['Ticker'][0]) + ' Closing Prices between ' + \
            str(df['Date'][0]) + ' and ' + str(df['Date'][len(df)-1]))

p.line('x1', 'y1', source=source, line_width=1, alpha=0.5, color='grey')
p.line('x2', 'y2', source=source, line_width=3)
p.yaxis.axis_label = 'Price (USD)'
p.xaxis.axis_label = 'Date'
p.xaxis.major_label_orientation = 3.14159/4

cr = p.circle('Date', 'Close', source=source, size=20,
            fill_color="grey", hover_fill_color="firebrick",
            fill_alpha=0, hover_alpha=0.6,
            line_color=None, hover_line_color=None)
p.add_tools(HoverTool(tooltips=[("Price", "@Close")], renderers=[cr], mode='vline'))

# Set up widgets
ticker_text = TextInput(title="TickerName", value='GOOG')
date_text = TextInput(title="StartDate", value='2016-02-03')
 
# Set up callbacks
def update_data(attrname, old, new):
 
    # Get the current values
    new_ticker = ticker_text.value
    new_date = date_text.value
    curr_date = datetime.datetime.strptime(new_date, '%Y-%m-%d').date()
    prev_month = curr_date - datetime.timedelta(days=30)
 
    # Scrape new dataset
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=' + str(new_ticker) + '&date.gte=' + str(prev_month) + '&date.lte=' + str(curr_date) + '&api_key=' + str(api_key)
    #print(url, sys.stderr)
            
    response = requests.get(url)
    meta_data = response.json()
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

    new_idx = pd.date_range(prev_month, curr_date, freq='D')
    temp2 = temp.reindex(new_idx)
 
    source.data = dict(x1=pd.to_datetime(temp['Date']),
                    x2 = pd.to_datetime(new_idx),
                    y1 = temp['Close'][:],
                    y2 = temp2['Close'][:])
 
for w in [ticker_text, date_text]:
    w.on_change('value', update_data)
 
# Set up layouts and add to document
inputs = widgetbox(ticker_text, date_text)
 
curdoc().add_root(row(inputs, p, width=800))
curdoc().title = "Closing Prices"