import pandas as pd
import streamlit as st
import os
import ast

@st.cache_data
def load_data(file_path):
    """
    Loads and preprocesses the contract data from the CSV file.
    """
    if not os.path.exists(file_path):
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
        return pd.DataFrame()

    # Convert Date columns
    date_cols = ['dataAssinatura', 'dataFimVigencia', 'dataInicioVigencia', 'dataPublicacaoDOU']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Convert Numeric columns (cleaning if necessary)
    num_cols = ['valorInicialCompra', 'valorFinalCompra']
    for col in num_cols:
        if col in df.columns:
             df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # Extract 'nome' from 'fornecedor' JSON-like string
    if 'fornecedor' in df.columns:
        def extract_fornecedor_name(val):
            try:
                # The data seems to use single quotes for JSON, which is not standard JSON but valid Python dict string
                # using ast.literal_eval is safer than eval()
                if isinstance(val, str):
                    data = ast.literal_eval(val)
                    return data.get('nome', 'N/A')
            except:
                pass
            return 'N/A'
        
        df['nome_fornecedor'] = df['fornecedor'].apply(extract_fornecedor_name)

    # Add 'ano_assinatura' for filtering
    if 'dataAssinatura' in df.columns:
        df['ano_assinatura'] = df['dataAssinatura'].dt.year

    return df
