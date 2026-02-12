import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import utils
from utils import load_data, get_data_metadata
import os
from datetime import datetime, date
import calendar
import streamlit.components.v1 as components
import plotly.io as pio

# --- Page Config ---
st.set_page_config(
    page_title="Dashboard Contratos Gov",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for FinUI Styling ---
st.markdown("""
<style>
    /* FinUI Color Palette */
    :root {
        --primary-color: #4318FF;
        --secondary-color: #A3AED0;
        --text-color: #2B3674;
        --bg-color: #F4F7FE;
        --card-bg: #FFFFFF;
        --success-color: #05CD99;
    }

    /* Global Background */
    .stApp {
        background-color: var(--bg-color);
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Remove top padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--card-bg) !important;
        border-right: 1px solid #E0E5F2;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* Sidebar Headers */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--text-color);
    }
    
    /* Custom Cards (finui-card) */
    .finui-card {
        background-color: var(--card-bg);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0px 10px 20px rgba(112, 144, 176, 0.07);
        color: var(--text-color);
        margin-bottom: 20px;
        height: 100%;
        overflow: hidden;
    }
    
    .card-title {
        color: var(--secondary-color);
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 5px;
    }
    
    .card-value {
        color: var(--text-color);
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    
    .card-icon {
        background-color: var(--primary-color);
        color: #fff;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-bottom: 10px;
    }

    /* Specific Styles for Main Card */
    .main-card {
        background: linear-gradient(85deg, #4318FF 0%, #868CFF 100%);
        color: white;
    }
    .main-card .card-title { color: #E0E5F2; }
    .main-card .card-value { color: white; }
    .main-card .card-icon { background-color: rgba(255,255,255,0.2); }

    /* Active Filters Box */
    .active-filters-box {
        background-color: var(--card-bg);
        padding: 10px 20px;
        border-radius: 30px;
        font-size: 14px;
        color: var(--primary-color);
        font-weight: 500;
        display: inline-block;
        box-shadow: 0px 5px 10px rgba(112, 144, 176, 0.12);
        margin-bottom: 15px;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 0;
        color: var(--secondary-color);
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--primary-color);
        border-bottom: 2px solid var(--primary-color);
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

# Helper function to create metric cards
def metric_card(title, value, subtext=None, icon=None, is_main=False):
    card_class = "finui-card main-card" if is_main else "finui-card"
    icon_html = f"<div class='card-icon'>{icon}</div>" if icon else ""
    return f"""
    <div class="{card_class}">
        {icon_html}
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
        {'<div style="font-size:12px; color:var(--success-color); margin-top:5px;">' + subtext + '</div>' if subtext else ''}
    </div>
    """

# Helper function to render Chart INSIDE a Card (HTML Component)
def render_chart_within_card(fig, title, height_px=300):
    # Convert figure to HTML div string (including plotly.js via CDN for efficiency)
    fig_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
    
    # Custom HTML styling for the card wrapping the chart
    card_html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
        body {{ margin: 0; padding: 0; font-family: 'DM Sans', sans-serif; background-color: transparent; }}
        .finui-card {{
            background-color: #FFFFFF;
            border-radius: 20px;
            padding: 15px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
            box-sizing: border-box;
            height: {height_px}px;
            overflow: hidden;
        }}
        .card-title {{
            color: #A3AED0;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 5px;
            margin-left: 5px;
        }}
    </style>
    <div class="finui-card">
        <div class="card-title">{title}</div>
        <div style="width: 100%; height: 100%;">
            {fig_html}
        </div>
    </div>
    """
    # Render with Streamlit Components
    components.html(card_html, height=height_px, scrolling=False)

# --- Title ---
st.title("📊 Análise de Contratos")

# --- Load Data ---
df = load_data()
data_load_date = get_data_metadata()

if df.empty:
    st.error("Dados não encontrados.")
    st.stop()

# --- Session State Initialization ---
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

def reset_page():
    st.session_state.page_number = 1

def next_page():
    st.session_state.page_number += 1

def prev_page():
    st.session_state.page_number -= 1

# --- Sidebar Filters ---
st.sidebar.header("Filtros")

# 1. Ano Assinatura
years = sorted(df['ano_assinatura'].unique(), reverse=True)
selected_years = st.sidebar.multiselect("Ano de Assinatura", years, default=[], placeholder="Selecione o ano...", on_change=reset_page)

# 2. Situação Contrato
statuses = sorted(df['situacaoContrato'].astype(str).unique())
selected_statuses = st.sidebar.multiselect("Situação do Contrato", statuses, default=[], placeholder="Selecione a situação...", on_change=reset_page)

# 3. Modalidade Compra
modalities = sorted(df['modalidadeCompra'].astype(str).unique())
selected_modalities = st.sidebar.multiselect("Modalidade de Compra", modalities, placeholder="Selecione a modalidade...", on_change=reset_page)

# 4. UF Gestora
ufs = sorted(df['uf_gestora'].astype(str).unique())
selected_ufs = st.sidebar.multiselect("UF (Localização)", ufs, placeholder="Selecione a UF...", on_change=reset_page)

# 5. Tipo Contrato
types = sorted(df['tipo_contrato'].astype(str).unique())
selected_types = st.sidebar.multiselect("Tipo de Contrato", types, placeholder="Selecione o tipo...", on_change=reset_page)

# 6. Fornecedor (Searchable)
suppliers = sorted(df['nome_fornecedor'].astype(str).unique())
selected_suppliers = st.sidebar.multiselect("Fornecedor", suppliers, placeholder="Busque por fornecedor...", on_change=reset_page)

# 7. Datas (Ranges)
st.sidebar.markdown("---")
st.sidebar.markdown("**Filtros de Data**")

date_filters = {}
date_cols = {
    'dataAssinatura': 'Data Assinatura',
    'dataInicioVigencia': 'Início Vigência',
    'dataFimVigencia': 'Fim Vigência',
    'dataPublicacaoDOU': 'Publicação DOU'
}

# Calculate current month range
today = date.today()
last_day = calendar.monthrange(today.year, today.month)[1]
current_month_start = date(today.year, today.month, 1)
current_month_end = date(today.year, today.month, last_day)

for col, label in date_cols.items():
    if col in df.columns:
        min_date = df[col].min()
        max_date = df[col].max()
        
        # Determine default value
        default_val = [] # Blank by default
        if col == 'dataFimVigencia':
             default_val = (current_month_start, current_month_end)
        
        if pd.notnull(min_date) and pd.notnull(max_date):
            date_filters[col] = st.sidebar.date_input(
                f"{label}",
                value=default_val,
                min_value=min_date, # Still constraint the picker
                max_value=max_date,
                format="DD/MM/YYYY",
                on_change=reset_page
            )

# Apply Filters
filtered_df = df.copy()

if selected_years:
    filtered_df = filtered_df[filtered_df['ano_assinatura'].isin(selected_years)]

if selected_statuses:
    filtered_df = filtered_df[filtered_df['situacaoContrato'].isin(selected_statuses)]

if selected_modalities:
    filtered_df = filtered_df[filtered_df['modalidadeCompra'].isin(selected_modalities)]

if selected_ufs:
    filtered_df = filtered_df[filtered_df['uf_gestora'].isin(selected_ufs)]

if selected_types:
    filtered_df = filtered_df[filtered_df['tipo_contrato'].isin(selected_types)]

if selected_suppliers:
    filtered_df = filtered_df[filtered_df['nome_fornecedor'].isin(selected_suppliers)]

# Apply Date Filters
for col, dates in date_filters.items():
    if isinstance(dates, tuple) and len(dates) == 2:
        start_date, end_date = dates
        # Ensure we compare date to date (remove time component if present in df)
        filtered_df = filtered_df[
            (filtered_df[col].dt.date >= start_date) & 
            (filtered_df[col].dt.date <= end_date)
        ]

st.sidebar.text(f"Registros encontrados: {len(filtered_df)}")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Atualizado em:**\n{data_load_date}")


# --- Main Layout ---

# Active Filters Summary (Global)
active_filters = []
if selected_years: active_filters.append(f"Ano de Assinatura: {', '.join(map(str, selected_years))}")
if selected_statuses: active_filters.append(f"Situação do Contrato: {', '.join(selected_statuses)}")
if selected_modalities: active_filters.append(f"Modalidade de Compra: {', '.join(selected_modalities)}")
if selected_ufs: active_filters.append(f"UF (Localização): {', '.join(selected_ufs)}")
if selected_types: active_filters.append(f"Tipo de Contrato: {', '.join(selected_types)}")
if selected_suppliers: active_filters.append(f"Fornecedor: {len(selected_suppliers)} selecionado(s)")

# Date filters check
current_month_start = date(today.year, today.month, 1)
current_month_end = date(today.year, today.month, last_day)

for col, dates in date_filters.items():
    if isinstance(dates, tuple) and len(dates) == 2:
        start, end = dates
        if col == 'dataFimVigencia':
             active_filters.append(f"Fim Vigência: {start.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}")
        elif start != df[col].min().date() or end != df[col].max().date():
             active_filters.append(f"{date_cols[col]}: {start.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}")

# render active filters with new style
if active_filters:
    st.markdown(f"<div class='active-filters-box'>🔍 Filtros Ativos: {' | '.join(active_filters)}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='active-filters-box'>📋 Mostrando todos os registros (padrão vigência)</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Visão Geral", "Dados Detalhados"])

# --- Tab 1: Overview ---
with tab1:
    # KPIs Row - Grid Layout
    col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
    
    total_contratos = len(filtered_df)
    valor_total = filtered_df['valorInicialCompra'].sum()
    
    # Calculate % Goods vs Services if data exists
    if total_contratos > 0:
        bens_count = len(filtered_df[filtered_df['tipo_contrato'] == 'Aquisição de Bens'])
        servicos_count = len(filtered_df[filtered_df['tipo_contrato'] == 'Prestação de Serviços'])
        pct_bens = (bens_count / total_contratos) * 100
        pct_servicos = (servicos_count / total_contratos) * 100
    else:
        pct_bens = 0
        pct_servicos = 0

    with col1:
        st.markdown(metric_card("Valor Total (R$)", f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), icon="💰", is_main=True), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("Contratos", f"{total_contratos}", icon="📄"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("% Bens", f"{pct_bens:.1f}%", icon="📦"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card("% Serviços", f"{pct_servicos:.1f}%", icon="🛠️"), unsafe_allow_html=True)

    # Row 2: Charts (Side by Side) - Compact Height
    col_chart1, col_chart2 = st.columns(2)
    
    msg_no_data = "<div class='finui-card' style='display:flex;align-items:center;justify-content:center;height:260px;'>Sem dados.</div>"
    
    with col_chart1:
        if total_contratos > 0:
            fig_pie = px.pie(filtered_df, names='tipo_contrato', hole=0.6, 
                             color_discrete_sequence=['#4318FF', '#05CD99', '#EFF4FB'])
            # Tweak margins to fit card
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                  height=220, margin=dict(l=10, r=10, t=10, b=10),
                                  font=dict(family="DM Sans"),
                                  showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            render_chart_within_card(fig_pie, "Distribuição por Tipo", height_px=270)
        else:
            st.markdown(msg_no_data, unsafe_allow_html=True)

    with col_chart2:
        if total_contratos > 0:
            uf_counts = filtered_df['uf_gestora'].value_counts().reset_index().head(10)
            uf_counts.columns = ['UF', 'Contratos']
            fig_bar = px.bar(uf_counts, x='UF', y='Contratos', 
                             color_discrete_sequence=['#4318FF'])
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  height=220, margin=dict(l=10, r=10, t=10, b=10),
                                  font=dict(family="DM Sans"),
                                  xaxis_title=None, yaxis_title=None)
            render_chart_within_card(fig_bar, "Top 10 UFs", height_px=270)
        else:
            st.markdown(msg_no_data, unsafe_allow_html=True)
            
    # Row 3: Timeline (Card) - Global Evolution (Unfiltered)
    # Compact Height for Single Screen View
    if not df.empty:
        # Group by Year using the FULL dataframe (df)
        yearly_data = df['ano_assinatura'].value_counts().reset_index()
        yearly_data.columns = ['Ano', 'Qtd']
        yearly_data = yearly_data.sort_values('Ano')
        
        fig_area = px.area(yearly_data, x='Ano', y='Qtd', markers=True,
                           labels={'Ano': 'Ano', 'Qtd': 'Qtd'},
                           color_discrete_sequence=['#4318FF'],
                           text='Qtd') # Add labels
        
        fig_area.update_traces(textposition='top center') 
        fig_area.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               height=180, margin=dict(l=10, r=10, t=10, b=20),
                               font=dict(family="DM Sans"),
                               xaxis=dict(type='category'),
                               xaxis_title=None, yaxis_title=None)
                               
        render_chart_within_card(fig_area, "Evolução de Contratos (Histórico Completo)", height_px=220)

# --- Tab 2: Detailed Data (Pagination Optimized) ---
with tab2:
    # Header & Export Button
    col_header, col_spacer, col_export = st.columns([6, 3, 2])
    
    with col_header:
        st.subheader("Tabela de Contratos")
        
    with col_export:
        # Prepare Data for Export (WYSIWYG - Formatted Strings)
        export_df = filtered_df.copy()
        
        # Columns to swap (Raw -> Formatted)
        cols_to_swap = {
            'valorInicialCompra': 'valorInicialCompra_formatado',
            'valorFinalCompra': 'valorFinalCompra_formatado',
            'dataAssinatura': 'dataAssinatura_formatada',
            'dataInicioVigencia': 'dataInicioVigencia_formatada',
            'dataFimVigencia': 'dataFimVigencia_formatada',
            'dataPublicacaoDOU': 'dataPublicacaoDOU_formatada'
        }
        
        # Apply swap if formatted column exists
        for raw_col, fmt_col in cols_to_swap.items():
            if fmt_col in export_df.columns:
                export_df[raw_col] = export_df[fmt_col] # Overwrite with pre-formatted string
        
        # Drop internal formatting columns to avoid duplication
        cols_to_drop = [c for c in export_df.columns if c.endswith('_formatada') or c.endswith('_formatado')]
        export_df = export_df.drop(columns=cols_to_drop, errors='ignore')
        
        # Rename columns to match Dashboard UI (Friendly Names)
        column_renames = {
            'valorInicialCompra': 'Valor Inicial',
            'valorFinalCompra': 'Valor Final',
            'dataAssinatura': 'Data Assinatura',
            'dataInicioVigencia': 'Início Vigência',
            'dataFimVigencia': 'Fim Vigência',
            'dataPublicacaoDOU': 'Publicação DOU',
            'ano_assinatura': 'Ano Assinatura',
            'situacaoContrato': 'Situação',
            'modalidadeCompra': 'Modalidade',
            'uf_gestora': 'UF',
            'tipo_contrato': 'Tipo Contrato',
            'nome_fornecedor': 'Fornecedor',
            'objeto': 'Objeto'
        }
        export_df = export_df.rename(columns=column_renames)
        
        # Convert using Brazilian compatible format (semicolon + decimal comma logic handles by strings)
        # Using utf-8-sig for Excel compatibility
        csv = export_df.to_csv(index=False, sep=';').encode('utf-8-sig')
        
        st.download_button(
            label="📄 Exportar CSV (Formatado)",
            data=csv,
            file_name='contratos_formatados.csv',
            mime='text/csv',
            use_container_width=True
        )
    
    # Pagination - Default 13 rows to fit screen
    if total_contratos > 0:
        rows_per_page = 13 # Fixed number to fit 1080p
        total_pages = (total_contratos - 1) // rows_per_page + 1
        
        # Ensure page number is valid logic
        if st.session_state.page_number > total_pages:
            st.session_state.page_number = 1

        # Controls
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            st.button("⬅️ Anterior", on_click=prev_page, disabled=(st.session_state.page_number <= 1), use_container_width=True)
        
        with col_page:
            st.markdown(f"<div style='text-align: center; padding-top: 5px;'><b>Página {st.session_state.page_number} de {total_pages}</b></div>", unsafe_allow_html=True)
            
        with col_next:
            st.button("Próxima ➡️", on_click=next_page, disabled=(st.session_state.page_number >= total_pages), use_container_width=True)

        # Slice Data
        start_idx = (st.session_state.page_number - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        
        # Display Table - Optimized Height
        cols_to_hide = [c for c in filtered_df.columns if c.endswith('_formatada') or c.endswith('_formatado')]
        display_df = filtered_df.iloc[start_idx:end_idx].drop(columns=cols_to_hide, errors='ignore')

        column_config = {
            "valorInicialCompra": st.column_config.NumberColumn("Valor Inicial", format="R$ %.2f"),
             "valorFinalCompra": st.column_config.NumberColumn("Valor Final", format="R$ %.2f")
        }
        
        for col, label in date_cols.items():
            if col in display_df.columns:
                column_config[col] = st.column_config.DateColumn(label, format="DD/MM/YYYY")

        st.dataframe(
            display_df, 
            use_container_width=True,
            column_config=column_config,
            height=500 # Fixed table height
        )
    else:
        st.warning("Nenhum contrato encontrado.")
