"""
Data loader module - migrado do utils.py do Streamlit.
Carrega e pré-processa os dados do CSV de contratos.
"""
import pandas as pd
import os
from datetime import datetime
from functools import lru_cache
from django.conf import settings


_data_cache = {
    'df': None,
    'mtime': None,
    'metadata': None,
}


def _get_csv_path():
    return getattr(settings, 'DATA_CSV_PATH', None)


def get_data_metadata():
    """Retorna a data de última modificação do arquivo CSV."""
    target_path = _get_csv_path()
    if target_path and os.path.exists(target_path):
        mod_time = os.path.getmtime(target_path)
        return datetime.fromtimestamp(mod_time).strftime('%d/%m/%Y %H:%M')
    return 'N/A'


def load_data():
    """
    Carrega e pré-processa os dados de contratos do CSV.
    Usa cache baseado na data de modificação do arquivo.
    """
    target_path = _get_csv_path()
    if not target_path or not os.path.exists(target_path):
        return pd.DataFrame()

    # Check cache validity
    current_mtime = os.path.getmtime(target_path)
    if _data_cache['df'] is not None and _data_cache['mtime'] == current_mtime:
        return _data_cache['df']

    try:
        df = pd.read_csv(target_path)
    except Exception:
        return pd.DataFrame()

    # Dates
    date_cols = ['dataAssinatura', 'dataFimVigencia', 'dataInicioVigencia', 'dataPublicacaoDOU']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Numerics
    num_cols = ['valorInicialCompra', 'valorFinalCompra']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # Fornecedor name
    if 'fornecedor_nome' in df.columns:
        df['nome_fornecedor'] = df['fornecedor_nome'].fillna('N/A')
    elif 'fornecedor_razaoSocialReceita' in df.columns:
        df['nome_fornecedor'] = df['fornecedor_razaoSocialReceita'].fillna('N/A')
    else:
        df['nome_fornecedor'] = 'N/A'

    # Year
    if 'dataAssinatura' in df.columns:
        df['ano_assinatura'] = df['dataAssinatura'].dt.year.fillna(0).astype(int)

    # Fill NAs
    categorical_cols = ['situacaoContrato', 'modalidadeCompra', 'uf_gestora', 'tipo_contrato']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Não Informado')

    # Update cache
    _data_cache['df'] = df
    _data_cache['mtime'] = current_mtime
    _data_cache['metadata'] = get_data_metadata()

    return df
