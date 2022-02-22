import sqlite3
from flask import Flask, render_template, redirect
import dash
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

def emptyLayout(text='No matching data found'):
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": text,
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 34
                        }
                    }
                ]
            }
        }


def init_app():
    appFlask = Flask(__name__)

    appDash = dash.Dash(__name__, server=appFlask, url_base_pathname='/dash/')

    con = sqlite3.connect('data.sqlite')

    df_timelog = pd.read_sql_query('SELECT * FROM timelog', con)
    #print(df_timelog.head())
    fig_workDuration = px.histogram(df_timelog, x='userId', y='workedDuration', color='userId',  
    barmode='group')
    fig_workStatus = px.histogram(df_timelog, x='workStatus',  color='workStatus', barmode='group')
    
    df_jobs = pd.read_sql_query('SELECT * FROM jobs', con)
    #print(df_jobs.head())
    fig_jobStatus = px.histogram(df_jobs, x='currentStatus', color='currentStatus', barmode='group')

    df_Users = pd.read_sql_query('SELECT * FROM users WHERE userIdIndex > "0"', con)
    print(df_Users[['userId', 'userName']].values)
    df_Users['dropdown_values'] = df_Users[['userIdIndex','userName']].agg(':'.join, axis=1)

    
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
    ),
    dcc.Dropdown(
        df_Users['dropdown_values'] , 'Users', id='dropdown_users'),
    dcc.Graph(id='dropdown_figure')
    ]) 
    
    @appDash.callback(
    Output('dropdown_figure', 'figure'),
    Input('dropdown_users', 'value')
    )
    def update_user_graph(value):
        con = sqlite3.connect('data.sqlite')

        # If nothing has been selected we draw the empty layout
        if(value == 'Users' or not value):
            return emptyLayout("Please select User from the dropdown menu.")

        # Format <index>:<username>
        index_username = value.split(':', maxsplit=1)
        
        # We get the UserId from Users table using UserIdIndex
        userId = df_Users.loc[df_Users['userIdIndex']==index_username[0], 'userId']
        
        # Get the data from timelog table using UserId
        df_jobs_by_userId = pd.read_sql_query(f'SELECT * FROM timelog WHERE userId==\"{userId.values[0]}\" AND userId>"0"', con)

        dropdown_figure = px.histogram(df_jobs_by_userId, x='userId', y='workedDuration', color='userId',  barmode='group')

        return dropdown_figure

    return appFlask

app = init_app()

@app.route("/")
def home():
    """Landing page."""
    return render_template("index.jinja2", title="Landing Page")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)
