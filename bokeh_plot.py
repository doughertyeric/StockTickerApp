from __future__ import print_function
import sys
import os
import requests
import datetime
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import TextInput, RadioButtonGroup
from bokeh.models.tools import HoverTool
from bokeh.plotting import figure
from bokeh.embed import components

# Set up data
api_key = 'gw2NbPXKQYZkf46yfNQS'
url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=GOOG&date.gte=2016-01-04&date.lte=2016-02-03&api_key=' + str(api_key)

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

curr_date = curr_date = datetime.datetime(2016, 2, 3).date()
prev_month = curr_date - datetime.timedelta(days=30)
new_idx = pd.date_range(prev_month, curr_date, freq='D')
temp2 = temp.reindex(new_idx)
 
source = ColumnDataSource(
            data=dict(
                x1=pd.to_datetime(temp['Date']),
                y1 = temp['Close'][:]))
source2 = ColumnDataSource(
            data=dict(
                x2 = pd.to_datetime(new_idx),
                y2 = temp2['Close'][:]))
 
# Set up plot    
p = figure(width=800, height=500, x_axis_type='datetime',
            title=str(df['Ticker'][0]) + ' Closing Prices between ' + \
            str(df['Date'][0]) + ' and ' + str(df['Date'][len(df)-1]))

p.line('x1', 'y1', source=source, line_width=1, alpha=0.5, color='grey')
p.line('x2', 'y2', source=source2, line_width=3)
p.yaxis.axis_label = 'Price (USD)'
p.xaxis.axis_label = 'Date'
p.xaxis.major_label_orientation = 3.14159/4

cr = p.circle('x1', 'y1', source=source, size=20,
            fill_color="grey", hover_fill_color="firebrick",
            fill_alpha=0, hover_alpha=0.6,
            line_color=None, hover_line_color=None)
p.add_tools(HoverTool(tooltips=[("Price", "@y1")], renderers=[cr], mode="mouse"))

# Set up widgets
ticker_text = TextInput(title="Ticker Symbol", value='GOOG')
date_text = TextInput(title="End Date", value='2016-02-03')
temporal_button = RadioButtonGroup(labels=["1 Month", "6 Months", "1 Year"], active=0)

def get_dates(new_date, active_button):
    curr_date = datetime.datetime.strptime(new_date, '%Y-%m-%d').date()
    if active_button == 0:
        prev_date = curr_date - datetime.timedelta(days=30)
    elif active_button == 1:
        prev_date = curr_date - datetime.timedelta(days=30.5*6)
    else:
        prev_date = curr_date - datetime.timedelta(days=365)
    return curr_date, prev_date
    

def update_title_ticker(attrname, old, new):
    curr_date, prev_date = get_dates(date_text.value, temporal_button.active)
    p.title.text = str(ticker_text.value) + ' Closing Prices between ' + \
            str(prev_date) + ' and ' + str(curr_date)
 
ticker_text.on_change('value', update_title_ticker)

def update_title_date(attrname, old, new):
    curr_date, prev_date = get_dates(date_text.value, temporal_button.active)
    p.title.text = str(ticker_text.value) + ' Closing Prices between ' + \
            str(prev_date) + ' and ' + str(curr_date)
 
date_text.on_change('value', update_title_date)

def update_title_button(attrname, old, new):
    curr_date, prev_date = get_dates(date_text.value, temporal_button.active)
    p.title.text = str(ticker_text.value) + ' Closing Prices between ' + \
            str(prev_date) + ' and ' + str(curr_date)
 
temporal_button.on_change('active', update_title_button)
 
# Set up callbacks
def update_data(attrname, old, new):
 
    # Get the current values
    new_ticker = ticker_text.value
    curr_date, prev_date = get_dates(date_text.value, temporal_button.active)
 
    # Scrape new dataset
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=' + str(new_ticker) + '&date.gte=' + str(prev_date) + '&date.lte=' + str(curr_date) + '&api_key=' + str(api_key)
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

    new_idx = pd.date_range(prev_date, curr_date, freq='D')
    temp2 = temp.reindex(new_idx)
 
    source.data = dict(x1=pd.to_datetime(temp['Date']),
                        y1 = temp['Close'][:])
    source2.data = dict(x2 = pd.to_datetime(new_idx),
                        y2 = temp2['Close'][:])
 
for w in [ticker_text, date_text]:
    w.on_change('value', update_data)
    
temporal_button.on_change('active', update_data)
 
# Set up layouts and add to document
inputs = widgetbox(ticker_text, date_text, temporal_button)
 
curdoc().add_root(row(inputs, p, width=800))
curdoc().title = "Closing Prices"