
#%% Carregando bibliotecas necessárias 

import pandas as pd
import streamlit as st
import plotly.express as px
import zipfile

#%% Definindo o layout da página

st.set_page_config(page_title='Análise de Imóveis', layout='wide')

st.title('📊 Dashboard de Imóveis - Real Estate')


#%% Carregando os dados 

@st.cache_data
def load_data():
    zip_path = 'Real_Estate_Tratado.zip'
    csv = 'Real_Estate_Tratado.csv'
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(csv) as f:
            df = pd.read_csv(f)
    
    df['Date Recorded'] = pd.to_datetime(df['Date Recorded'])
    df['year'] = df['Date Recorded'].dt.year
    df['month'] = df['Date Recorded'].dt.to_period('M').astype(str)
    df['gap values'] = df['Sale Amount'] - df['Assessed Value']
    df.drop('Unnamed: 0', axis=1, inplace=True)
    return df 
    
df = load_data()

#%% Configurando os filtros

st.sidebar.subheader('Filtros')

cidades = st.sidebar.multiselect('Cidade', df['Town'].unique())
anos = st.sidebar.slider("Ano de venda", int(df['year'].min()), int(df['year'].max()), (int(df['year'].min()), int(df['year'].max())))

#%% Aplicador dos filtros 

if not cidades:
    cidades = df['Town'].unique()

df_filtros = df[
        (df['Town'].isin(cidades)) &
        (df['year'].between(anos[0], anos[1]))
    ]

#%% KPIs 

st.markdown('---')

quantidade_vendida = len(df_filtros)
media_vendida = df_filtros['Sale Amount'].mean()
media_avaliado = df_filtros['Assessed Value'].mean()
diferencia_media = df_filtros['gap values'].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric('🏠 Quantidade de Imóveis Vendidos', f'{quantidade_vendida:,.0f}')
col2.metric('💰 Valor Médio Vendido', f'$ {media_vendida:,.0f}')
col3.metric('📉 Valor Médio Avaliado', f'$ {media_avaliado:,.0f}')
col4.metric('📊 Diferença média Vendido / Avaliado', f'$ {diferencia_media:,.0f}')

#%% Comparação por tipo de propriedade 

st.markdown('---')

st.subheader('🧱 Análise por Tipo de Propriedade')

col1, col2 = st.columns(2)

with col1:
    
    tipos = df_filtros['Property Type'].value_counts().reset_index()
    tipos.columns = ['Tipo', 'Quantidade']
    
    fig_pizza = px.pie(tipos,
                       names='Tipo',
                       values='Quantidade',
                       hole=0.4
                       )
    
    st.plotly_chart(fig_pizza, use_container_width=True)
    
with col2:
    
    fig_hist = px.histogram(
        df_filtros,
        x='Sale Amount',
        nbins=30,
        labels={'Sale Amount': 'Valor Vendido ($)', 'Property Type': 'Tipo do Imóvel'},
        color='Property Type',
        barmode='overlay',
        opacity=1
        )
    
    st.plotly_chart(fig_hist, use_container_width=True)
    

preco_propriedade = df_filtros.groupby('Property Type')[['Sale Amount', 'Assessed Value']].mean().reset_index()
preco_propriedade.columns = ['Tipo', 'Valor Médio de Venda', 'Valor Médio Avaliado']
    
preco_propriedade_melt = preco_propriedade.melt(id_vars = 'Tipo', value_vars =  ['Valor Médio de Venda', 'Valor Médio Avaliado'])
    
fig_barras = px.bar(
preco_propriedade_melt,
x='Tipo',
y='value',
color='variable',
barmode='group',
labels={'value': 'Valor ($)', 'tipo_propriedade': 'Tipo de Imóvel', 'variable': 'Tipo de Valor'},
)
    
st.plotly_chart(fig_barras, use_container_width=True)
    


#%% Evolução Temporal

st.markdown('---')

st.subheader('📆 Evolução de Preços ao Longo do Tempo')

evolucao_precos = df_filtros.groupby('month')[['Sale Amount', 'Assessed Value']].mean().reset_index()
evolucao_precos.columns = ['month', 'Valor Médio de Venda', 'Valor Médio Avaliado']

fig1 = px.line(evolucao_precos,
               x='month', y=['Valor Médio de Venda', 'Valor Médio Avaliado'],
               labels={'value': 'Valor ($)', 'month': 'Período', 'variable':'Tipo de Valor'}
               )

st.plotly_chart(fig1, use_container_width=True)




















