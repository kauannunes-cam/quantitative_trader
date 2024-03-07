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
        go.Scatter(name='Dívida PIB', x=dados.index, y=dados['DIVIDA_PIB'], marker_color='#49E2B1')
    ], layout=layout)

    fig_divida_pib.update_layout(font = dict(color = "#D3D6DF"), margin=dict(l=24, r=45, t=31, b=23))
    
    fig_divida_pib.layout.plot_bgcolor = '#131516'
    fig_divida_pib.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    
    fig_divida_pib.update_xaxes(tickcolor = '#131516')
    fig_divida_pib.update_yaxes(tickcolor = '#131516')

    return fig_divida_pib