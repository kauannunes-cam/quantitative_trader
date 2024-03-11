import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from bcb import Expectativas
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from bcb import sgs
from fredapi import Fred
import yfinance as yf



end_date = datetime.now()
start_date = end_date - timedelta(days=1460)
api_key = '380531467d6612b096037c4a0a81412b'

periodo = 60

ativos = ['USDBRL=X', '^BVSP']

for i, ativo in enumerate(ativos):
    dados = yf.download(ativo, start=start_date, end=end_date)['Adj Close'].tail(90)
    ultimo_valor = dados.tail(1)
    var_percentual = dados.pct_change()
    desvio_7 = var_percentual.rolling(window=7).std()
    desvio_14 = var_percentual.rolling(window=14).std()
    desvio_21 = var_percentual.rolling(window=21).std()

    # Calcular média dos desvios padrão
    desvio_padrao = pd.concat([desvio_7, desvio_14, desvio_21], axis=1).mean(axis=1)


    # Criar gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dados.index, y=dados, mode='lines', name=ativo, line=dict(color='white')))

    # Adicionar linhas de desvio padrão
    for n in [1, 2, 3]:
        fig.add_trace(go.Scatter(
            x=dados.index, 
            y=dados + n * desvio_padrao * dados,
            mode='lines', name=f'Desvio +{n}', line=dict(color='#EF7737', dash='solid')))
        fig.add_trace(go.Scatter(
            x=dados.index, 
            y=dados - n * desvio_padrao * dados,
            mode='lines', name=f'Desvio -{n}', line=dict(color='#EF7737', dash='solid')))

    # Configurar layout
    fig.update_layout(
    title={'text': f'Histórico de Preços e Desvio Padrão - {ativo}', 
            'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'color': 'white'}},
    xaxis_title='Período',
    yaxis_title='Valores',
    paper_bgcolor='rgba(0,0,0,0.6)',
    plot_bgcolor='rgba(0,0,0,0.6)',
    font=dict(color='white'),
    legend=dict(
        font=dict(color='white'),
        x=0,  # Posição horizontal da legenda (0 = extrema esquerda)
        y=1,  # Posição vertical da legenda (1 = topo)
        bgcolor='rgba(0,0,0,0.6)',  # Cor de fundo da legenda
        bordercolor='white'  # Cor da borda da legenda
    ),
    xaxis=dict(showgrid=False, title_font=dict(color='white'), tickfont=dict(color='white')),
    yaxis=dict(showgrid=False, side='right', title_font=dict(color='white'), tickfont=dict(color='white'))
    )   

    # Salvar gráfico
    fig.write_html(f'fig{i+1}.html')
