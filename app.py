import dash
import dash_core_components as dcc      # input 
import dash_html_components as html
from datetime import datetime as dt

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px


app = dash.Dash(__name__)
server = app.server

# html
item1 = html.Div(
    [
        html.H1("Welcome to the Stock Dash App!", className="start"),
        html.Div([
            html.P("Welcome to the Stock Dash App!"),
        ]),
    ])
    

# app
app.layout = html.Div([item1])


# main
if __name__ == '__main__':
    app.run_server(debug=True)

