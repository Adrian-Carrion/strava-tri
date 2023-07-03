# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:40:40 2023

@author: a.a.carrion.almagro
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 23:06:36 2023

@author: a.a.carrion.almagro
"""

from dash import Dash, html, dash_table, dcc
import plotly.express as px
import pandas as pd
from sql import createDB, initConn, getAll, emptyDB, insertJson
import dash_bootstrap_components as dbc
from datetime import date, timedelta, datetime
import plotly.graph_objects as go
import json
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")

today = datetime.now()
first_day =  today.today() + timedelta(days = - today.weekday())
first_day = datetime.combine(first_day.today(), datetime.min.time())

def calcTriPuntos(row):
    if row['type'] == 'Run' or row['type'] == 'TrailRun':
        p = 2*row['stat_distance']
    elif row['type'] == 'Swim':
        p = 4*row['stat_distance']/1000
    else:
        p = row['stat_distance']
    return p

config={
    'displayModeBar': False,
    'displaylogo': False,                                       
    'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
    'responsive' : True
  }

with open('mapping_names.json', encoding='utf-8') as json_file:
    M = json.load(json_file)


df = getAll('strava')
df['athlete_name'] = df['athlete_name'].map(M)
df['activity_date_dt'] = pd.to_datetime(df['activity_date_epoc'], unit='s')
df = df[df['activity_date_dt'] >= first_day]
df['stat_distance'] = df['stat_distance'].str.replace(' km','').str.replace(' m','').astype(float)
df_count = df.groupby(['type','athlete_name'])['stat_distance'].sum().reset_index(name='Distancia').sort_values('Distancia')
df['tri_puntos'] = df.apply(calcTriPuntos, axis=1)
df_tri_puntos = df.groupby(['type','athlete_name'])['tri_puntos'].sum().reset_index(name='TriPuntos').sort_values('TriPuntos')

df_swim = df_count.query("type=='Swim'").sort_values(by='Distancia', ascending=False)

fig = go.Figure()
fig.add_trace(go.Indicator(
    mode = "number",
    value = 300,
    number={'font_color':'red'},
    domain = {'row': 0, 'column': 0}))

fig.add_trace(go.Indicator(
    mode = "number",
    value = 500,
    domain = {'row': 0, 'column': 1}))

fig.add_trace(go.Indicator(
    mode = "number",
    value = 700,
    domain = {'row': 0, 'column': 2}))
fig.update_layout(
    grid = {'rows': 2, 'columns': 2, 'pattern': "independent"})

fig_swim = px.bar(df_swim.head(20),
             x="Distancia",
             y="athlete_name",
             orientation='h',
             hover_data=["Distancia"],
             height=400,
             title='🏊‍♀️🏊Pececito de la semana',
             text='Distancia',
             labels={'athlete_name':'Triatleta'})
fig_swim.update_traces(width=len(df_swim)/10, marker_color='#1381f4')
fig_swim.update_layout(yaxis={'categoryorder':'total ascending', 'fixedrange':True})
fig_swim.update_layout(xaxis={'categoryorder':'total ascending','gridcolor':'LightGrey', 'fixedrange':True})
fig_swim.layout.xaxis.fixedrange = True
fig_swim.layout.yaxis.fixedrange = True
fig_swim.update_layout({
'plot_bgcolor': 'rgb(255, 255, 255)',
'paper_bgcolor': 'rgb(255, 255, 255)',
})

df_run = df_count.query("type=='Run' or type=='TrailRun' or type=='MountainBikeRide'").sort_values(by='Distancia', ascending=False)
fig_run = px.bar(df_run.head(20),
             x="Distancia", 
             y="athlete_name",
             orientation='h',
             hover_data=["Distancia"],
             height=400,
             title='🏃‍♂️🏃‍♀️Correcaminos de la semana',
             text='Distancia',
             labels={'athlete_name':'Triatleta'})
fig_run.update_traces(width=len(df_run)/10, marker_color='#ffa500')
fig_run.update_layout(yaxis={'categoryorder':'total ascending', 'fixedrange':True})
fig_run.update_layout(xaxis={'categoryorder':'total ascending','gridcolor':'LightGrey', 'fixedrange':True})
fig_run.update_layout({
'plot_bgcolor': 'rgb(255, 255, 255)',
'paper_bgcolor': 'rgb(255, 255, 255)',
})


df_ride = df_count.query("type=='Ride' or type=='VirtualRide'").sort_values(by='Distancia', ascending=False)
fig_ride = px.bar(df_ride.head(20),
             x="Distancia", 
             y="athlete_name",
             orientation='h',
             hover_data=["Distancia"],
             height=400,
             title='🚴‍♂️🚴‍♀️Pedalines de la semana',
             text='Distancia',
             labels={'athlete_name':'Triatleta'})
fig_ride.update_traces(width=len(df_ride)/10, marker_color='#10882f')
fig_ride.update_layout(yaxis={'categoryorder':'total ascending', 'fixedrange':True})
fig_ride.update_layout(xaxis={'categoryorder':'total ascending','gridcolor':'LightGrey', 'fixedrange':True})
fig_ride.update_layout({
'plot_bgcolor': 'rgb(255, 255, 255)',
'paper_bgcolor': 'rgb(255, 255, 255)',
})


df_tripuntos = df_count.query("type=='TriPuntos'").sort_values(by='Distancia', ascending=False)
fig_tripuntos = px.bar(df_tri_puntos.head(20),
             x="TriPuntos",
             y="athlete_name",
             color="type",
             color_discrete_sequence =['#1381f4','#ffa500','#10882f'],
             orientation='h',
             hover_data=["TriPuntos"],
             height=400,
             title='TriPuntos🏊‍♀️🚴‍♀️🏃‍♂️',
             text='TriPuntos',
             labels={'athlete_name':'Triatleta'})
fig_tripuntos.update_layout(xaxis={'categoryorder':'total ascending','gridcolor':'LightGrey', 'fixedrange':True})
fig_tripuntos.update_layout(yaxis={'categoryorder':'total ascending', 'fixedrange':True})
fig_tripuntos.update_layout({
'plot_bgcolor': 'rgb(255, 255, 255)',
'paper_bgcolor': 'rgb(255, 255, 255)',
})

# app.layout = html.Div([
#         html.Div(children=[
#         dcc.Graph(
#             id='sv-graph',
#             figure=fig,
#             config=config
#             )]),
#         html.Div(children=[
#         dcc.Graph(
#             id='tripoints-graph',
#             figure=fig_tripuntos,
#             config=config
#             )]),
#         html.Div(children=[
#         dcc.Graph(
#             id='swim-graph',
#             figure=fig_swim,
#             config=config,
#             style={'width' : '33%'}
#             ),
#         dcc.Graph(
#             id='ride-graph',
#             figure=fig_ride,
#             config=config,
#             style={'width' : '33%'}
#         ),
#         dcc.Graph(
#             id='run-graph',
#             figure=fig_run,
#             config=config,
#             style={'width' : '33%'}
#         )
#     ], style={'display': 'flex', 'flex-direction': 'row'})
#         ])


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

header = html.H4(
    "Los números del Club", className="text-white p-4 mb-2 text-center"
)


graph_tripuntos = html.Div(dcc.Graph(id='tripoints-graph',figure=fig_tripuntos,config=config), className="m-3")
graph_swim = dcc.Graph(id='swim-graph',figure=fig_swim,config=config)
graph_ride = dcc.Graph(id='ride-graph',figure=fig_ride,config=config)
graph_run = dcc.Graph(id='run-graph',figure=fig_run,config=config)
app.layout = dbc.Container(
    [
        header,
        dbc.Row(
            [dbc.Col([graph_tripuntos],width=12)]
        ),
        dbc.Row(
            [dbc.Col([graph_swim], width=12, md=4),
            dbc.Col([graph_ride], width=12, md=4),
            dbc.Col([graph_run], width=12, md=4)
            ])
    ],
    className="dbc",
    fluid=True,
    style={'background-color': '#f3f4f6'}
)

if __name__ == '__main__':
    app.run(debug=True, port=3004)