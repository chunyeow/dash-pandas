# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests
import base64
import json
import datetime
import time
import pandas as pd
import plotly.graph_objs as go
import dash_table
requests.packages.urllib3.disable_warnings()

import conf

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def get_data(limit, sort):
    try:
       headers = {'Accept':'application/json', 'Authorization': 'Bearer ' + conf.gw_token }
       url = conf.url + "/" + conf.projnum + "/data" + \
             "?limit=" + limit + "&sort=" + sort
       get_resp = requests.get(url, headers=headers, verify=False)
       if get_resp.status_code == 200:
          return get_resp
       else:
          return
    except requests.exceptions.ConnectionError:
       return

def generate_table_layout(df):
    return dash_table.DataTable(
       id='table',
       columns=[
          {'name': i, 'id': i, 'deletable': True} for i in df.columns
       ],
       data=df.to_dict('records'),
    )

def generate_trace(df, gtype, naming):
    trace = {'x': df.index, 'y': df.values, 'type': gtype, 'name': naming},
    return trace

def generate_layout(title, mode, category):
    if category == True:
    # make sure x-axis is category type instead of converting string to integer
       layout = go.Layout(title = title, hovermode = mode, xaxis=dict(type='category'))
    else:
       layout = go.Layout(title = title, hovermode = mode)
    return layout

def generate_trace_marker(df, naming):
    return go.Scatter(x = df.index, y = df.values,
                      mode='markers',
                      opacity=0.7,
                      marker={
                         'size': 15,
                         'line': {'width': 0.5, 'color': 'white'}
                      },
                      name = naming)

 
def serve_layout():
    res = get_data("12000", "qty desc")
    if res != None:
       docs = res.json()['docs']
       df = pd.read_json(json.dumps(docs), orient='columns')

       # Get statistic table to be displayed
       dft = df.describe(include='all')
       dft = dft.reset_index()

       # Popular Brand
       brand_count = df['brand'].value_counts()
       brand_count = brand_count[:10,]

       # Popular Item Code
       item_count = df['itemcode'].value_counts()
       item_count = item_count[:30,]

       # Common Number of Quantity Purchased
       qty_count = df[(df['qty'] < 10) & (df['Qty'] > 0)]['Qty'].value_counts()

       # Unit Price for Each Transaction    
       unitp_count1 = df['unitsoldprice'][df['brand'] == 'F006'].value_counts()
       unitp_count2 = df['unitsoldprice'][df['brand'] == 'P007'].value_counts()
       unitp_count3 = df['unitsoldprice'][df['brand'] == 'D006'].value_counts()
       unitp_count4 = df['unitsoldprice'][df['brand'] == 'P006'].value_counts()
       unitp_count5 = df['unitsoldprice'][df['brand'] == 'L010'].value_counts()
       
       itemc_count = df['itemcode'][(df['brand'] == 'F006') & (df['unitsoldprice'] == 10)].value_counts()
       itemc_count = itemc_count[:30,]

       # Net Sold Price for Each Transaction
       nets_count1 = df['netsoldprice'][df['brand'] == 'F006'].value_counts()
       nets_count2 = df['netsoldprice'][df['brand'] == 'P007'].value_counts()
       nets_count3 = df['netsoldprice'][df['brand'] == 'D006'].value_counts()
       nets_count4 = df['netsoldprice'][df['brand'] == 'P006'].value_counts()
       nets_count5 = df['netsoldprice'][df['brand'] == 'L010'].value_counts()

    fig1 = go.Figure(data = generate_trace(brand_count, "bar", "Brand"), layout = generate_layout("Top 10 Most Popular Brands", "closest", True))
    fig2 = go.Figure(data = generate_trace(item_count, "bar", "Item"), layout = generate_layout("Top 30 Most Popular Sale Items", "closest", True))
    fig3 = go.Figure(data = generate_trace(qty_count, "bar", "Quantity Purchased"), layout = generate_layout("Common Quantity Purchased for Each Transaction", "closest", True))
    fig4 = go.Figure(data = generate_trace(itemc_count, "bar", "Item Code Brand F006"), layout = generate_layout("Most Popular Item Code for Brand F006 with Unit Sold Price RM10.00", "closest", True))

    traceu1 = generate_trace_marker(unitp_count1, "F006")
    traceu2 = generate_trace_marker(unitp_count2, "P007")
    traceu3 = generate_trace_marker(unitp_count3, "D006")
    traceu4 = generate_trace_marker(unitp_count4, "P006")
    traceu5 = generate_trace_marker(unitp_count5, "L010") 
    layout1 = generate_layout("Occurrence of Unit Sold Price for Popular Brands", "closest", False)
    fig5 = go.Figure(data = [traceu1, traceu2, traceu3, traceu4, traceu5], layout = layout1)

    tracen1 = generate_trace_marker(nets_count1, "F006")
    tracen2 = generate_trace_marker(nets_count2, "P007")
    tracen3 = generate_trace_marker(nets_count3, "D006")
    tracen4 = generate_trace_marker(nets_count4, "P006")
    tracen5 = generate_trace_marker(nets_count5, "L010")
    layout2 = generate_layout("Occurrence of Net Sold Price for Popular Brands", "closest", False)
    fig6 = go.Figure(data = [tracen1, tracen2, tracen3, tracen4, tracen5], layout = layout2)

    return html.Div(
                    [html.Div([
                               html.Div([dcc.Graph(id='plot1', figure=fig1)]),
                               html.Div([dcc.Graph(id='plot2', figure=fig2)]),
                               html.Div([dcc.Graph(id='plot3', figure=fig3)]),
                               html.Div([dcc.Graph(id='plot5', figure=fig5)]),
                               html.Div([dcc.Graph(id='plot4', figure=fig4)]),
                               html.Div([dcc.Graph(id='plot6', figure=fig6)]),
                               html.Div(children = [html.H5('Statistics for Sales'), generate_table_layout(dft)], style = {'textAlign': 'center'}),
                              ], className="row")
                    ]
                   )

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = serve_layout

if __name__ == '__main__':
   app.run_server(debug=True, port=8051)
