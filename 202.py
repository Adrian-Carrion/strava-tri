# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 01:07:07 2023

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

config={
    'displayModeBar': True,
    'displaylogo': False,                                       
    'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
    'responsive' : True
  }

external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

df = getAll('strava')

df['stat_distance'] = df['stat_distance'].str.replace(' km','').str.replace(' m','').astype(float)
df_count = df.groupby(['type','athlete_name'])['stat_distance'].sum().reset_index(name='Distancia').sort_values('Distancia')

fig_swim = px.bar(df_count.query("type=='Swim'").sort_values(by='Distancia', ascending=False).head(10),
             x="Distancia", 
             y="athlete_name",
             orientation='h',
             hover_data=["Distancia"],
             height=400,
             title='Pececito de la semana',
             labels={'athlete_name':'Triatleta'})
fig_swim.update_layout(yaxis={'categoryorder':'total ascending'})



fig_run = px.bar(df_count.query("type=='Ride' or type=='VirtualRide'").sort_values(by='Distancia', ascending=False).head(10),
             x="Distancia", 
             y="athlete_name",
             orientation='h',
             hover_data=["Distancia"],
             height=400,
             title='Correcaminos de la semana',
             labels={'athlete_name':'Triatleta'})
fig_run.update_layout(yaxis={'categoryorder':'total ascending'})

fig_ride = px.bar(df_count.query("type=='Run' or type=='TrailRun' or type=='MountainBikeRide'").sort_values(by='Distancia', ascending=False).head(10),
             x="Distancia", 
             y="athlete_name",
             orientation='h',
             hover_data=["Distancia"],
             height=400,
             title='Pedalines de la semana',
             labels={'athlete_name':'Triatleta'})
fig_run.update_layout(yaxis={'categoryorder':'total ascending'})

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([dcc.Graph(id='swim-graph', figure=fig_swim)], width=4),
        dbc.Col([dcc.Graph(id='ride-graph', figure=fig_ride)], width=4),
        dbc.Col([dcc.Graph(id='run-graph', figure=fig_run)], width=4),
        ]),
    ], fluid=True)
             

if __name__ == '__main__':
    app.run(debug=True, port=3004)