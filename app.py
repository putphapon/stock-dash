from pydoc import classname
from tkinter.ttk import Style
from turtle import ht
import dash
from dash import dcc
from dash import html
from datetime import datetime as dt
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# model
from model import prediction
from sklearn.svm import SVR

def get_stock_price_fig(df):
    fig = px.line(df,
                  x="Date",
                  y=["Close", "Open"],
                  title="Closing and Openning Price vs Date")
    return fig


def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
                     x="Date",
                     y="EWA_20",
                     title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig

# -----------------------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai+Looped&display=swap",
        "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
        
    ])

server = app.server

app.title = "COS4101 #7"

# html layout of site
app.layout = html.Div(
    [
        html.Div([
            html.Div(
                [
                    # Navigation
                    html.Div([
                        html.A([
                            html.P("Stock App", className="badge bg-success text-wrap text-uppercase fw-bolder fs-3 mt-2 pt-5 mb-0 pb-0"),
                            html.P("by Group 7", className="badge bg-success text-wrap text-uppercase fw-bolder fs-6 mb-2 pb-5 mt-0 pt-0"),
                            ],
                            href="", className="text-decoration-none"),
                        ],
                        className="text-center",
                    ),
                    
                    # Stock Info
                    html.Div([
                        html.Label("Stock Info", className="form-label badge bg-success text-wrap"),
                        html.Div([
                            dcc.Input(id="dropdown_tickers", type="text", className="form-control", placeholder="Input stock code"),
                            html.Button("Submit", id='submit', type="button", className="btn btn-light"),
                        ],
                        className="input-group mb-3 text-capitalize"),
                    ],
                    className="text-capitalize"),
                    
                    # Stock Price/ EMA Stock
                    html.Div([
                        html.Label("Stock Price / EMA Stock",className="form-label badge bg-success text-wrap"),
                        html.Div([
                            dcc.DatePickerRange(id='my-date-picker-range',
                                                min_date_allowed=dt(2000, 1, 1),
                                                max_date_allowed=dt.now(),
                                                initial_visible_month=dt.now(),
                                                end_date=dt.now().date(),
                                                style={'z-index': '100'}),
                        ],
                        className="date d-flex flex-row"),
                        html.Div([
                            html.Button("Stock Price", id="stock", className="btn btn-danger"),
                            html.Button("Indicators", id="indicators", className="btn btn-warning"),
                        ],
                        className="btn-group d-flex flex-row", role="group"),
                    ],
                    className="text-capitalize"),
                    
                    # Stock Price Forecast
                    html.Div([
                        html.Label("Stock Price Forecast", className="form-label badge bg-success text-wrap"),
                        html.Div([
                            dcc.Input(id="n_days", type="number", min="1", max="365", className="form-control", placeholder="number of days"),
                            html.Button("Forecast", id="forecast", type="button", className="btn btn-light"),
                        ],
                        className="input-group mb-3 text-capitalize"),
                    ],
                    className="text-capitalize"),
                ],
                className="col-md-3 col-sm-4 bg-success p-2"),
            
            # content
            html.Div(
                [
                    html.Div([
                        html.Div([
                            # header
                            html.Div([
                                html.Div([
                                    html.Img(id="logo", className="w-100 mw-100 rounded align-items-center", style={'hight': '25vh'}),
                                ],
                                className="col-md-4 col-sm-12 d-flex"),
                                
                                html.Div([
                                    html.P(id="ticker",className="d-flex align-items-center text-capitalize fw-bold fs-1")
                                ],
                                className="col-md-8 col-sm-12 d-flex justify-content-center bg-light p-3", style={'hight': '25vh'}),
                            ],
                            className="row"),
                            
                            # description
                            html.Div([
                                html.Div([
                                    html.Div(id="description", className="align-items-center p-4"),
                                ],className="col d-flex justify-content-center bg-light text-center"),
                            ],className="row"),
                            
                            # content
                            html.Div([
                                html.Div([], id="graphs-content", className="text-center m-2"),
                                html.Div([], id="main-content", className="text-center m-2"),
                                html.Div([], id="forecast-content", className="text-center m-2")
                            ],className="row"),
                            
                        ],
                        className="col"),
                    ],
                    className="row"),
                ],
                className="col-md-9 col-sm-8", style={'min-height': '100vh', 'max-width': '100vw'}),
        ],
        className="row px-2"),
    ],
    className="container-fluit")


# callback for Stock Info
@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("stock", "n_clicks"),
    Output("indicators", "n_clicks"),
    Output("forecast", "n_clicks")
], [Input("submit", "n_clicks")], [State("dropdown_tickers", "value")])
def update_data(n, val):  # inpur parameter(s)
    if n == None:
        return "ค้นหา รหัสหุ้น ที่คุณต้องการ", "https://www.freeiconspng.com/thumbs/stock-exchange-icon-png/stock-exchange-icon-png-1.png", "Stocks", None, None, None
        # raise PreventUpdate
    else:
        if val == None:
            raise PreventUpdate
        else:
            ticker = yf.Ticker(val)
            inf = ticker.info
            df = pd.DataFrame().from_dict(inf, orient="index").T
            df[['logo_url', 'shortName', 'longBusinessSummary']]
            return df['longBusinessSummary'].values[0], df['logo_url'].values[
                0], df['shortName'].values[0], None, None, None


# callback for Stock Price graphs
@app.callback([
    Output("graphs-content", "children"),
], [
    Input("stock", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
        #raise PreventUpdate
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]


# callback for EMA indicators
@app.callback([Output("main-content", "children")], [
    Input("indicators", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]


# callback for Price Forecast
@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("dropdown_tickers", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(
        debug=False,
        port=41017
        )
