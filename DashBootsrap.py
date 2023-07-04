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
import dash
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")
app = Dash(__name__, title="TriDashboard", external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

def serve_layout():
    
    def calcTriPuntos(row):
        if row['type'] == 'Run' or row['type'] == 'TrailRun':
            p = 2*row['stat_distance']
        elif row['type'] == 'Swim':
            p = 4*row['stat_distance']/1000
        else:
            p = row['stat_distance']
        return p
    
    today = datetime.now()
    first_day =  today.today() + timedelta(days = - today.weekday())
    first_day = datetime.combine(first_day, datetime.min.time())
    config={
        'displayModeBar': False,
        'staticPlot': True,
        'displaylogo': False,                                       
        'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
        'responsive' : True
      }
    
    with open('mapping_names.json', encoding='utf-8') as json_file:
        M = json.load(json_file)
    
    
    df = getAll('strava')
    df['type'] = df['type'].replace(['VirtualRide','MountainBikeRide','TrailRun'],['Ride','Ride','Run'])
    df['athlete_name'] = df['athlete_name'].map(M)
    df['activity_date_dt'] = pd.to_datetime(df['activity_date_epoc'], unit='s')
    df = df[df['activity_date_dt'] >= first_day]
    df['stat_distance'] = df['stat_distance'].str.replace(' km','').str.replace(' m','').astype(float)
    df_count = df.groupby(['type','athlete_name'])['stat_distance'].sum().reset_index(name='Distancia').sort_values('Distancia')
    df['tri_puntos'] = df.apply(calcTriPuntos, axis=1)
    df_tri_puntos = df.groupby(['type','athlete_name'])['tri_puntos'].sum().reset_index(name='TriPuntos')
    
    df_swim = df_count.query("type=='Swim'").sort_values(by='Distancia', ascending=False)
    
    total_swim = df_count.query("type=='Swim'")['Distancia'].sum()
    total_ride = df_count.query("type=='Ride'")['Distancia'].sum()
    total_run = df_count.query("type=='Run'")['Distancia'].sum()
    
    
    # =============================================================================
    # Create header and titles
    # =============================================================================
    header = html.H1("Los números del Club", className="text-center bg-light border m-4 p-4")
    
    title_totals = html.Div([
        html.H2(
            "Totales", className="text-center m-4 bg-light border p-4", id='tooltip-target'
            ),
        dbc.Tooltip(
               "Suma de todas las distancias desde el 01/07/2023",
               target="tooltip-target",
               placement='bottom'
           )
        ])
    
    title_tripoints =  html.H2(
        "Tripuntos: 🏊‍♀️ Nadar x4 - 🏃‍♂️ Correr x2 - 🚴‍♀️ Bici x1", className="text-center m-4 p-4 bg-light border"
    )
    
    logo = html.Img(src=app.get_asset_url('logo_color.jpg'),style={'width':'100%'},  className="float-end m-4")
    # header_logo = html.Div([header, logo], className='d-flex justify-content-evenly')
    
    title_sports=  html.H2(
        "Ranking semanal por deporte", className="text-center m-4 bg-light border p-4"
    )
    
    # =============================================================================
    # Create single values
    # =============================================================================
    fig_sv_swim = go.Figure()
    fig_sv_ride = go.Figure()
    fig_sv_run = go.Figure()
    
    fig_sv_swim.add_trace(go.Indicator(
        mode = "number",
        value = total_swim,
        title = {"text": "Natación"},
        number = {"font_color" : "#1381f4", "valueformat": "f", "suffix":" m"},
        domain = {'row': 0, 'column': 0}))
    fig_sv_swim.layout.height = 250

    fig_sv_ride.add_trace(go.Indicator(
        mode = "number",
        value = total_ride,
        title = {"text": "Ciclismo"},
        number={'font_color':'#10882f',  "valueformat": "f", "suffix":" Km"},
        domain = {'row': 0, 'column': 0}))
    fig_sv_ride.layout.height = 250
    
    fig_sv_run.add_trace(go.Indicator(
        mode = "number",
        value = total_run,
        title = {"text": "Carrera"},
        number={'font_color':'#ffa500',  "valueformat": "f", "suffix":" Km"},
    
        domain = {'row': 0, 'column': 0}))
    fig_sv_run.layout.height = 250
    
    
    fig_swim = px.bar(df_swim.head(15),
                 x="Distancia",
                 y="athlete_name",
                 orientation='h',
                 hover_data=["Distancia"],
                 height=500,
                 text_auto='.2f',
                 title='🏊‍♀️🏊Pececito de la semana',
                 text='Distancia',
                 labels={'athlete_name':'Triatleta'})
    fig_swim.update_traces(width=len(df_swim)/15, marker_color='#1381f4')
    fig_swim.update_layout(yaxis={'categoryorder':'total ascending', 'fixedrange':True})
    fig_swim.update_layout(xaxis={'categoryorder':'total ascending','gridcolor':'LightGrey', 'fixedrange':True})
    fig_swim.layout.xaxis.fixedrange = True
    fig_swim.layout.yaxis.fixedrange = True
    fig_swim.update_layout({
    'plot_bgcolor': 'rgb(255, 255, 255)',
    'paper_bgcolor': 'rgb(255, 255, 255)',
    })
    
    
    # =============================================================================
    # Create sports rankings
    # =============================================================================
    df_run = df_count.query("type=='Run'").sort_values(by='Distancia', ascending=False)
    fig_run = px.bar(df_run.head(15),
                 x="Distancia", 
                 y="athlete_name",
                 orientation='h',
                 hover_data=["Distancia"],
                 height=500,
                 text_auto='.2f',
                 title='🏃‍♂️🏃‍♀️Correcaminos de la semana',
                 text='Distancia',
                 labels={'athlete_name':'Triatleta'})
    fig_run.update_traces(width=len(df_run)/15, marker_color='#ffa500')
    fig_run.update_layout(yaxis={'categoryorder':'total ascending', 'fixedrange':True})
    fig_run.update_layout(xaxis={'categoryorder':'total ascending','gridcolor':'LightGrey', 'fixedrange':True})
    fig_run.update_layout({
    'plot_bgcolor': 'rgb(255, 255, 255)',
    'paper_bgcolor': 'rgb(255, 255, 255)',
    })
    
    
    df_ride = df_count.query("type=='Ride'").sort_values(by='Distancia')
    fig_ride = px.bar(df_ride.head(15),
                 x="Distancia", 
                 y="athlete_name",
                 orientation='h',
                 hover_data=["Distancia"],
                 height=500,
                 text_auto='.2f',
                 title='🚴‍♂️🚴‍♀️Pedalines de la semana',
                 text='Distancia',
                 labels={'athlete_name':'Triatleta'})
    fig_ride.update_traces(width=len(df_ride)/15, marker_color='#10882f')
    fig_ride.update_layout(yaxis={'categoryorder':'total ascending', 'fixedrange':True})
    fig_ride.update_layout(xaxis={'categoryorder':'total ascending','gridcolor':'LightGrey', 'fixedrange':True})
    fig_ride.update_layout({
    'plot_bgcolor': 'rgb(255, 255, 255)',
    'paper_bgcolor': 'rgb(255, 255, 255)',
    })
    
    # =============================================================================
    # Create fig tripuntos
    # =============================================================================
    
    fig_tripuntos = px.bar(df_tri_puntos,
                 x="TriPuntos",
                 y="athlete_name",
                 color="type",
                 color_discrete_sequence =['#10882f','#ffa500','#1381f4'],
                 orientation='h',
                 text_auto='.2f',
                 hover_data=["TriPuntos"],
                 height=len(df_tri_puntos)*22,
                 title='🏊‍♀️🚴‍♀️🏃‍♂️ TriPuntos de la semana',
                 text='TriPuntos',
                 labels={'athlete_name':'Triatleta'})
    fig_tripuntos.update_layout(xaxis={'categoryorder':'total ascending','gridcolor':'LightGrey', 'fixedrange':True})
    fig_tripuntos.update_layout(yaxis={'categoryorder':'total ascending', 'fixedrange':True})
    fig_tripuntos.update_layout({
    'plot_bgcolor': 'rgb(255, 255, 255)',
    'paper_bgcolor': 'rgb(255, 255, 255)',
    "showlegend": False
    })
    
    
    # =============================================================================
    # Create Graph from figs
    # =============================================================================
    graph_tripuntos = html.Div(dcc.Graph(id='tripoints-graph',figure=fig_tripuntos,config=config), className="m-3")
    graph_swim = dcc.Graph(id='swim-graph',figure=fig_swim,config=config)
    graph_ride = dcc.Graph(id='ride-graph',figure=fig_ride,config=config)
    graph_run = dcc.Graph(id='run-graph',figure=fig_run,config=config)
    
    graph_sv_swim = dcc.Graph(id='sv_graph_swim',figure=fig_sv_swim,config=config)
    graph_sv_ride = dcc.Graph(id='sv_graph_ride',figure=fig_sv_ride,config=config)
    graph_sv_run = dcc.Graph(id='sv_graph_run',figure=fig_sv_run,config=config)
    
    return dbc.Container(
        [
        # header_logo,
            # header,
            # logo,
            dbc.Row(
                [dbc.Col([header], width={"size": 11}),
                 dbc.Col([logo], width={"size":1}),
            ]
            ),
            title_totals,
            dbc.Row(
                [dbc.Col([graph_sv_swim], width=12, md=4),
                 dbc.Col([graph_sv_ride], width=12, md=4),
                 dbc.Col([graph_sv_run], width=12, md=4)]
            ),
            html.Br(),html.Br(),
            title_tripoints,
            dbc.Row(
                [dbc.Col([graph_tripuntos],width=12)]
            ),
            html.Br(),html.Br(),
            title_sports,
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

app.layout = serve_layout

if __name__ == '__main__':
    app.run(debug=True, port=3004)
    # app.run(debug=False, host='0.0.0.0', port=80)