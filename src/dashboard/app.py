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
    page_title="GovAnalytics - Análise de Contratos",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for GovAnalytics Mockup ---
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Color Palette - GovAnalytics */
    :root {
        --primary: #2563EB;
        --primary-light: #E8F0FE;
        --primary-dark: #1D4ED8;
        --text-dark: #1E293B;
        --text-secondary: #64748B;
        --text-muted: #94A3B8;
        --bg-main: #F8FAFC;
        --card-bg: #FFFFFF;
        --border-color: #E2E8F0;
        --success: #16A34A;
        --success-bg: #DCFCE7;
        --warning: #F59E0B;
        --warning-bg: #FEF9C3;
        --danger: #DC2626;
        --danger-bg: #FEE2E2;
        --info: #2563EB;
        --info-bg: #DBEAFE;
    }

    /* Global */
    .stApp {
        background-color: var(--bg-main);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ====== SIDEBAR ====== */
    section[data-testid="stSidebar"] {
        background-color: var(--card-bg) !important;
        border-right: 1px solid var(--border-color);
        width: 260px !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
    }

    /* Sidebar logo area */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0 24px 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }
    .sidebar-logo-icon {
        background: var(--primary);
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
    }
    .sidebar-logo-text {
        font-size: 16px;
        font-weight: 700;
        color: var(--primary);
    }

    /* Sidebar section labels */
    .sidebar-section {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 16px;
        margin-bottom: 8px;
    }

    /* Sidebar filter label */
    .sidebar-filter-label {
        font-size: 13px;
        font-weight: 500;
        color: var(--text-dark);
        margin-bottom: 4px;
    }

    /* Sidebar status chips */
    .status-chips {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
    }
    .status-chip {
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        border: 1px solid var(--border-color);
        color: var(--text-secondary);
        background: var(--card-bg);
        cursor: pointer;
    }
    .status-chip.active {
        background: var(--primary-light);
        color: var(--primary);
        border-color: var(--primary);
    }

    /* Sidebar footer */
    .sidebar-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 260px;
        padding: 12px 20px;
        border-top: 1px solid var(--border-color);
        background: var(--card-bg);
        font-size: 12px;
        color: var(--text-secondary);
    }
    .sidebar-footer-item {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 4px;
    }
    .sidebar-footer-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--primary);
        display: inline-block;
    }
    .sidebar-footer-dot.green {
        background: var(--success);
    }

    /* ====== HEADER ====== */
    .gov-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0;
        margin-bottom: 8px;
    }
    .gov-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .gov-header-icon {
        font-size: 24px;
    }
    .gov-header-title {
        font-size: 22px;
        font-weight: 700;
        color: var(--text-dark);
    }
    .gov-header-right {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .gov-header-bell {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--bg-main);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        cursor: pointer;
    }
    .gov-header-profile {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .gov-header-profile-info {
        text-align: right;
    }
    .gov-header-profile-name {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-dark);
    }
    .gov-header-profile-role {
        font-size: 11px;
        color: var(--text-muted);
    }
    .gov-header-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--primary);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 600;
    }

    /* ====== ACTIVE FILTERS BAR ====== */
    .filters-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        background: var(--card-bg);
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin-bottom: 16px;
        flex-wrap: wrap;
    }
    .filters-bar-icon {
        font-size: 14px;
        color: var(--text-muted);
        margin-right: 4px;
    }
    .filters-bar-label {
        font-size: 13px;
        color: var(--text-secondary);
        font-weight: 500;
        white-space: nowrap;
    }
    .filter-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        background: var(--primary-light);
        color: var(--primary);
    }
    .filter-chip .chip-x {
        font-size: 14px;
        cursor: pointer;
        opacity: 0.7;
    }
    .clear-all-link {
        font-size: 12px;
        color: var(--text-muted);
        text-decoration: underline;
        margin-left: auto;
        cursor: pointer;
    }

    /* ====== TABS ====== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 0;
        color: var(--text-muted);
        font-weight: 500;
        font-size: 14px;
        padding: 10px 20px;
        border-bottom: 2px solid transparent;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary) !important;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 0;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: var(--primary) !important;
    }

    /* ====== KPI CARDS ====== */
    .kpi-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid var(--border-color);
        position: relative;
        min-height: 130px;
    }
    .kpi-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .kpi-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: var(--primary-light);
        color: var(--primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .kpi-badge {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        background: var(--success-bg);
        color: var(--success);
    }
    .kpi-label {
        font-size: 13px;
        color: var(--text-muted);
        font-weight: 500;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 700;
        color: var(--text-dark);
        line-height: 1.2;
        word-wrap: break-word;
    }
    .kpi-bar {
        height: 4px;
        border-radius: 2px;
        background: var(--border-color);
        margin-top: 12px;
        overflow: hidden;
    }
    .kpi-bar-fill {
        height: 100%;
        border-radius: 2px;
        background: var(--primary);
    }

    /* ====== CHART CARDS ====== */
    .chart-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid var(--border-color);
        margin-bottom: 20px;
    }
    .chart-card-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 16px;
    }

    /* ====== TABLE SECTION ====== */
    .table-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }
    .table-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-dark);
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-align: center;
    }
    .status-ativo { background: var(--success-bg); color: var(--success); }
    .status-execucao { background: var(--info-bg); color: var(--info); }
    .status-concluido { background: #F1F5F9; color: var(--text-secondary); }
    .status-suspenso { background: var(--danger-bg); color: var(--danger); }
    .status-default { background: var(--warning-bg); color: var(--warning); }

    /* Pagination */
    .pagination-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        border-top: 1px solid var(--border-color);
        margin-top: 8px;
    }
    .pagination-btn {
        font-size: 13px;
        color: var(--text-secondary);
        font-weight: 500;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .pagination-btn:hover { color: var(--primary); }
    .pagination-info {
        font-size: 13px;
        color: var(--text-secondary);
    }

    /* Export button override */
    .stDownloadButton > button {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 8px 20px !important;
    }
    .stDownloadButton > button:hover {
        background: var(--primary-dark) !important;
    }

    /* Selectbox styling */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label {
        font-size: 13px !important;
        font-weight: 500 !important;
        color: var(--text-dark) !important;
    }

    /* Streamlit elements fine tune */
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"],
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
        border-radius: 10px !important;
        border-color: var(--border-color) !important;
        font-size: 13px !important;
    }

    [data-testid="stSidebar"] .stDateInput input {
        border-radius: 10px !important;
        border-color: var(--border-color) !important;
        font-size: 13px !important;
    }

    /* Dataframe override */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-color);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Button overrides */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        border-color: var(--border-color) !important;
    }

    /* Remove streamlit extra spacing */
    .element-container { margin-bottom: 0 !important; }
    .stMarkdown { margin-bottom: 0 !important; }

    /* Sidebar divider override */
    [data-testid="stSidebar"] hr {
        border-color: var(--border-color);
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper function: Render chart inside styled card ---
def render_chart_within_card(fig, title, height_px=300):
    fig_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
    card_html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body {{ margin: 0; padding: 0; font-family: 'Inter', sans-serif; background-color: transparent; }}
        .chart-card {{
            background-color: #FFFFFF;
            border-radius: 16px;
            padding: 20px;
            border: 1px solid #E2E8F0;
            box-sizing: border-box;
            min-height: {height_px - 20}px;
            overflow: visible;
        }}
        .chart-card-title {{
            font-size: 15px;
            font-weight: 600;
            color: #1E293B;
            margin-bottom: 12px;
        }}
    </style>
    <div class="chart-card">
        <div class="chart-card-title">{title}</div>
        <div style="width: 100%; height: 100%;">
            {fig_html}
        </div>
    </div>
    """
    components.html(card_html, height=height_px, scrolling=False)


# --- Helper: KPI Card via components.html ---
def render_kpi_card(title, value, icon, badge=None, badge_type='positive', bar_pct=None):
    badge_html = f'<div class="kpi-badge {badge_type}">{badge}</div>' if badge else ''
    bar_html = ''
    if bar_pct is not None:
        bar_html = f'<div class="kpi-bar"><div class="kpi-bar-fill" style="width:{bar_pct}%"></div></div>'
    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body {{ margin: 0; padding: 0; font-family: 'Inter', sans-serif; background-color: transparent; }}
        .kpi-card {{
            background: #FFFFFF;
            border-radius: 16px;
            padding: 20px;
            border: 1px solid #E2E8F0;
            min-height: 110px;
            box-sizing: border-box;
        }}
        .kpi-header {{ display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px; }}
        .kpi-icon {{
            width: 42px; height: 42px; border-radius: 12px;
            background: #E8F0FE; color: #2563EB;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px;
        }}
        .kpi-badge {{
            display: inline-flex; align-items: center;
            padding: 2px 8px; border-radius: 12px;
            font-size: 11px; font-weight: 600;
        }}
        .kpi-badge.positive {{ background: #DCFCE7; color: #16A34A; }}
        .kpi-badge.negative {{ background: #FEE2E2; color: #DC2626; }}
        .kpi-badge.neutral {{ background: #F1F5F9; color: #64748B; }}
        .kpi-label {{ font-size: 13px; color: #94A3B8; font-weight: 500; margin-bottom: 4px; }}
        .kpi-value {{ font-size: 22px; font-weight: 700; color: #1E293B; line-height: 1.2; word-wrap: break-word; }}
        .kpi-bar {{ height: 4px; border-radius: 2px; background: #E2E8F0; margin-top: 12px; overflow: hidden; }}
        .kpi-bar-fill {{ height: 100%; border-radius: 2px; background: #2563EB; }}
    </style>
    <div class="kpi-card">
        <div class="kpi-header">
            <div class="kpi-icon">{icon}</div>
            {badge_html}
        </div>
        <div class="kpi-label">{title}</div>
        <div class="kpi-value">{value}</div>
        {bar_html}
    </div>
    """
    components.html(html, height=160, scrolling=False)


# --- Header ---
st.markdown("""
<div class="gov-header">
    <div class="gov-header-left">
        <span style="font-size:22px;">🏛️</span>
        <span class="gov-header-title">Análise de Contratos</span>
    </div>
    <div class="gov-header-right">
        <div class="gov-header-bell">🔔</div>
        <div class="gov-header-profile">
            <div class="gov-header-profile-info">
                <div class="gov-header-profile-name">Admin Gov</div>
                <div class="gov-header-profile-role">Sinfra-MT</div>
            </div>
            <div class="gov-header-avatar">AG</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- Load Data ---
df = load_data()
data_load_date = get_data_metadata()

if df.empty:
    st.error("Dados não encontrados.")
    st.stop()

# --- Session State ---
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

def reset_page():
    st.session_state.page_number = 1

def next_page():
    st.session_state.page_number += 1

def prev_page():
    st.session_state.page_number -= 1


# --- Sidebar ---
# Logo
st.sidebar.markdown("""
<div class="sidebar-logo">
    <div class="sidebar-logo-icon">🏛️</div>
    <div class="sidebar-logo-text">GovAnalytics</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-section">FILTROS</div>', unsafe_allow_html=True)

# Categoria (maps to tipo_contrato)
types = sorted(df['tipo_contrato'].astype(str).unique())
all_types_option = "Todos os Serviços"
type_options = [all_types_option] + types
selected_type_sidebar = st.sidebar.selectbox("Categoria", type_options, index=0, on_change=reset_page)
selected_types = [] if selected_type_sidebar == all_types_option else [selected_type_sidebar]

# Departamento (maps to modalidadeCompra)
modalities = sorted(df['modalidadeCompra'].astype(str).unique())
selected_modality_sidebar = st.sidebar.selectbox("Departamento", ["Todos"] + modalities, index=0, on_change=reset_page)
selected_modalities = [] if selected_modality_sidebar == "Todos" else [selected_modality_sidebar]

# Status (maps to situacaoContrato)
statuses = sorted(df['situacaoContrato'].astype(str).unique())
selected_statuses = st.sidebar.multiselect("Status", statuses, default=[], placeholder="Selecione...", on_change=reset_page)

# Show active status chips
if selected_statuses:
    chips_html = '<div class="status-chips">'
    for s in selected_statuses:
        chips_html += f'<span class="status-chip active">{s}</span>'
    chips_html += '</div>'
    st.sidebar.markdown(chips_html, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-section">FILTROS DE DATA</div>', unsafe_allow_html=True)

# Date Filters
date_filters = {}
today = date.today()
last_day = calendar.monthrange(today.year, today.month)[1]
current_month_start = date(today.year, today.month, 1)
current_month_end = date(today.year, today.month, last_day)

date_cols = {
    'dataAssinatura': 'Data Assinatura',
    'dataInicioVigencia': 'Início Vigência',
    'dataFimVigencia': 'Fim Vigência',
    'dataPublicacaoDOU': 'Publicação DOU'
}

# Data Inicial / Data Final (simplified to match mockup)
if 'dataAssinatura' in df.columns:
    min_date = df['dataAssinatura'].min()
    max_date = df['dataAssinatura'].max()
    if pd.notnull(min_date) and pd.notnull(max_date):
        date_start = st.sidebar.date_input(
            "Data Inicial",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            on_change=reset_page
        )
        date_end = st.sidebar.date_input(
            "Data Final",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            on_change=reset_page
        )
        date_filters['dataAssinatura'] = (date_start, date_end)

# Extra filters (not in mockup but preserving functionality)
st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-section">FILTROS ADICIONAIS</div>', unsafe_allow_html=True)

# Ano Assinatura
years = sorted(df['ano_assinatura'].unique(), reverse=True)
selected_years = st.sidebar.multiselect("Ano de Assinatura", years, default=[], placeholder="Selecione o ano...", on_change=reset_page)

# UF Gestora
ufs = sorted(df['uf_gestora'].astype(str).unique())
selected_ufs = st.sidebar.multiselect("UF (Localização)", ufs, placeholder="Selecione a UF...", on_change=reset_page)

# Fornecedor
suppliers = sorted(df['nome_fornecedor'].astype(str).unique())
selected_suppliers = st.sidebar.multiselect("Fornecedor", suppliers, placeholder="Busque por fornecedor...", on_change=reset_page)

# Sidebar footer
st.sidebar.markdown(f"""
<div class="sidebar-footer">
    <div class="sidebar-footer-item">
        <span class="sidebar-footer-dot"></span>
        <span>Registros: <b>{len(df):,}</b></span>
    </div>
    <div class="sidebar-footer-item">
        <span class="sidebar-footer-dot green"></span>
        <span>Atualizado em: {data_load_date}</span>
    </div>
</div>
""".replace(",", "."), unsafe_allow_html=True)


# --- Apply Filters ---
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

# Date filter
for col, dates in date_filters.items():
    if isinstance(dates, tuple) and len(dates) == 2:
        start_date, end_date = dates
        filtered_df = filtered_df[
            (filtered_df[col].dt.date >= start_date) &
            (filtered_df[col].dt.date <= end_date)
        ]


# --- Active Filters Bar ---
active_filters = []
if selected_types:
    active_filters.append(f"Categoria: {', '.join(selected_types)}")
if selected_statuses:
    active_filters.append(f"Status: {', '.join(selected_statuses)}")
if selected_years:
    active_filters.append(f"Ano: {', '.join(map(str, selected_years))}")
if selected_modalities:
    active_filters.append(f"Departamento: {', '.join(selected_modalities)}")
if selected_ufs:
    active_filters.append(f"UF: {', '.join(selected_ufs)}")
if selected_suppliers:
    active_filters.append(f"Fornecedor: {len(selected_suppliers)} selecionado(s)")

for col, dates in date_filters.items():
    if isinstance(dates, tuple) and len(dates) == 2:
        start, end = dates
        min_d = df[col].min().date() if pd.notnull(df[col].min()) else None
        max_d = df[col].max().date() if pd.notnull(df[col].max()) else None
        if min_d and max_d and (start != min_d or end != max_d):
            active_filters.append(f"Data: {start.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}")

if active_filters:
    chips_html = '<div class="filters-bar"><span class="filters-bar-icon">🔍</span><span class="filters-bar-label">Filtros Ativos:</span>'
    for f in active_filters:
        chips_html += f'<span class="filter-chip">{f} <span class="chip-x">×</span></span>'
    chips_html += '<span class="clear-all-link">Limpar Todos</span></div>'
    st.markdown(chips_html, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="filters-bar">
        <span class="filters-bar-icon">📋</span>
        <span class="filters-bar-label">Mostrando todos os registros</span>
    </div>
    """, unsafe_allow_html=True)


# --- Tabs ---
tab1, tab2 = st.tabs(["📋 Visão Geral", "📁 Dados Detalhados"])

# --- Tab 1: Visão Geral ---
with tab1:
    # KPIs
    total_contratos = len(filtered_df)
    valor_total = filtered_df['valorInicialCompra'].sum()

    if total_contratos > 0:
        bens_count = len(filtered_df[filtered_df['tipo_contrato'] == 'Aquisição de Bens'])
        servicos_count = len(filtered_df[filtered_df['tipo_contrato'] == 'Prestação de Serviços'])
        pct_bens = (bens_count / total_contratos) * 100
        pct_servicos = (servicos_count / total_contratos) * 100
    else:
        pct_bens = 0
        pct_servicos = 0

    # --- Cálculo da variação % YoY do Valor Total ---
    valor_badge = None
    valor_badge_type = 'neutral'
    if 'ano_assinatura' in filtered_df.columns and total_contratos > 0:
        anos_disponiveis = sorted(filtered_df['ano_assinatura'].unique())
        if len(anos_disponiveis) >= 2:
            ultimo_ano = anos_disponiveis[-1]
            penultimo_ano = anos_disponiveis[-2]
            valor_ultimo = filtered_df[filtered_df['ano_assinatura'] == ultimo_ano]['valorInicialCompra'].sum()
            valor_penultimo = filtered_df[filtered_df['ano_assinatura'] == penultimo_ano]['valorInicialCompra'].sum()
            if valor_penultimo > 0:
                variacao = ((valor_ultimo - valor_penultimo) / valor_penultimo) * 100
                sinal = '+' if variacao >= 0 else ''
                valor_badge = f"{sinal}{variacao:.1f}%"
                valor_badge_type = 'positive' if variacao >= 0 else 'negative'

    col1, col2, col3, col4 = st.columns(4)

    valor_fmt = f"{valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    with col1:
        render_kpi_card("Valor Total (R$)", valor_fmt, "📊", badge=valor_badge, badge_type=valor_badge_type, bar_pct=100)
    with col2:
        render_kpi_card("Contratos", f"{total_contratos:,}".replace(",", "."), "📄", bar_pct=75)
    with col3:
        render_kpi_card("% Bens", f"{pct_bens:.1f}%", "📦", bar_pct=pct_bens)
    with col4:
        render_kpi_card("% Serviços", f"{pct_servicos:.1f}%", "🔧", bar_pct=pct_servicos)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Charts Row
    col_chart1, col_chart2 = st.columns(2)
    msg_no_data = "<div class='chart-card' style='display:flex;align-items:center;justify-content:center;height:260px;color:#94A3B8;'>Sem dados para exibir.</div>"

    with col_chart1:
        if total_contratos > 0:
            fig_pie = px.pie(filtered_df, names='tipo_contrato', hole=0.65,
                             color_discrete_sequence=['#2563EB', '#93C5FD', '#E2E8F0'])
            fig_pie.update_traces(
                textinfo='none',
                hovertemplate='%{label}: %{percent}<extra></extra>'
            )
            # Center annotation
            fig_pie.add_annotation(
                text=f"<b>100%</b><br><span style='font-size:11px;color:#94A3B8'>Total</span>",
                x=0.5, y=0.5, font=dict(size=20, color='#1E293B', family='Inter'),
                showarrow=False
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=300, margin=dict(l=20, r=20, t=10, b=50),
                font=dict(family="Inter"),
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.15,
                    xanchor="center", x=0.5, font=dict(size=12)
                )
            )
            render_chart_within_card(fig_pie, "Distribuição por Tipo", height_px=400)
        else:
            st.markdown(msg_no_data, unsafe_allow_html=True)

    with col_chart2:
        if total_contratos > 0:
            uf_counts = filtered_df['uf_gestora'].value_counts().reset_index().head(5)
            uf_counts.columns = ['UF', 'Contratos']
            uf_counts = uf_counts.sort_values('Contratos', ascending=True)

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                y=uf_counts['UF'],
                x=uf_counts['Contratos'],
                orientation='h',
                marker_color='#2563EB',
                marker_cornerradius=4,
                text=uf_counts['Contratos'],
                textposition='outside',
                textfont=dict(size=12, color='#64748B')
            ))
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=300, margin=dict(l=40, r=60, t=10, b=20),
                font=dict(family="Inter"),
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=13, color='#1E293B')),
                bargap=0.35
            )
            render_chart_within_card(fig_bar, "Top 10 UFs por Quantidade", height_px=400)
        else:
            st.markdown(msg_no_data, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Evolution Chart
    if not df.empty:
        yearly_data = df['ano_assinatura'].value_counts().reset_index()
        yearly_data.columns = ['Ano', 'Qtd']
        yearly_data = yearly_data.sort_values('Ano')

        fig_area = px.area(yearly_data, x='Ano', y='Qtd', markers=True,
                           color_discrete_sequence=['#2563EB'],
                           text='Qtd')
        fig_area.update_traces(
            textposition='top center',
            line=dict(width=2),
            fillcolor='rgba(37, 99, 235, 0.08)'
        )
        fig_area.update_xaxes(type='category')
        fig_area.update_yaxes(tickformat='d', nticks=6, showgrid=True, gridcolor='#F1F5F9')
        fig_area.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=250, margin=dict(l=60, r=30, t=20, b=40),
            font=dict(family="Inter"),
            xaxis_title=None, yaxis_title=None
        )
        render_chart_within_card(fig_area, "Evolução de Contratos (Histórico Completo)", height_px=340)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # --- Table in Visão Geral (as shown in mockup) ---
    col_tbl_header, col_tbl_export = st.columns([3, 1])
    with col_tbl_header:
        st.markdown('<div class="table-title">Tabela de Contratos</div>', unsafe_allow_html=True)
    with col_tbl_export:
        # Export button
        export_df = filtered_df.copy()
        cols_to_swap = {
            'valorInicialCompra': 'valorInicialCompra_formatado',
            'valorFinalCompra': 'valorFinalCompra_formatado',
            'dataAssinatura': 'dataAssinatura_formatada',
            'dataInicioVigencia': 'dataInicioVigencia_formatada',
            'dataFimVigencia': 'dataFimVigencia_formatada',
            'dataPublicacaoDOU': 'dataPublicacaoDOU_formatada'
        }
        for raw_col, fmt_col in cols_to_swap.items():
            if fmt_col in export_df.columns:
                export_df[raw_col] = export_df[fmt_col]
        cols_to_drop = [c for c in export_df.columns if c.endswith('_formatada') or c.endswith('_formatado')]
        export_df = export_df.drop(columns=cols_to_drop, errors='ignore')
        column_renames = {
            'valorInicialCompra': 'Valor Inicial', 'valorFinalCompra': 'Valor Final',
            'dataAssinatura': 'Data de Assinatura', 'dataInicioVigencia': 'Início da Vigência',
            'dataFimVigencia': 'Fim da Vigência', 'dataPublicacaoDOU': 'Publicação no DOU',
            'ano_assinatura': 'Ano de Assinatura', 'id': 'ID do Contrato',
            'numero': 'Número do Contrato', 'numeroProcesso': 'Número do Processo',
            'situacaoContrato': 'Situação do Contrato', 'modalidadeCompra': 'Modalidade de Compra',
            'tipo_contrato': 'Tipo de Contrato', 'objeto': 'Objeto do Contrato',
            'fundamentoLegal': 'Fundamento Legal', 'compra_numero': 'Número da Compra',
            'compra_objeto': 'Objeto da Compra', 'compra_numeroProcesso': 'Processo da Compra',
            'compra_contatoResponsavel': 'Contato Responsável', 'fornecedor_id': 'ID do Fornecedor',
            'fornecedor_cpfFormatado': 'CPF do Fornecedor', 'fornecedor_cnpjFormatado': 'CNPJ do Fornecedor',
            'fornecedor_numeroInscricaoSocial': 'Inscrição Social', 'fornecedor_nome': 'Nome do Fornecedor',
            'fornecedor_razaoSocialReceita': 'Razão Social', 'fornecedor_nomeFantasiaReceita': 'Nome Fantasia',
            'fornecedor_tipo': 'Tipo de Fornecedor', 'nome_fornecedor': 'Fornecedor',
            'ug_codigo': 'Código da UG', 'ug_nome': 'Unidade Gestora', 'ug_poder': 'Poder (UG)',
            'ug_orgao_vinculado': 'Órgão Vinculado (UG)', 'ug_orgao_maximo': 'Órgão Máximo (UG)',
            'ugc_codigo': 'Código da UG Compras', 'ugc_nome': 'UG Compras',
            'ugc_poder': 'Poder (UG Compras)', 'ugc_orgao_vinculado': 'Órgão Vinculado (UG Compras)',
            'ugc_orgao_maximo': 'Órgão Máximo (UG Compras)', 'uf_gestora': 'UF'
        }
        export_df = export_df.rename(columns=column_renames)
        csv = export_df.to_csv(index=False, sep=';').encode('utf-8-sig')
        st.download_button(
            label="📄 Exportar CSV (Formatado)",
            data=csv,
            file_name='contratos_formatados.csv',
            mime='text/csv',
            use_container_width=True
        )

    # Paginated Table
    if total_contratos > 0:
        rows_per_page = 10
        total_pages = (total_contratos - 1) // rows_per_page + 1

        if st.session_state.page_number > total_pages:
            st.session_state.page_number = 1

        start_idx = (st.session_state.page_number - 1) * rows_per_page
        end_idx = start_idx + rows_per_page

        cols_to_hide = [c for c in filtered_df.columns if c.endswith('_formatada') or c.endswith('_formatado')]
        display_df = filtered_df.iloc[start_idx:end_idx].drop(columns=cols_to_hide, errors='ignore')

        column_config = {
            "valorInicialCompra": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
            "valorFinalCompra": st.column_config.NumberColumn("Valor Final", format="R$ %.2f"),
            "id": st.column_config.TextColumn("ID Contrato", width="small"),
            "numero": st.column_config.TextColumn("Número", width="small"),
            "numeroProcesso": st.column_config.TextColumn("Processo", width="medium"),
            "situacaoContrato": st.column_config.TextColumn("Status", width="small"),
            "modalidadeCompra": st.column_config.TextColumn("Modalidade", width="medium"),
            "tipo_contrato": st.column_config.TextColumn("Tipo", width="medium"),
            "objeto": st.column_config.TextColumn("Objeto", width="large"),
            "fundamentoLegal": st.column_config.TextColumn("Fundamento Legal", width="medium"),
            "nome_fornecedor": st.column_config.TextColumn("Contratado", width="large"),
            "uf_gestora": st.column_config.TextColumn("UF", width="small"),
            "ano_assinatura": st.column_config.NumberColumn("Ano", format="%d"),
        }

        for col, label in date_cols.items():
            if col in display_df.columns:
                column_config[col] = st.column_config.DateColumn(label, format="DD/MM/YYYY")

        st.dataframe(
            display_df,
            use_container_width=True,
            column_config=column_config,
            height=450
        )

        # Pagination below table (mockup style)
        col_prev, col_page, col_next = st.columns([1, 2, 1])

        with col_prev:
            st.button("← Anterior", on_click=prev_page, disabled=(st.session_state.page_number <= 1), use_container_width=True)
        with col_page:
            st.markdown(f"<div style='text-align:center; padding-top:6px; font-size:13px; color:#64748B;'>Página <b>{st.session_state.page_number}</b> de <b>{total_pages}</b></div>", unsafe_allow_html=True)
        with col_next:
            st.button("Próxima →", on_click=next_page, disabled=(st.session_state.page_number >= total_pages), use_container_width=True)
    else:
        st.warning("Nenhum contrato encontrado com os filtros atuais.")


# --- Tab 2: Dados Detalhados (full table) ---
with tab2:
    col_header2, col_export2 = st.columns([3, 1])

    with col_header2:
        st.markdown('<div class="table-title">Dados Detalhados</div>', unsafe_allow_html=True)

    with col_export2:
        st.download_button(
            label="📄 Exportar CSV (Completo)",
            data=csv,
            file_name='contratos_completos.csv',
            mime='text/csv',
            use_container_width=True,
            key='export_tab2'
        )

    if total_contratos > 0:
        cols_to_hide_t2 = [c for c in filtered_df.columns if c.endswith('_formatada') or c.endswith('_formatado')]
        full_display_df = filtered_df.drop(columns=cols_to_hide_t2, errors='ignore')

        full_column_config = {
            "valorInicialCompra": st.column_config.NumberColumn("Valor Inicial", format="R$ %.2f"),
            "valorFinalCompra": st.column_config.NumberColumn("Valor Final", format="R$ %.2f"),
            "id": st.column_config.TextColumn("ID do Contrato", width="small"),
            "numero": st.column_config.TextColumn("Número do Contrato", width="small"),
            "numeroProcesso": st.column_config.TextColumn("Número do Processo", width="medium"),
            "situacaoContrato": st.column_config.TextColumn("Situação do Contrato", width="medium"),
            "modalidadeCompra": st.column_config.TextColumn("Modalidade de Compra", width="medium"),
            "tipo_contrato": st.column_config.TextColumn("Tipo de Contrato", width="medium"),
            "objeto": st.column_config.TextColumn("Objeto do Contrato", width="large"),
            "fundamentoLegal": st.column_config.TextColumn("Fundamento Legal", width="medium"),
            "compra_numero": st.column_config.TextColumn("Número da Compra", width="small"),
            "compra_objeto": st.column_config.TextColumn("Objeto da Compra", width="large"),
            "compra_numeroProcesso": st.column_config.TextColumn("Processo da Compra", width="medium"),
            "compra_contatoResponsavel": st.column_config.TextColumn("Contato Responsável", width="medium"),
            "fornecedor_id": st.column_config.TextColumn("ID do Fornecedor", width="small"),
            "fornecedor_cpfFormatado": st.column_config.TextColumn("CPF do Fornecedor", width="small"),
            "fornecedor_cnpjFormatado": st.column_config.TextColumn("CNPJ do Fornecedor", width="medium"),
            "fornecedor_numeroInscricaoSocial": st.column_config.TextColumn("Inscrição Social", width="small"),
            "fornecedor_nome": st.column_config.TextColumn("Nome do Fornecedor", width="large"),
            "fornecedor_razaoSocialReceita": st.column_config.TextColumn("Razão Social", width="large"),
            "fornecedor_nomeFantasiaReceita": st.column_config.TextColumn("Nome Fantasia", width="large"),
            "fornecedor_tipo": st.column_config.TextColumn("Tipo de Fornecedor", width="small"),
            "nome_fornecedor": st.column_config.TextColumn("Fornecedor", width="large"),
            "ug_codigo": st.column_config.TextColumn("Código da UG", width="small"),
            "ug_nome": st.column_config.TextColumn("Unidade Gestora", width="large"),
            "ug_poder": st.column_config.TextColumn("Poder (UG)", width="small"),
            "ug_orgao_vinculado": st.column_config.TextColumn("Órgão Vinculado (UG)", width="medium"),
            "ug_orgao_maximo": st.column_config.TextColumn("Órgão Máximo (UG)", width="medium"),
            "ugc_codigo": st.column_config.TextColumn("Código da UG Compras", width="small"),
            "ugc_nome": st.column_config.TextColumn("UG Compras", width="large"),
            "ugc_poder": st.column_config.TextColumn("Poder (UG Compras)", width="small"),
            "ugc_orgao_vinculado": st.column_config.TextColumn("Órgão Vinculado (UG Compras)", width="medium"),
            "ugc_orgao_maximo": st.column_config.TextColumn("Órgão Máximo (UG Compras)", width="medium"),
            "uf_gestora": st.column_config.TextColumn("UF", width="small"),
            "ano_assinatura": st.column_config.NumberColumn("Ano de Assinatura", format="%d")
        }

        for col, label in date_cols.items():
            if col in full_display_df.columns:
                full_column_config[col] = st.column_config.DateColumn(label, format="DD/MM/YYYY")

        st.dataframe(
            full_display_df,
            use_container_width=True,
            column_config=full_column_config,
            height=700
        )
    else:
        st.warning("Nenhum contrato encontrado com os filtros atuais.")
