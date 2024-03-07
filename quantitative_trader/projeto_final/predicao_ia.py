import math
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from pandas_datareader import data as pdr
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler 
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
pd.options.mode.chained_assignment = None

# Cores da marca Cambirela
cor_primaria = '#EB7737'  # Verde Principal
cor_secundaria = '#FFFCF5'  # Creme



# Defina as datas de início e fim
end_date = datetime.now()
start_date = end_date - timedelta(days=1000)

ticker = ['USDBRL=X']

dados_acao = yf.download(ticker, start=start_date, end=end_date)

ultimo_ajuste = dados_acao['Adj Close'].tail(1)

cotacao = dados_acao['Adj Close'].to_numpy().reshape(-1, 1)

tamanho_dados_treinamento = int(len(cotacao) * 0.8)

#escalar os dados entre 0 e 1, para deixar mais fácil o processamento
escalador = MinMaxScaler(feature_range=(0, 1))
dados_entre_0_e_1_treinamento = escalador.fit_transform(cotacao[0: tamanho_dados_treinamento, :])
dados_entre_0_e_1_teste = escalador.transform(cotacao[tamanho_dados_treinamento: , :])
dados_entre_0_e_1 = list(dados_entre_0_e_1_treinamento.reshape(
    len(dados_entre_0_e_1_treinamento))) + list(dados_entre_0_e_1_teste.reshape(len(dados_entre_0_e_1_teste)))
dados_entre_0_e_1 = np.array(dados_entre_0_e_1).reshape(len(dados_entre_0_e_1), 1)


dados_para_treinamento = dados_entre_0_e_1[0: tamanho_dados_treinamento, :]
treinamento_x = []
treinamento_y = []
for i in range(60, len(dados_para_treinamento)):
    #60 ultimos dias
    treinamento_x.append(dados_para_treinamento[i - 60: i, 0])
    #cotacao
    treinamento_y.append(dados_para_treinamento[i, 0])
    if i <= 61:
        print('treinamento_x Concluido')
        print('treinamento_x Concluido')
        
        
        
treinamento_x, treinamento_y = np.array(treinamento_x), np.array(treinamento_y)
treinamento_x = treinamento_x.reshape(treinamento_x.shape[0], treinamento_x.shape[1], 1)

modelo = Sequential()
modelo.add(LSTM(50, return_sequences=True, input_shape = (treinamento_x.shape[1], 1)))
modelo.add(LSTM(50, return_sequences=False))
modelo.add(Dense(25))
modelo.add(Dense(1))

modelo.compile(optimizer="adam", loss="mean_squared_error") 


modelo.fit(treinamento_x, treinamento_y, batch_size=1, epochs=1)

dados_teste = dados_entre_0_e_1[tamanho_dados_treinamento - 60:, :]
teste_x = []
teste_y = cotacao[tamanho_dados_treinamento: , :] 
for i in range(60, len(dados_teste)):
    teste_x.append(dados_teste[i - 60: i, 0])
teste_x = np.array(teste_x)
teste_x = teste_x.reshape(teste_x.shape[0], teste_x.shape[1], 1)
predicoes = modelo.predict(teste_x)
predicoes = escalador.inverse_transform(predicoes)

rmse = np.sqrt(np.mean(predicoes - teste_y) ** 2)

treinamento = dados_acao.iloc[:tamanho_dados_treinamento, :]
df_teste = pd.DataFrame({"Adj Close": dados_acao['Adj Close'].iloc[tamanho_dados_treinamento:],
                        "predicoes": predicoes.reshape(len(predicoes))})
df_teste['predicoes'] = df_teste['predicoes'].shift(-1)


correlacao = df_teste['Adj Close'].corr(df_teste['predicoes'])

df_teste.sort_index()

df_teste['variacao_percentual_acao'] = df_teste['Adj Close'].pct_change()
df_teste['variacao_percentual_modelo'] = df_teste['predicoes'].pct_change()
df_teste = df_teste.dropna()
df_teste['var_acao_maior_menor_que_zero'] = np.where(df_teste['variacao_percentual_acao'] > 0, 
                                                      True, False)
df_teste['var_modelo_maior_menor_que_zero'] = np.where(df_teste['variacao_percentual_modelo'] > 0, 
                                                      True, False)
df_teste['acertou_o_lado'] = np.where(df_teste['var_acao_maior_menor_que_zero'] == df_teste['var_modelo_maior_menor_que_zero']
                                      , True, False)
df_teste['variacao_percentual_acao_abs'] = df_teste['variacao_percentual_acao'].abs()

valor_projetado = predicoes[-1][0]

# Converte o último ajuste para um número, para cálculo
ultimo_ajuste_numero = ultimo_ajuste.iloc[0]

# Calcula a variação percentual projetada
var_perc_projetado = (valor_projetado - ultimo_ajuste_numero) / ultimo_ajuste_numero * 100

# Verifica a direção do mercado baseado na variação percentual projetada
direcao_mercado = "Pregão de Alta" if var_perc_projetado > 0 else "Pregão de Baixa"


#_____________________________________________________________________________________________________________________

fig_predicao = go.Figure()
fig_predicao.add_trace(go.Scatter(x=treinamento.index, y=treinamento['Adj Close'], mode='lines', name='Treinamento', line=dict(color=cor_primaria)))
fig_predicao.add_trace(go.Scatter(x=df_teste.index, y=df_teste['Adj Close'], mode='lines', name='Adj Close', line=dict(color='#1F4741')))
fig_predicao.add_trace(go.Scatter(x=df_teste.index, y=df_teste['predicoes'], mode='lines', name='Predições', line=dict(color='#49e2b1')))
fig_predicao.update_layout(
    title='.                          Modelo de Previsão de Preço - Rede Neural',
    xaxis_title='Data',
    yaxis_title='Preço de Fechamento',
    plot_bgcolor=cor_secundaria,
    paper_bgcolor=cor_secundaria,
    font=dict(family='Arial', size=12, color=cor_primaria),
    legend=dict(bgcolor=cor_secundaria, font=dict(size=12, color=cor_primaria)),
    yaxis=dict(tickformat=".3f")  # Formatando o eixo Y com 3 casas decimais
)
fig_predicao.add_vline(x=treinamento.index[-1], line_width=2, line_dash="dash", line_color="#2B6960")
fig_predicao.add_layout_image(
    dict(
        source="https://i.imgur.com/ZE3asBY.png",  # Substitua com a URL do seu logotipo
        xref="paper", yref="paper",
        x=0.08, y=1.05,  # Ajuste essas coordenadas conforme necessário
        sizex=0.2, sizey=0.2,  # Ajuste o tamanho conforme necessário
        xanchor="right", yanchor="bottom"
    )
)
fig_predicao.add_hline(y=valor_projetado, line_width=2, line_dash="dash", line_color="#2B6960")
fig_predicao.add_annotation(
    xref="paper", yref="y",
    x=1, y=valor_projetado,
    text=f"Valor Projetado: {valor_projetado:.3f}",
    showarrow=True,
    arrowhead=1
)


#fig_predicao.show()






print(f'''
Relatório de Modelo LSTM para Previsão de Preços de Ativos em Séries Temporais

1. Ativo Analisado: {ticker}
2. Período de Análise: De {start_date.date()} até {end_date.date()}
3. Total de Dados: {len(cotacao)} preços de fechamento
4. Treinamento e Teste:
   - Dados para Treinamento: {tamanho_dados_treinamento} dias (80% dos dados)
   - Dados para Teste: {len(cotacao) - tamanho_dados_treinamento} dias (20% dos dados)
5. Estrutura do Modelo LSTM:
   - Primeira camada LSTM: 50 neurônios
   - Segunda camada LSTM: 50 neurônios
   - Camadas Densas: 25 e 1 neurônio(s)
6. Desempenho do Modelo:
   - RMSE nos Dados de Teste: {rmse:.4f}
   - Correlação entre Dados Reais e Previsões: {correlacao:.4f}
7. Previsão para a Data Mais Recente ({end_date.date()}):
    A direção projetada é: {direcao_mercado}))
''')