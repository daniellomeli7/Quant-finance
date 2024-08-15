#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 17:34:36 2024

@author: daniellomeli
"""

import datetime as dt
import pandas as pd
import numpy as np
from finta import TA
import matplotlib.pyplot as plt
import yfinance as yf

#Input parameters

end = dt.datetime.today()
interval = 4000
start = end - dt.timedelta(interval)
asset = ["QQQ", "META", "NFLX","MSFT","NVDA","AAPL","^GSPC","DIS","INTC","AMD","TSLA","TQQQ","GME","IVV"]
investment_per_period = 2000
period_lenght = 21


#Data import

def close(ticker,start,end):
    df = yf.download(ticker,start,end)
    df = df.dropna()
    df = df['Close']
    df = df.reset_index()
    return df 


df = close(asset, start, end)

returns =  df.copy()
returns.set_index('Date', inplace=True)
returns = returns.pct_change()
returns = returns.dropna()

periods = len(df)// period_lenght

#%%

for i in range(1,len(df.columns)):
    df['Periodo'] = (df.index // period_lenght) + 1
    df[f"Titulos {df.columns[i]}"] = 0
    df[f"Titulos {df.columns[i]}"][df['Periodo']==1]= investment_per_period/df[df.columns[i]][0]
    


#%%

for s in range(len(asset)):
    
    i = 2
    for x in range(periods):
        df[f"Titulos {asset[s]}"][df['Periodo']==i]= investment_per_period/df[asset[s]][(i-1)*period_lenght] + \
            df[f"Titulos {asset[s]}"][df['Periodo']==i-1][(i-2)*period_lenght]
        df[f'Capital {asset[s]}']= df[f"Titulos {asset[s]}"]*df[asset[s]]
        i+=1


#%%
    
df["Aportado"] = df["Periodo"]* investment_per_period

#%%

# import plotly.io as pio

# # Set default renderer to browser
# pio.renderers.default = 'browser'

# # Using plotly.express
# import plotly.express as px
# from plotly.offline import plot

# fig = px.line(df, x=df[df.columns[0]], y=df.columns[-(len(asset)+1):])
# fig.show()

#%%
table = df[df.columns[-(len(asset)+1):].copy()]

table1 = table.loc[[251,(252*3)-1,(252*5)-1,(252*10)-1]]
table1.head()

VaR = np.percentile(returns,5,axis=0)
CVaR = np.mean(returns[returns<=VaR],axis=0)

table1.columns = [col.replace('Capital', '') for col in table1.columns]

table1 =table1.T

VaR = list(VaR)

VaR.extend([np.nan] * (len(table1) - len(VaR)))

CVaR = list(CVaR)

CVaR.extend([np.nan] * (len(table1) - len(CVaR)))

table1["CVaR"] = CVaR

table1["VaR"] = VaR

table1.iloc[:, :4] = np.round(table1.iloc[:,:4],3)
table1[["VaR","CVaR"]] = np.round(table1[["VaR","CVaR"]],5)

table1

table1 =table1.rename(columns={251: "1 yr", 755: "3 yr",1259:"5 yr",2519:"10 yr"})

table1 = table1.reset_index()

table1.iloc[:, 1:5] = table1.iloc[:, 1:5].applymap(lambda x: "${:,.2f}".format(x))

#%%

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import webbrowser
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_table

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    style={"padding": "20px"},  # Set padding for the full-page layout
    children=[
        html.H1('Dollar Cost Averaging', style={'textAlign': 'center', 'color': '#2c3e50', 'fontSize': '100px'}),
        html.P("Select stock:", style={'color': '#34495e', 'fontSize': '45px'}),
        dcc.Dropdown(
            id="ticker",
            options=asset,
            value=asset[0],
            clearable=False,
            style={'fontSize': '30px', 'color': '#34495e','width': '40vw'}
        ),
        
       html.Div([
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id="time-series-chart", style={"height": "50vh"})
                ]),
                style={"width": "62vw"}
            ),
            # Column with the first table
            dbc.Card(
                dbc.CardBody([
                    dash_table.DataTable(
                        id='table1',
                        columns=[{"name": i, "id": i} for i in table1.columns],
                        data=table1.to_dict('records'),
                        style_table={'width': '35vw'},
                        style_header={'backgroundColor': '#95a5a6', 'color': 'white', 'fontWeight': 'bold'},
                        style_cell={'backgroundColor': '#ecf0f1', 'color': '#2c3e50', 'fontSize': '20px'},  # Increased font size
                    )
                ]),
                style={"width": "37vw", "marginLeft": "20px"}
            )
        ], style={"display": "flex", "flexDirection": "row", "alignItems": "flex-start", "justifyContent": "space-between", "marginTop": "20px"}),
        
        html.H1('Value at Risk 95%', style={'textAlign': 'center', 'color': '#2c3e50', 'fontSize': '80px'}),
        
        # Positioned sh table below the title, centered
        html.Div(
            dbc.Card(
                dbc.CardBody([
                    dash_table.DataTable(
                        id='sh',
                        columns=[{"name": i, "id": i} for i in ['Mean return', 'Volatility', 'Sharpe Ratio']],
                        style_table={'width': '35vw', 'marginTop': '20px', 'marginLeft': 'auto', 'marginRight': 'auto',},
                        style_header={'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': 'bold'},
                        style_cell={'backgroundColor': '#ecf0f1', 'color': '#2c3e50', 'fontSize': '40px',"textAlign": "center"},  # Slightly smaller font size for the second table
                    )
                ])
            ),
            style={"textAlign": "center", "marginTop": "20px"}
        ),
        
        # Bottom container with two graphs
        html.Div([
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id="returns-hist", style={"height": "40vh"})
                ]),
                style={"width": "50vw"}
            ),
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id="line-plot", style={"height": "40vh"})
                ]),
                style={"width": "50vw", "marginLeft": "20px"}
            )
        ], style={"display": "flex", "flexDirection": "row", "alignItems": "flex-start", "justifyContent": "space-between", "marginTop": "20px"})
    ]
)


@app.callback(
    [Output("time-series-chart", "figure"), 
     Output("returns-hist", "figure"),
     Output("line-plot", "figure"),
     Output("sh","data")],
    Input("ticker", "value"),
)
def display_time_series(ticker):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df[f'Capital {ticker}'],
        mode='lines',
        line=dict(color='#1f77b4'),
        fill='tozeroy',
        name=f'Capital {ticker}'
    ))

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Aportado'],
        mode='lines',
        line=dict(color='#ff7f0e'),
        fill='tozeroy',
        name='Aportado'
    ))

    fig.update_layout(
        title={
        'text': f"Saving vs DCA in {ticker}",
        'y':0.95,  # Adjust the y-position of the title
        'x':0.5,  # Center the title
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(size=50)
    },
        plot_bgcolor='#ecf0f1',
        paper_bgcolor='#ecf0f1',
        font=dict(color='#2c3e50'),
        
        xaxis=dict(
        showgrid=True, 
        title_text='Date',
        title_font=dict(size=25),  # Increase the x-axis title font size
        tickfont=dict(size=25)     # Increase the x-axis tick label font size
        ),
        yaxis=dict(
        showgrid=True, 
        title_text='Value',
        title_font=dict(size=25),  # Increase the y-axis title font size
        tickfont=dict(size=25)     # Increase the y-axis tick label font size
        ),
        showlegend=False,
        hoverlabel=dict(font_size=30)
        ),
        

    VaR = np.percentile(returns[ticker], 5)
    varn = returns[ticker][lambda x: x > VaR]
    vary = returns[ticker][lambda x: x <= VaR]

    hist = go.Figure()
    hist.add_trace(go.Histogram(x=varn))
    hist.add_trace(go.Histogram(x=vary))
    hist.update_layout(
        plot_bgcolor='#ecf0f1',
        paper_bgcolor='#ecf0f1',
        font=dict(color='#2c3e50', size=14),
        barmode='stack',
        xaxis=dict(
        showgrid=True, 
        title_text='Returns',
        title_font=dict(size=25),  # Increase the x-axis title font size
        tickfont=dict(size=25)     # Increase the x-axis tick label font size
        ),
        yaxis=dict(
        showgrid=True, 
        title_text='Freq',
        title_font=dict(size=25),  # Increase the y-axis title font size
        tickfont=dict(size=25)     # Increase the y-axis tick label font size
        ),
        showlegend=False,
        hoverlabel=dict(font_size=30)  # Increase hover label font size
    )

    ts = go.Figure()
    ts.add_trace(go.Scatter(
        x=returns.index,
        y=returns[ticker],
        mode='lines',
        name=f"{ticker} Returns"
    ))

    ts.add_trace(go.Scatter(
        x=[returns.index.min(), returns.index.max()],
        y=[VaR, VaR],
        mode='lines',
        name='VaR',
        line=dict(color='red')
    ))

    ts.update_layout(
        plot_bgcolor='#ecf0f1',
        paper_bgcolor='#ecf0f1',
        font=dict(color='#2c3e50', size=14),
        xaxis=dict(
        showgrid=True, 
        title_text='Time',
        title_font=dict(size=25),  # Increase the x-axis title font size
        tickfont=dict(size=25)     # Increase the x-axis tick label font size
        ),
        yaxis=dict(
        showgrid=True, 
        title_text='Returns',
        title_font=dict(size=25),  # Increase the y-axis title font size
        tickfont=dict(size=25)     # Increase the y-axis tick label font size
        ),
        showlegend=False,
        hoverlabel=dict(font_size=30)  # Increase hover label font size
    )
    
    info = [
        round(returns[ticker].mean() * 252, 5),
        round(returns[ticker].std() * np.sqrt(252), 5),
        round((returns[ticker].mean() / returns[ticker].std()) * np.sqrt(252), 5)
    ]
    
    sh_data = pd.DataFrame([info], columns=['Mean return', 'Volatility', 'Sharpe Ratio']).to_dict('records')
    
    return fig, hist, ts, sh_data


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8054')
    app.run_server(debug=True, port=8054, use_reloader=False)
    
#%%
info = list()
sh = pd.DataFrame(columns=['Mean return', 'Volatility', 'Sharpe Ratio'])

info.append(returns["QQQ"].mean()*252)
info.append(returns["QQQ"].std()*np.sqrt(252))
info.append(returns["QQQ"].mean()/returns["QQQ"].std()*np.sqrt(252))
sh.loc[0] = info