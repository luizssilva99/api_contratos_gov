import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data
import os

# Page Config
st.set_page_config(
    page_title="Dashboard Contratos Gov",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .reportview-container {
        background: #ffffff;
    }
    .sidebar .sidebar-content {
        background: #f0f2f6;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stMetric {
        background-color: #f0f8ff;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #d1e8ff;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Análise de Contratos - Portal da Transparência")
st.markdown("---")

# Load Data
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.tmp', 'contratos_20701.csv')

if not os.path.exists(DATA_PATH):
    st.error(f"Arquivo de dados não encontrado em: {DATA_PATH}")
    st.info("Execute 'python3 execution/extract_contratos.py' para gerar os dados.")
    st.stop()

df = load_data(DATA_PATH)

if df.empty:
    st.warning("O arquivo CSV está vazio ou não pôde ser lido.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filtros")

# Filter by Year
if 'ano_assinatura' in df.columns:
    years = sorted(df['ano_assinatura'].dropna().astype(int).unique(), reverse=True)
    selected_years = st.sidebar.multiselect("Ano de Assinatura", years, default=years[:1] if years else None) 
else:
    selected_years = []

# Filter by Status (situacaoCompra) if available
if 'situacaoCompra' in df.columns:
    statuses = sorted(df['situacaoCompra'].dropna().unique())
    selected_statuses = st.sidebar.multiselect("Situação", statuses, default=statuses)
else:
    selected_statuses = []

# Apply Filters
filtered_df = df.copy()

if selected_years:
    filtered_df = filtered_df[filtered_df['ano_assinatura'].isin(selected_years)]

if selected_statuses and 'situacaoCompra' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['situacaoCompra'].isin(selected_statuses)]

# KPIs
col1, col2, col3 = st.columns(3)

total_contratos = len(filtered_df)
valor_total = filtered_df['valorInicialCompra'].sum()

# Top Supplier
top_supplier = "N/A"
if 'nome_fornecedor' in filtered_df.columns and not filtered_df.empty:
    top_supplier = filtered_df['nome_fornecedor'].mode()[0] if not filtered_df['nome_fornecedor'].mode().empty else "N/A"

col1.metric("Total de Contratos", f"{total_contratos}")
col2.metric("Valor Total Inicial", f"R$ {valor_total:,.2f}")
col3.metric("Principal Fornecedor (Qtd)", top_supplier)

st.markdown("---")

# Charts Layout
col_chart1, col_chart2 = st.columns(2)

# Chart 1: Contracts by Month/Year
with col_chart1:
    st.subheader("Contratos ao Longo do Tempo")
    if 'dataAssinatura' in filtered_df.columns and not filtered_df.empty:
        # Group by month
        monthly_counts = filtered_df.groupby(filtered_df['dataAssinatura'].dt.to_period("M")).size().reset_index(name='Contagem')
        monthly_counts['dataAssinatura'] = monthly_counts['dataAssinatura'].astype(str)
        
        fig_time = px.bar(monthly_counts, x='dataAssinatura', y='Contagem', 
                          title="Quantidade de Contratos por Mês",
                          labels={'dataAssinatura': 'Mês/Ano', 'Contagem': 'Qtd Contratos'},
                          color_discrete_sequence=['#3498db'])
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("Dados de data não disponíveis para gráfico temporal.")

# Chart 2: Top 10 Suppliers by Value
with col_chart2:
    st.subheader("Top 10 Fornecedores por Valor")
    if 'nome_fornecedor' in filtered_df.columns and 'valorInicialCompra' in filtered_df.columns and not filtered_df.empty:
        top_suppliers = filtered_df.groupby('nome_fornecedor')['valorInicialCompra'].sum().nlargest(10).reset_index()
        fig_suppliers = px.bar(top_suppliers, x='valorInicialCompra', y='nome_fornecedor', orientation='h',
                               title="Top 10 Fornecedores (Valor Total)",
                               labels={'valorInicialCompra': 'Valor Total (R$)', 'nome_fornecedor': 'Fornecedor'},
                               color_discrete_sequence=['#2 ecc71'])
        fig_suppliers.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_suppliers, use_container_width=True)
    else:
        st.info("Dados de fornecedor ou valor não disponíveis.")

# Detailed Data Table
st.markdown("### Detalhes dos Contratos")
st.dataframe(filtered_df)

# Download Button
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Baixar Dados Filtrados (CSV)",
    data=csv,
    file_name='contratos_filtrados.csv',
    mime='text/csv',
)
