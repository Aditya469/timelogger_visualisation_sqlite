import sqlite3
from flask import Flask, render_template, redirect
import dash
import pandas as pd
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd


def init_app():
    appFlask = Flask(__name__)

    appDash = dash.Dash(__name__, server=appFlask, url_base_pathname='/dash/')

    con = sqlite3.connect('data.sqlite')
    df_timelog = pd.read_sql_query('SELECT * FROM timelog', con)
    print(df_timelog.head())

    df_jobs = pd.read_sql_query('SELECT * FROM jobs', con)
    print(df_jobs.head())

    fig_workDuration = px.histogram(df_timelog, x='userId', y='workedDuration', color='userId',  
    barmode='group')

    fig_workStatus = px.histogram(df_timelog, x='workStatus',  color='workStatus', barmode='group')

    fig_jobStatus = px.histogram(df_jobs, x='currentStatus', color='currentStatus', barmode='group')

    appDash.layout = html.Div(children=[
    html.H1(children='Dash Application'),
    html.Div(children='''
    Dash: Web Application
    '''),
    dcc.Graph(
        id='fig_workDuration-graph',
        figure=fig_workDuration
    ),
    dcc.Graph(
        id='fig_workStatus',
        figure=fig_workStatus
    ),
    dcc.Graph(
        id='fig_jobStatus',
        figure=fig_jobStatus
    )
    ]) 

    return appFlask

app = init_app()

@app.route("/")
def home():
    """Landing page."""
    return render_template("index.jinja2", title="Landing Page")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)