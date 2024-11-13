import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest

# Carregando os dados
df2 = pd.read_csv('df2.csv')

# Filtrando os dados para clientes sem medições negativas
df_positivos = df2[df2['tem_negativos'] == False]

# Filtrando os dados para clientes com medições negativas
df_negativos = df2[df2['tem_negativos'] == True]

# Ordenando os condomínios em ordem crescente
df_positivos = df_positivos.sort_values(by='C_condCode')
df_negativos = df_negativos.sort_values(by='C_condCode')

# Interface do Streamlit
st.set_page_config(page_title="Análise de Consumo e Anomalias", layout="wide")
st.title("🔍 Análise de Consumo e Detecção de Anomalias")

# Criação de abas para separar zonas
tab1, tab2, tab3 = st.tabs(["📊 Comparação de Condomínios", "🔍 Análise Detalhada por Cliente", "⚠️ Condomínios com Medições Negativas"])

# ========================= ZONA 1: COMPARAÇÃO ENTRE CONDOMÍNIOS ========================= #
with tab1:
    st.header("📈 Comparação de Consumo Médio Entre Condomínios")

    # Agrupando por condomínio e calculando a média de consumo
    consumo_condominios = df_positivos.groupby('C_condCode')['measure_avg_consumption'].mean().reset_index()

    # Gráfico de comparação de consumo entre condomínios
    fig_condominios = px.bar(
        consumo_condominios,
        x='C_condCode',
        y='measure_avg_consumption',
        title="🌐 Consumo Médio por Condomínio",
        labels={'C_condCode': 'Código do Condomínio', 'measure_avg_consumption': 'Consumo Médio (M³/s)'},
        template='plotly_white',
        color='measure_avg_consumption',
        color_continuous_scale=px.colors.sequential.Viridis
    )

    # Exibir o gráfico de comparação entre condomínios
    st.plotly_chart(fig_condominios)

# ========================= ZONA 2: ANÁLISE DETALHADA POR CLIENTE ========================= #
with tab2:
    st.header("📊 Análise Detalhada por Condomínio e Cliente (Sem Medições Negativas)")

    # Selecionando o condomínio
    condominio_selecionado = st.selectbox('🏢 Escolha um Condomínio (C_condCode):', sorted(df_positivos['C_condCode'].unique()))

    # Filtrando os clientes do condomínio selecionado
    clientes_condominio = df_positivos[df_positivos['C_condCode'] == condominio_selecionado]

    # Selecionando o cliente
    cliente_selecionado = st.selectbox('👤 Escolha um Cliente (C_clientCode):', clientes_condominio['C_clientCode'].unique())

    # Filtrando os dados do cliente selecionado
    dados_cliente = clientes_condominio[clientes_condominio['C_clientCode'] == cliente_selecionado]

    # Preparando os dados para o Isolation Forest
    X_condominio = clientes_condominio[['measure_avg_consumption']]

    # Treinando o modelo Isolation Forest para detectar anomalias
    model_iforest = IsolationForest(contamination=0.05, random_state=42)
    anomalias_pred = model_iforest.fit_predict(X_condominio)

    # Adicionando a coluna de anomalia
    clientes_condominio['anomaly'] = anomalias_pred
    clientes_condominio['anomaly'] = clientes_condominio['anomaly'].apply(lambda x: 'Anomalia' if x == -1 else 'Normal')

    # Verificando o status do cliente selecionado
    cliente_anomaly_status = clientes_condominio[clientes_condominio['C_clientCode'] == cliente_selecionado]['anomaly'].values[0]

    # Exibir o status de anomalia no Streamlit
    st.subheader(f"📌 Status do Cliente {cliente_selecionado}: {cliente_anomaly_status}")

    # Gráfico interativo mostrando todos os clientes do condomínio, destacando o cliente selecionado e anomalias
    st.subheader(f"📈 Comparação do Cliente {cliente_selecionado} com os Demais do Condomínio {condominio_selecionado}")

    # Plotting using Plotly with a cleaner design
    fig = go.Figure()

    # Adicionando os clientes normais
    fig.add_trace(go.Scatter(
        x=clientes_condominio[clientes_condominio['anomaly'] == 'Normal']['C_clientCode'],
        y=clientes_condominio[clientes_condominio['anomaly'] == 'Normal']['measure_avg_consumption'],
        mode='markers',
        name='Normal',
        marker=dict(color='blue', size=8),
        text=clientes_condominio[clientes_condominio['anomaly'] == 'Normal']['C_clientCode'],
        hovertemplate="<b>Cliente</b>: %{text}<br><b>Consumo</b>: %{y}<extra></extra>"
    ))

    # Adicionando as anomalias
    fig.add_trace(go.Scatter(
        x=clientes_condominio[clientes_condominio['anomaly'] == 'Anomalia']['C_clientCode'],
        y=clientes_condominio[clientes_condominio['anomaly'] == 'Anomalia']['measure_avg_consumption'],
        mode='markers',
        name='Anomalia',
        marker=dict(color='orange', size=10, symbol='diamond-tall-open-dot'),
        text=clientes_condominio[clientes_condominio['anomaly'] == 'Anomalia']['C_clientCode'],
        hovertemplate="<b>Cliente</b>: %{text}<br><b>Consumo</b>: %{y}<extra></extra>"
    ))

    # Adicionando o cliente selecionado
    fig.add_trace(go.Scatter(
        x=dados_cliente['C_clientCode'],
        y=dados_cliente['measure_avg_consumption'],
        mode='markers',
        name=f'Cliente Selecionado ({cliente_selecionado})',
        marker=dict(color='red', size=15, symbol='star-diamond'),
        text=dados_cliente['C_clientCode'],
        hovertemplate="<b>Cliente Selecionado</b>: %{text}<br><b>Consumo</b>: %{y}<extra></extra>"
    ))

    # Layout do gráfico
    fig.update_layout(
    title=f"🌟 Consumo Médio no Condomínio {condominio_selecionado}",
    xaxis_title="Código do Cliente",
    yaxis_title="Medição Média de Consumo",
    template='plotly_white',
    legend=dict(
        title="Legenda",
        title_font=dict(size=14, color="black"),  # Tamanho e cor do título da legenda
        font=dict(size=12, color="black"),  # Tamanho e cor do texto da legenda
        bgcolor="rgba(255, 255, 255, 0.8)",  # Fundo com um pouco mais de opacidade
        bordercolor="black",  # Cor da borda
        borderwidth=2,  # Largura da borda
        x=0.9, y=1.1,
        xanchor="right",  # Ancorar à direita
        yanchor="bottom",  # Ancorar na parte inferior
    ),
    hovermode="closest"
    )


    # Exibir o gráfico interativo no Streamlit
    st.plotly_chart(fig)

    # Exibindo os dados detalhados do cliente
    st.subheader(f"📋 Detalhes do Cliente {cliente_selecionado}:")
    st.write(dados_cliente)

# ========================= ZONA 3: ANÁLISE DE CONDOMÍNIOS COM MEDIÇÕES NEGATIVAS ========================= #
with tab3:
    st.header("⚠️ Análise de Condomínios com Medições Negativas")

    # Selecionando o condomínio
    condominio_negativo_selecionado = st.selectbox('🏢 Escolha um Condomínio (C_condCode):', sorted(df_negativos['C_condCode'].unique()))

    # Filtrando os clientes do condomínio selecionado
    clientes_negativos_condominio = df_negativos[df_negativos['C_condCode'] == condominio_negativo_selecionado]

    # Selecionando o cliente
    cliente_negativo_selecionado = st.selectbox('👤 Escolha um Cliente (C_clientCode):', clientes_negativos_condominio['C_clientCode'].unique())

    # Filtrando os dados do cliente selecionado
    dados_negativos_cliente = clientes_negativos_condominio[clientes_negativos_condominio['C_clientCode'] == cliente_negativo_selecionado]

    # Preparando os dados para o Isolation Forest
    X_condominio_negativo = clientes_negativos_condominio[['measure_avg_consumption']]

    # Treinando o modelo Isolation Forest para detectar anomalias
    model_iforest_negativo = IsolationForest(contamination=0.05, random_state=42)
    anomalias_pred_negativo = model_iforest_negativo.fit_predict(X_condominio_negativo)

    # Adicionando a coluna de anomalia
    clientes_negativos_condominio['anomaly'] = anomalias_pred_negativo
    clientes_negativos_condominio['anomaly'] = clientes_negativos_condominio['anomaly'].apply(lambda x: 'Anomalia' if x == -1 else 'Normal')

    # Verificando o status do cliente selecionado
    cliente_negativo_anomaly_status = clientes_negativos_condominio[clientes_negativos_condominio['C_clientCode'] == cliente_negativo_selecionado]['anomaly'].values[0]

    # Exibir o status de anomalia no Streamlit
    st.subheader(f"📌 Status do Cliente {cliente_negativo_selecionado}: {cliente_negativo_anomaly_status}")

    # Gráfico interativo mostrando todos os clientes do condomínio, destacando o cliente selecionado e anomalias
    st.subheader(f"📈 Comparação do Cliente {cliente_negativo_selecionado} com os Demais do Condomínio {condominio_negativo_selecionado}")

    # Plotting using Plotly with a cleaner design
    fig_negativo = go.Figure()

    # Adicionando os clientes normais
    fig_negativo.add_trace(go.Scatter(
        x=clientes_negativos_condominio[clientes_negativos_condominio['anomaly'] == 'Normal']['C_clientCode'],
        y=clientes_negativos_condominio[clientes_negativos_condominio['anomaly'] == 'Normal']['measure_avg_consumption'],
        mode='markers',
        name='Normal',
        marker=dict(color='blue', size=8),
        text=clientes_negativos_condominio[clientes_negativos_condominio['anomaly'] == 'Normal']['C_clientCode'],
        hovertemplate="<b>Cliente</b>: %{text}<br><b>Consumo</b>: %{y}<extra></extra>"
    ))

    # Adicionando as anomalias
    fig_negativo.add_trace(go.Scatter(
        x=clientes_negativos_condominio[clientes_negativos_condominio['anomaly'] == 'Anomalia']['C_clientCode'],
        y=clientes_negativos_condominio[clientes_negativos_condominio['anomaly'] == 'Anomalia']['measure_avg_consumption'],
        mode='markers',
        name='Anomalia',
        marker=dict(color='orange', size=10, symbol='diamond-tall-open-dot'),
        text=clientes_negativos_condominio[clientes_negativos_condominio['anomaly'] == 'Anomalia']['C_clientCode'],
        hovertemplate="<b>Cliente</b>: %{text}<br><b>Consumo</b>: %{y}<extra></extra>"
    ))

    # Adicionando o cliente selecionado
    fig_negativo.add_trace(go.Scatter(
        x=dados_negativos_cliente['C_clientCode'],
        y=dados_negativos_cliente['measure_avg_consumption'],
        mode='markers',
        name=f'Cliente Selecionado ({cliente_negativo_selecionado})',
        marker=dict(color='red', size=15, symbol='star-diamond'),
        text=dados_negativos_cliente['C_clientCode'],
        hovertemplate="<b>Cliente Selecionado</b>: %{text}<br><b>Consumo</b>: %{y}<extra></extra>"
    ))

    # Layout do gráfico
    fig_negativo.update_layout(
    title=f"🌟 Consumo Médio no Condomínio {condominio_negativo_selecionado}",
    xaxis_title="Código do Cliente",
    yaxis_title="Medição Média de Consumo",
    template='plotly_white',
    legend=dict(
        title="Legenda",
        title_font=dict(size=14, color="black"),  # Tamanho e cor do título da legenda
        font=dict(size=12, color="black"),  # Tamanho e cor do texto da legenda
        bgcolor="rgba(255, 255, 255, 0.8)",  # Fundo com um pouco mais de opacidade
        bordercolor="black",  # Cor da borda
        borderwidth=2,  # Largura da borda
        x=0.9, y=1.1,
        xanchor="right",  # Ancorar à direita
        yanchor="bottom",  # Ancorar na parte inferior
    ),
    hovermode="closest"
    )


    # Exibir o gráfico interativo no Streamlit
    st.plotly_chart(fig_negativo)

    # Exibindo os dados detalhados do cliente
    st.subheader(f"📋 Detalhes do Cliente {cliente_negativo_selecionado}:")
    st.write(dados_negativos_cliente)
