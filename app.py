import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import streamlit as st
from sqlalchemy import create_engine, text, inspect
from datetime import date, timedelta


DATABASE_URL = st.secrets.get("DATABASE_URL")

st.set_page_config(
    page_title="Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

# Mantém a conexão aberta em cache (não recria a cada clique)
@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)

# Guarda o resultado da consulta em cache por 10 minutos (600 segundos)
@st.cache_data(ttl=600)
def carregar_dados():
    engine = create_engine(DATABASE_URL)
    df= pd.read_sql('SELECT * FROM registros', engine)
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    df["preco"] = pd.to_numeric(df["preco"])
    return df.sort_values("data_hora")

df = carregar_dados()
produtos = ["PS5 Slim Dig - 825Gb - S/Jogos","PS5 Slim Dig - 825Gb - Pct AstroBot+Gran", "PS5 Slim Dig 825Gb + GTA VI + AstroBot + Gran "]
df = df[df['produto'].isin(produtos)]

LINKS_MANUAIS = {
    "PS5 Slim Dig - 825Gb - S/Jogos": "https://www.amazon.com.br/Sony-PlayStation-Edição-Digital-Controle/dp/B0GWNKJDCZ/ref=sr_1_2?__mk_pt_BR=ÅMÅŽÕÑ&crid=3MQ5MI6DS8I6X&dib=eyJ2IjoiMSJ9.0TWYKganEp-3_8_Isg7DEBPhBv9oj7clyYGDf1WiySoVbw-6Mwov2k2bddyf4TafO05kF7aJCwUxJUmEsBRUHReUmkTtYja9vHr"
        "_H4dkETXX6k1CDVGAvW4iYkRImw1_eL_IcIwfNjKsKiEujNA24dPiT2vL69AqOuMsNjZu-eWsAJ1BvFDR0psMEmlUliroqQFKtDK0_I_bKreg_373l9Rkgkrz42nfvRzhmrmuwZTYsT9r6B74RvYqFPn3tYecAzR3lgxXzs4SG2_5YRefWnpabr_TQplM0Yg7Xiv_J70.otpCYdPPQ9HjUjafITXa0Xo1w6bQSoE4OSjO-xswLhs&dib_tag=se&keywords=sony+playstation+5+slim&qid=1795611934&sprefix=sony+playstation+5+slim+%2Caps%2C270&sr=8-2&ufe=app_do%3Aamzn1.fos.95de73c3-5dda-43a7-bd1f-63af03b14751",
    "PS5 Slim Dig - 825Gb - Pct AstroBot+Gran": "https://www.amazon.com.br/PlayStation®5-Slim-Digital-825GB-Turismo/dp/B0FPGF9J2J/ref=sr_1_2?brr=1&dib=eyJ2IjoiMSJ9._FCLhj9XU-hEdG3fD-U35DYTp2GQj492MqboULIQJI3KtyQI_aP48dVU73DoJkKQwKAUALOY_Sn3j1UKom9dj4PtnNVM0Tk16Ghh4l7b2_Fvc5NZ85Y6DvekuAV1PPo90O"
        "_e3l4jeAG6AG3ItkwN6GiIOrxYtNEkS5PHVtmsKMj06RfWL-Xdfhez6gIcAKZKS-3aN-78Lg6DdwLxmIjn38KNaA601Wu0OR_oKxxIBMY.JimE7O5nuuGTS8MmwU4rM8Vk8cvKbwCPJsGIjzrDpEk&dib_tag=se&qid=1795441523&rd=1&s=videogames&sr=1-2&ufe=app_do%3Aamzn1.fos.9e6a115c-05b9-4b96-8e1c-b1f9ce2ac1a6",
    "PS5 Slim Dig 825Gb + GTA VI + AstroBot + Gran ":  "https://www.amazon.com.br/Bundle-GTA-PlayStation-Slim-Digital/dp/B0H6LVH152/ref=sr_1_6?brr=1&dib=eyJ2IjoiMSJ9._FCLhj9XU-hEdG3fD-U35DYTp2GQj492MqboULIQJI3KtyQI_aP48dVU73DoJkKQwKAUALOY_Sn3j1UKom9dj4PtnNVM0Tk16Ghh4l7b2_Fvc5NZ85Y6DvekuAV1PPo90O_"
        "e3l4jeAG6AG3ItkwN6GiIOrxYtNEkS5PHVtmsKMj06RfWL-Xdfhez6gIcAKZKS-3aN-78Lg6DdwLxmIjn38KNaA601Wu0OR_oKxxIBMY.JimE7O5nuuGTS8MmwU4rM8Vk8cvKbwCPJsGIjzrDpEk&dib_tag=se&qid=1795444025&rd=1&s=videogames&sr=1-6"

}

st.subheader("Preços Atuais")

produtos = df["produto"].unique()
colunas = st.columns(len(produtos))

for idx, prod in enumerate(produtos):
    df_prod = df[df["produto"] == prod].sort_values("data_hora")
    preco_atual = df_prod["preco"].iloc[-1]
    
    # Calcula a diferença em relação ao registro imediatamente anterior
    if len(df_prod) > 1:
        preco_anterior = df_prod["preco"].iloc[-2]
        diferenca = preco_atual - preco_anterior
        delta_texto = f"R$ {diferenca:+.2f}" if diferenca != 0 else "Sem alteração"
        url_produto = LINKS_MANUAIS.get(prod)
    else:
        delta_texto = None

    with colunas[idx]:
        st.metric(
            label=prod,
            value=f"R$ {preco_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            delta=delta_texto,
            delta_color="inverse"  # Verde quando o preço cai, vermelho quando sobe
        )
        if url_produto:
                st.link_button("🔗 Ver oferta", url_produto, use_container_width=True)

st.divider()

# --- 2. GRÁFICO DE EVOLUÇÃO E DIFERENÇA POR DATA ---
st.subheader("Histórico de Variação por Data")

# Filtro opcional para selecionar produtos específicos
selecionados = st.multiselect(
    "Filtrar produtos no gráfico:",
    options=produtos,
    default=produtos
)

df_filtrado = df[df["produto"].isin(selecionados)]
df_filtrado["data"] = df_filtrado["data_hora"].dt.date
df_diario = df_filtrado.groupby(["data", "produto"], as_index=False)["preco"].min()

fig = px.line(
    df_diario,
    x="data",
    y="preco",
    color="produto",
    markers=True,
    labels={
        "data_hora": "Data e Hora",
        "preco": "Preço (R$)",
        "produto": "Produto"
    }
)

fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# --- 3. TABELA COM VARIAÇÃO CALCULADA ---
with st.expander("Ver tabela detalhada com variação de preço"):
    df_tabela = df_filtrado.copy()
    df_tabela["variacao_R$"] = df_tabela.groupby("produto")["preco"].diff()
    df_tabela["variacao_%"] = df_tabela.groupby("produto")["preco"].pct_change() * 100
    st.dataframe(df_tabela.sort_values("data_hora", ascending=False), use_container_width=True)