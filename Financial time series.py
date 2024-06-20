#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 19:01:52 2022

@author: daniellomeli
"""

import numpy as np 
import pandas as pd
from pylab import mpl,plt
plt.style.use('seaborn')
mpl.rcParams['font.family']= 'serif'
import pandas_datareader as web
import datetime as dt
 
start = dt.datetime(2022,5,6)
end = dt.datetime(2022,7,6)

df= web.DataReader('QQQ','yahoo',start,end)

#sacar una columna del dataframe
sym = 'Close'
QQQ = pd.DataFrame(df[sym]).dropna()
QQQ.tail()

#Graficar una de las columnas
#plt.plot(df['Close'])

#cambiar nombre de las columnas
#df.columns = ['new_col1', 'new_col2', 'new_col3', 'new_col4']

#Cambios en el tiempo frente al anterior
#df.diff().head()

#Cambio porcentual redondeado a tres decimales
QQQ.pct_change().round(3).head()

#logarithmic returns
rets = np.log(QQQ / QQQ.shift(1))

#Plots the cumulative log returns over time; first the cumsum() 
#method is called, then np.exp() is applied to the results.
rets.cumsum().apply(np.exp).plot(figsize=(10, 6))

#Cambiar temporalidad
#df.resample('1w', label='right').last().head()
#%%
'''
Rolling statistics
'''
#Crear nueva variable
data = pd.DataFrame(df[sym]).dropna()
#Defines the window; i.e., the number of index values to include.
window = 20
#Calculates the rolling minimum value.
data['min'] = data[sym].rolling(window=window).min()
#Calculates the rolling mean value.
data['mean'] = data[sym].rolling(window=window).mean()
#Calculates the rolling standard deviation.
data['std'] = data[sym].rolling(window=window).std()
#Calculates the rolling median value.
data['median'] = data[sym].rolling(window=window).median()
#Calculates the rolling maximum value.
data['max'] = data[sym].rolling(window=window).max()
#Calculates the exponentially weighted moving average, with decay in terms of a half life of 0.5.
data['ewma'] = data[sym].ewm(halflife=0.5, min_periods=window).mean()

#Graficar los datos y estadisticas
ax = data[['min', 'mean', 'max']].plot(
              figsize=(10, 6), style=['g--', 'r--', 'g--'], lw=0.8) #1
data[sym].plot(ax=ax, lw=2.0); #2

#1 Plots three rolling statistics for the final 200 data rows.
#2 Adds the original time series data to the plot.

#media movil de n periodos
QQQ['SMA1'] = QQQ[sym].rolling(window=20).mean()
QQQ['SMA2'] = QQQ[sym].rolling(window=50).mean()

#Graficar columna de datos con medias moviles
QQQ[[sym, 'SMA1', 'SMA2']].plot(figsize=(10, 6));

#Estrategia con medias moviles, visualizes a long position by a value of 1
#and a short position by a value of -1. The change in the position is triggered 
#(vis‐ ually) by a crossover of the two lines representing the SMA time series:
QQQ['positions'] = np.where(QQQ['SMA1'] > QQQ['SMA2'],1,-1)
# graficar estrategia
ax = QQQ[[sym, 'SMA1', 'SMA2', 'positions']].plot(figsize=(10, 6),secondary_y='positions')
ax.get_legend().set_bbox_to_anchor((0.25, 0.85))
#%%
'''
Correlation Analysis
'''

#1 Agregar nuevo ticker 
df1= web.DataReader('^VIX','yahoo',start,end)
#Sacar la columna Close
VIX = pd.DataFrame(df1['Close']).dropna()
QQQ = pd.DataFrame(df['Close']).dropna()
#3 REnombrar columnas y combinar los dos dataframes
QQQ.columns = ['QQQ']
VIX.columns = ['VIX']
Analysis = pd.concat([QQQ,VIX], axis = 1)
#4 Graficar ambos dataframes con subplots
Analysis.plot(subplots=True, figsize=(10, 6));
#5 Graficar los dataframes juntos con dos indices
Analysis.plot(secondary_y='VIX', figsize=(10, 6));

#%%
# Logarithmic returns



rets = np.log(Analysis / Analysis.shift(1))

#graficar logarithmic returns

rets.dropna(inplace =True)
rets.plot(subplots=True, figsize=(10, 6));
#%%
#OLS regression

reg = np.polyfit(rets['QQQ'], rets['VIX'], deg=1)
"""
Shows a scatter plot of the log returns and the linear regression 
line through the cloud of dots. 
"""

ax = rets.plot(kind='scatter', x='QQQ', y='VIX', figsize=(10, 6))
ax.plot(rets['QQQ'], np.polyval(reg, rets['QQQ']), 'r', lw=2);
    

#%%
'''
Indice de correlación
'''

rets.corr()

#grafica de el indice de correlacion tanto statico como rolling
ax = rets['QQQ'].rolling(window=25).corr(rets['VIX']).plot(figsize=(10, 6))
ax.axhline(rets.corr().iloc[0, 1], c='r');
#%%