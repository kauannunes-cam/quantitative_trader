import pandas as pd
import datetime
import plotly.graph_objects as go
import plotly.io as pio
from dados_mt5 import pegando_todos_os_tickers, puxando_cotacoes

def criando_grafico_acao(acao):
    dados = pd.read_parquet("cotacoes.parquet")
    dados['time'] = pd.to_datetime(dados['time'])
    dados = dados.set_index('time')
    acao_grafico = dados[dados['ticker'] == acao]

    acao_grafico = acao_grafico[acao_grafico.index > datetime.datetime.now() - datetime.timedelta(days=1095)]
    
    # Calculando a variação percentual diária
    acao_grafico['daily_pct_change'] = acao_grafico['close'].pct_change() * 100

    # Calculando médias móveis e desvios padrões das variações percentuais
    for window in [7, 14, 21]:
        acao_grafico[f'std_pct_change_{window}'] = acao_grafico['daily_pct_change'].rolling(window=window).std()
    
    # Calculando a média dos desvios padrões das variações percentuais
    acao_grafico['mean_std_pct_change'] = acao_grafico[[f'std_pct_change_{window}' for window in [7, 14, 21]]].mean(axis=1)
    
    # Último preço de fechamento ajustado
    last_adjusted_close = acao_grafico['close'].iloc[-1]

    layout = go.Layout(yaxis=dict(tickfont=dict(color="#D3D6DF"), showline=False),
                       xaxis=dict(tickfont=dict(color="#D3D6DF"), showline=False))

    fig_ma = go.Figure(data=[go.Candlestick(x=acao_grafico.index,
                                        open=acao_grafico['open'], 
                                        high=acao_grafico['high'],
                                        low=acao_grafico['low'],
                                        close=acao_grafico['close']), 
                        ], layout=layout)
    
    # Adicionando as faixas de desvio padrão
    std_multiplier = 2.33
    fig_ma.add_trace(go.Scatter(
        x=acao_grafico.index, 
        y=last_adjusted_close + std_multiplier * acao_grafico['mean_std_pct_change'],
        mode='lines',
        name='Upper Limit',
        line=dict(width=2, color='red')
    ))
    
    fig_ma.add_trace(go.Scatter(
        x=acao_grafico.index, 
        y=last_adjusted_close - std_multiplier * acao_grafico['mean_std_pct_change'],
        mode='lines',
        name='Lower Limit',
        line=dict(width=2, color='darkblue')
    ))

    # Atualizando config_maurações do layout
    fig_ma.update_layout(
        margin=dict(l=24, r=45, t=31, b=23), showlegend=False, font=dict(color="#D3D6DF"),
        plot_bgcolor='black',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False,
        xaxis_tickcolor='#131516', xaxis_showgrid=False,
        yaxis_tickcolor='#131516', yaxis_showgrid=False
    )

    return fig_ma


def tabela_cotacao_setor_bolsa(setor_escolhido):

    acoes_mt5 = pegando_todos_os_tickers()

    caminho_arquivo = 'C:/Users/Kauan/OneDrive/Área de Trabalho/QuantitativeTrader/projeto_final/setores.csv'

    df_setores = pd.read_csv(caminho_arquivo, skiprows=[1]) 

    empresas_do_setor = df_setores[df_setores['SETOR'] == setor_escolhido]
    empresas_do_setor = empresas_do_setor['TICKER'].to_list()

    lista_tickers = [ticker for ticker in acoes_mt5 if ticker[:4] in empresas_do_setor] 
    lista_tickers = sorted(lista_tickers, reverse=True)
    lista_ticker_maior_liquidez = []

    for ticker in lista_tickers:

        if ticker[:4] + "4" not in lista_ticker_maior_liquidez:

            lista_ticker_maior_liquidez.append(ticker)

    cotacoes_ao_vivo = puxando_cotacoes(lista_ticker_maior_liquidez)

    cotacoes_ao_vivo = cotacoes_ao_vivo.dropna()

    return cotacoes_ao_vivo

def fazer_grafico_di(periodo):
        
        hoje = datetime.datetime.now() 
        
        dados_di = pd.read_csv('dados_di.csv')
        dados_di['data_vencimento'] = pd.to_datetime(dados_di['data_vencimento']).dt.date
        
        dados_atuais = dados_di[dados_di['data_preco'] == 'hoje']
        dados_atuais = dados_atuais.set_index('data_vencimento')
        dados_atuais = dados_atuais['preço']

        if periodo == '1 ano':
             
            dados_antigos = dados_di[dados_di['data_preco'] == 'um_ano_atras']
            data_antiga = hoje - datetime.timedelta(days = 365)
            data_antiga = data_antiga.strftime("%d/%m/%Y")
        
        elif periodo == '3 anos':
             
            dados_antigos = dados_di[dados_di['data_preco'] == 'tres_anos_atras']
            data_antiga = hoje - datetime.timedelta(days = 365 * 3)
            data_antiga = data_antiga.strftime("%d/%m/%Y")
        
        elif periodo == '5 anos':
             
            dados_antigos = dados_di[dados_di['data_preco'] == 'cinco_anos_atras']
            data_antiga = hoje - datetime.timedelta(days = 365 * 5)
            data_antiga = data_antiga.strftime("%d/%m/%Y")
        
        elif periodo == '10 anos':
             
            dados_antigos = dados_di[dados_di['data_preco'] == 'dez_anos_atras']
            data_antiga = hoje - datetime.timedelta(days = 365 * 10)
            data_antiga = data_antiga.strftime("%d/%m/%Y")
        
        dados_antigos = dados_antigos.set_index('data_vencimento')
        dados_antigos = dados_antigos['preço']
        
        hoje = hoje.strftime("%d/%m/%Y")

        layout = go.Layout(yaxis=dict(tickformat=".1%", tickfont=dict(color="#D3D6DF"), showline = False),
                            xaxis=dict(tickfont=dict(color="#D3D6DF"), showline = False))

        fig_di = go.Figure(layout=layout)

        fig_di.add_trace(go.Scatter(x=dados_atuais.index, y=dados_atuais.values, name=f"Curva {hoje}",
                                line=dict(color='#EB7737', width=4), mode='lines+markers'))
        fig_di.add_trace(go.Scatter(x=dados_antigos.index, y=dados_antigos.values, name=f"Curva {data_antiga}",
                                line=dict(color='#fff', width=4), mode='lines+markers'))

        fig_di.update_layout(
            margin=dict(l=60, r=48, t=24, b=36, autoexpand = False), legend=dict(x= 0.6, y=0.1, bgcolor = '#131516'), font = dict(color = "#D3D6DF"))

        fig_di.layout.plot_bgcolor = 'black'
        fig_di.update_layout(paper_bgcolor='rgba(0,0,0,0)') #deixamos o paper transparante pra mudar o background no CSS e fazer border

        fig_di.update_xaxes(tickcolor = '#131516', showgrid=False)
        fig_di.update_yaxes(tickcolor = '#131516', showgrid=False)
        
        return fig_di

def fazer_tabela_di():

    df = pd.read_csv('dados_di.csv')
    df['data_vencimento'] = pd.to_datetime(df['data_vencimento'])
    df = df[df['data_preco'] == 'hoje']
    df = df.set_index('data_vencimento')
    df = df['preço']

    hoje = datetime.datetime.now()
    ano_atual = hoje.year
    mes_atual = hoje.month

    DI_1Y = str(round(((df[df.index > datetime.datetime(ano_atual + 1, mes_atual, 1, 0, 0, 0)]).iloc[0] * 100), 2)) + "%" 
    DI_3Y = str(round(((df[df.index > datetime.datetime(ano_atual + 3, mes_atual, 1, 0, 0, 0)]).iloc[0] * 100), 2)) + "%" 
    DI_5Y = str(round(((df[df.index > datetime.datetime(ano_atual + 5, mes_atual, 1, 0, 0, 0)]).iloc[0] * 100), 2)) + "%" 
    DI_10Y = str(round(((df[df.index >= datetime.datetime(ano_atual + 10, 1, 1, 0, 0, 0)]).iloc[0] * 100), 2)) + "%" 

    df = pd.DataFrame({"ignore_1": ['DI 1Y', 'DI 3Y', 'DI 5Y', 'DI 10Y'], 'ignore_2': [DI_1Y, DI_3Y, DI_5Y, DI_10Y]})

    return df


def info_inflacao():
    
    inflacao = pd.read_csv('inflacao.csv')
    hoje = datetime.datetime.now()
    ano_atual = hoje.year
    inflacao = inflacao.set_index('Date')
    inflacao.index = pd.to_datetime(inflacao.index)

    inflacao = inflacao.iloc[-12:, :]

    inflacao_12m = (1 + inflacao).cumprod() - 1
    inflacao_ano = inflacao.loc[f'{ano_atual}']
    inflacao_ano = (1 + inflacao_ano).cumprod() - 1

    IPCA_12M = str(round((inflacao_12m.iloc[-1, 0] * 100), 2)) + "%"
    IGPM_12M = str(round((inflacao_12m.iloc[-1, 1] * 100), 2)) + "%"
    IPCA_ANO = str(round((inflacao_ano.iloc[-1, 0] * 100), 2)) + "%"
    IGPM_ANO = str(round((inflacao_ano.iloc[-1, 1] * 100), 2)) + "%"

    df = pd.DataFrame({"ignore_1": ["IPCA 12M", 'IGPM 12M', 'IPCA ANO', 'IGPM ANO'], 'ignore_2': [IPCA_12M, IGPM_12M, IPCA_ANO, IGPM_ANO]})

    return df

def grafico_inflacao(anos):

    pio.templates.default = "simple_white"
    
    inflacao = pd.read_csv('inflacao.csv')
    inflacao = inflacao.set_index('Date')
    inflacao.index = pd.to_datetime(inflacao.index)

    if anos == '1 ano':

        inflacao = inflacao.iloc[-12:, :]

    elif anos == '3 anos':

        inflacao = inflacao.iloc[-36:, :]
    
    elif anos == '5 anos':

        inflacao = inflacao.iloc[-60:, :]

    elif anos == '10 anos':

        inflacao = inflacao.iloc[-120:, :]

    layout = go.Layout(yaxis=dict(tickformat=".2%", tickfont=dict(color="#D3D6DF"), showline = False),
                        xaxis=dict(tickfont=dict(color="#D3D6DF"), showline = False))

    fig_infla = go.Figure(data=[
        go.Scatter(name='IPCA', x=inflacao.index, y=inflacao['ipca'], marker_color='orange'),
        go.Scatter(name='IGPM', x=inflacao.index, y=inflacao['igp-m'], marker_color='white')
    ], layout=layout)

    fig_infla.add_shape( # add a horizontal "target" line
        type="line", line_color="white", line_width=3, opacity=1,
        x0=0, x1=1, xref="paper", y0=0, y1=0, yref="y"
    )
    fig_infla.update_layout(font = dict(color = "#D3D6DF"), margin=dict(l=24, r=45, t=31, b=23))
    
    fig_infla.layout.plot_bgcolor = '#131516'
    fig_infla.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    
    fig_infla.update_xaxes(tickcolor = '#131516')
    fig_infla.update_yaxes(tickcolor = '#131516')
    
    return fig_infla



def info_divida_pib():

    dados = pd.read_csv('divida_pib.csv')
    hoje = datetime.datetime.now()
    ano_passado = hoje.year - 1
    dados = dados.set_index('Date')
    dados.index = pd.to_datetime(dados.index)
    
    dados = dados.iloc[-13:, :]

    VALOR_ATUAL = str(round((dados.iloc[-1, 0] * 100), 2)) + "%"
    VAR_12M = str(round(((dados.iloc[-1, 0] - dados.iloc[1, 0]) * 100), 2)) + "%" 
    VAR_ANO = str(round(((dados.iloc[-1, 0] - (dados.loc[f'{ano_passado}']).iloc[-1, 0]) * 100), 2)) + "%"  
    VAR_MES = str(round(((dados.iloc[-1, 0] - dados.iloc[-2, 0]) * 100), 2)) + "%"  

    df = pd.DataFrame({"ignore_1": ['VALOR ATUAL', 'Δ 12M', 'Δ ANO', 'Δ MÊS'], 'ignore_2': [VALOR_ATUAL, VAR_12M, VAR_ANO, VAR_MES]})

    return df



def grafico_divida_pib(anos):

    pio.templates.default = "simple_white"
    
    dados = pd.read_csv('divida_pib.csv')
    dados = dados.set_index('Date')
    dados.index = pd.to_datetime(dados.index)

    if anos == '1 ano':

        dados = dados.iloc[-252:, :]

    elif anos == '3 anos':

        dados = dados.iloc[-(252 * 3):, :]
    
    elif anos == '5 anos':

        dados = dados.iloc[-(252 * 5):, :]

    elif anos == '10 anos':

        dados = dados.iloc[-(252 * 10):, :]

    layout = go.Layout(yaxis=dict(tickformat=".2%", tickfont=dict(color="#D3D6DF"), showline = False),
                        xaxis=dict(tickfont=dict(color="#D3D6DF"), showline = False))

    fig_divida_pib = go.Figure(data=[
        go.Scatter(name='Dívida PIB', x=dados.index, y=dados['DIVIDA_PIB'], marker_color='#EB7737')
    ], layout=layout)

    fig_divida_pib.update_layout(font = dict(color = "#D3D6DF"), margin=dict(l=24, r=45, t=31, b=23))
    
    fig_divida_pib.layout.plot_bgcolor = '#131516'
    fig_divida_pib.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    
    fig_divida_pib.update_xaxes(tickcolor = '#131516')
    fig_divida_pib.update_yaxes(tickcolor = '#131516')

    return fig_divida_pib


def info_dolar():

    dados = pd.read_csv('dolar.csv')
    hoje = datetime.datetime.now()
    ano_passado = hoje.year - 1
    dados = dados.set_index('Date')
    dados.index = pd.to_datetime(dados.index)

    VALOR_ATUAL = "R$" + str(round((dados.iloc[-1, 0]), 2))
    VAR_12M = str(round(((dados.iloc[-1, 0]/dados.iloc[1, 0]) - 1), 2)) + "%" 
    VAR_ANO = str(round(((dados.iloc[-1, 0] / dados.loc[f'{ano_passado}'].iloc[-1, 0]) - 1), 2)) + "%"  
    VOL = str(round(((dados.pct_change().std().iloc[0] * 15.87) * 100), 2)) + "%"  

    df = pd.DataFrame({"ignore_1": ['VALOR ATUAL', 'Δ 12M', 'Δ ANO', 'VOL'], 'ignore_2': [VALOR_ATUAL, VAR_12M, VAR_ANO, VOL]})

    return df

def grafico_dolar(anos):

    pio.templates.default = "simple_white"
    
    dados = pd.read_csv('dolar.csv')
    dados = dados.set_index('Date')
    dados.index = pd.to_datetime(dados.index)

    if anos == '1 ano':

        dados = dados.iloc[-252:, :]

    elif anos == '3 anos':

        dados = dados.iloc[-(252 * 3):, :]
    
    elif anos == '5 anos':

        dados = dados.iloc[-(252 * 5):, :]

    elif anos == '10 anos':

        dados = dados.iloc[-(252 * 10):, :]

    layout = go.Layout(yaxis=dict(tickfont=dict(color="#D3D6DF"), showline = False),
                        xaxis=dict(tickfont=dict(color="#D3D6DF"), showline = False))

    fig_dolar = go.Figure(data=[
        go.Scatter(name='Dólar', x=dados.index, y=dados['DOLAR'], marker_color='#EB7737')
    ], layout=layout)

    fig_dolar.update_layout(font = dict(color = "#D3D6DF"), margin=dict(l=24, r=45, t=31, b=23))
    fig_dolar.update_layout(yaxis_tickprefix = 'R$', yaxis_tickformat = ',.2f')
    
    fig_dolar.layout.plot_bgcolor = '#131516'
    fig_dolar.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    
    fig_dolar.update_xaxes(tickcolor = '#131516')
    fig_dolar.update_yaxes(tickcolor = '#131516')

    return fig_dolar


























