import pandas as pd
import streamlit as st
import os
import ast
from datetime import datetime

import time

@st.cache_data
def get_data_metadata(file_path=None):
    """Returns metadata about the data file (e.g., last modified date)."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_path = os.path.join(base_dir, '.tmp', 'contratos_20701_refined.csv')
    target_path = file_path if file_path else default_path
    
    if os.path.exists(target_path):
        mod_time = os.path.getmtime(target_path)
        return datetime.fromtimestamp(mod_time).strftime('%d/%m/%Y %H:%M')
    return "N/A"

@st.cache_data
def load_data(file_path=None):
    """
    Loads and preprocesses the contract data from the CSV file.
    By default loads the REFINED data for organ 20701.
    """
    
    # Default to the refined file if no path provided or if generic path provided
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_path = os.path.join(base_dir, '.tmp', 'contratos_20701_refined.csv')
    
    target_path = file_path if file_path else default_path
    
    if not os.path.exists(target_path):
        return pd.DataFrame()

    try:
        df = pd.read_csv(target_path)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
        return pd.DataFrame()

    # Data types should already be clean from Transformer, but read_csv might infer wrong.
    # Ensure Dates are datetime objects for filtering/plotting
    date_cols = ['dataAssinatura', 'dataFimVigencia', 'dataInicioVigencia', 'dataPublicacaoDOU']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Ensure Numeric columns
    num_cols = ['valorInicialCompra', 'valorFinalCompra']
    for col in num_cols:
        if col in df.columns:
             df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # Ensure compatibility with app.py expected columns
    # Transformer creates 'fornecedor_nome'
    # Ensure compatibility with app.py expected columns
    if 'fornecedor_nome' in df.columns:
        df['nome_fornecedor'] = df['fornecedor_nome'].fillna('N/A')
    elif 'fornecedor_razaoSocialReceita' in df.columns:
         df['nome_fornecedor'] = df['fornecedor_razaoSocialReceita'].fillna('N/A')
    else:
        df['nome_fornecedor'] = 'N/A'

    # Add 'ano_assinatura' for filtering if not present
    if 'dataAssinatura' in df.columns:
        df['ano_assinatura'] = df['dataAssinatura'].dt.year.fillna(0).astype(int)
    
    # Fill N/A for categorical columns to avoid filter errors
    categorical_cols = ['situacaoContrato', 'modalidadeCompra', 'uf_gestora', 'tipo_contrato']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Não Informado')

    return df
