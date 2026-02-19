import pandas as pd
import ast
import logging
import re
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data(file_path):
    """Loads data from the raw CSV file."""
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} records from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return pd.DataFrame()

def _parse_dictionary_column(val):
    """Helper to safely parse dictionary strings."""
    try:
        if isinstance(val, str):
            val = val.strip()
            if not val: return {}
            return ast.literal_eval(val)
        elif isinstance(val, dict):
            return val
    except:
        pass
    return {}

def flatten_nested_columns(df):
    """Expands dictionary columns 'compra' and 'fornecedor'."""
    if df.empty:
        return df

    logger.info("Flattening dictionary columns...")
    
    # Process 'compra'
    if 'compra' in df.columns:
        # Check if first valid value is string representation of dict
        compra_data = df['compra'].apply(_parse_dictionary_column).apply(pd.Series)
        compra_data.columns = [f"compra_{col}" for col in compra_data.columns]
        df = pd.concat([df.drop('compra', axis=1), compra_data], axis=1)

    # Process 'fornecedor'
    if 'fornecedor' in df.columns:
        fornecedor_data = df['fornecedor'].apply(_parse_dictionary_column).apply(pd.Series)
        fornecedor_data.columns = [f"fornecedor_{col}" for col in fornecedor_data.columns]
        df = pd.concat([df.drop('fornecedor', axis=1), fornecedor_data], axis=1)

    # Process 'unidadeGestora'
    if 'unidadeGestora' in df.columns:
        ug_data = df['unidadeGestora'].apply(_parse_dictionary_column)
        
        # Extract specific fields
        df['ug_codigo'] = ug_data.apply(lambda x: x.get('codigo', '') if isinstance(x, dict) else '')
        df['ug_nome'] = ug_data.apply(lambda x: x.get('nome', '') if isinstance(x, dict) else '')
        df['ug_poder'] = ug_data.apply(lambda x: x.get('descricaoPoder', '') if isinstance(x, dict) else '')
        
        # Extract linked organ names
        df['ug_orgao_vinculado'] = ug_data.apply(lambda x: x.get('orgaoVinculado', {}).get('nome', '') if isinstance(x, dict) else '')
        df['ug_orgao_maximo'] = ug_data.apply(lambda x: x.get('orgaoMaximo', {}).get('nome', '') if isinstance(x, dict) else '')
        
        # Drop original
        df = df.drop(columns=['unidadeGestora'], errors='ignore')
        
    # Process 'unidadeGestoraCompras'
    if 'unidadeGestoraCompras' in df.columns:
        ugc_data = df['unidadeGestoraCompras'].apply(_parse_dictionary_column)
        
        # Extract specific fields
        df['ugc_codigo'] = ugc_data.apply(lambda x: x.get('codigo', '') if isinstance(x, dict) else '')
        df['ugc_nome'] = ugc_data.apply(lambda x: x.get('nome', '') if isinstance(x, dict) else '')
        df['ugc_poder'] = ugc_data.apply(lambda x: x.get('descricaoPoder', '') if isinstance(x, dict) else '')
        
        # Extract linked organ names
        df['ugc_orgao_vinculado'] = ugc_data.apply(lambda x: x.get('orgaoVinculado', {}).get('nome', '') if isinstance(x, dict) else '')
        df['ugc_orgao_maximo'] = ugc_data.apply(lambda x: x.get('orgaoMaximo', {}).get('nome', '') if isinstance(x, dict) else '')
        
        # Drop original
        df = df.drop(columns=['unidadeGestoraCompras'], errors='ignore')

    return df

def clean_data_types(df):
    """Standardizes data types."""
    if df.empty:
        return df

    logger.info("Cleaning data types...")

    # Date columns
    date_cols = ['dataAssinatura', 'dataFimVigencia', 'dataInicioVigencia', 'dataPublicacaoDOU']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Clean 'fundamentoLegal' column
    if 'fundamentoLegal' in df.columns:
        # Remove "Fundamento Legal:" prefix (case-insensitive) and strip whitespace
        df['fundamentoLegal'] = df['fundamentoLegal'].astype(str).str.replace(r'^\s*Fundamento Legal\s*:\s*', '', regex=True, flags=re.IGNORECASE).str.strip()

    def robust_objeto_clean(val):
        if pd.isna(val): return ""
        s = str(val).strip()
        # 1. Remove "Objeto:" prefix
        s = re.sub(r'^\s*Objeto\s*:\s*', '', s, flags=re.IGNORECASE).strip()
        # 2. Remove modality prefix if present (e.g., "Pregão Eletrônico - ")
        match = re.match(r'^[^:]*?\-\s*', s)
        if match and len(match.group(0)) < 60:
            modality_keywords = ['pregão', 'inexigibilidade', 'dispensa', 'convite', 'tomada', 'concorrência']
            prefix = match.group(0).lower()
            if any(k in prefix for k in modality_keywords):
                s = s[len(match.group(0)):].strip()
        return s

    # Clean 'objeto' column
    if 'objeto' in df.columns:
        df['objeto'] = df['objeto'].apply(robust_objeto_clean)

    # Clean 'compra_objeto' column
    if 'compra_objeto' in df.columns:
        df['compra_objeto'] = df['compra_objeto'].apply(robust_objeto_clean)

    # Numeric columns
    num_cols = ['valorInicialCompra', 'valorFinalCompra']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
    return df

def format_to_brazilian_standards(df):
    """Creates formatted columns for display in Brazilian standard."""
    if df.empty:
        return df

    logger.info("Formatting data to Brazilian standards...")

    # Format Dates (DD/MM/YYYY)
    date_cols = ['dataAssinatura', 'dataFimVigencia', 'dataInicioVigencia', 'dataPublicacaoDOU']
    for col in date_cols:
        if col in df.columns:
            # Create a new formatted column. Check if it's datetime first
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                 df[col] = pd.to_datetime(df[col], errors='coerce')
            df[f"{col}_formatada"] = df[col].dt.strftime('%d/%m/%Y').fillna('')

    # Format Currency (R$ X.XXX,XX)
    def format_currency(val):
        try:
            return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return val

    num_cols = ['valorInicialCompra', 'valorFinalCompra']
    for col in num_cols:
        if col in df.columns:
            df[f"{col}_formatado"] = df[col].apply(format_currency)
            
    return df


def enrich_data(df):
    """Adds derived columns like contract type and UF."""
    if df.empty:
        return df

    logger.info("Enriching data with derived columns...")

    # 1. Classify Contract Type (Bens vs Serviços)
    def classify_type(row):
        text = str(row.get('objeto', '')).lower() + " " + str(row.get('compra_objeto', '')).lower()
        if any(x in text for x in ['aquisição', 'compra', 'fornecimento', 'bens', 'material']):
            return 'Aquisição de Bens'
        if any(x in text for x in ['serviço', 'prestação', 'manutenção', 'locação', 'consultoria', 'apoio']):
            return 'Prestação de Serviços'
        return 'Outros'

    df['tipo_contrato'] = df.apply(classify_type, axis=1)

    # 2. Extract UF from Unidade Gestora
    def extract_uf(row):
        # Use the flattened name which should contain the "/UF" pattern
        ug_nome = str(row.get('ug_nome', ''))
        
        # Look for pattern like "/UF" at end of string
        if '/' in ug_nome:
            parts = ug_nome.split('/')
            if len(parts) > 1:
                last_part = parts[-1].strip().upper()
                if len(last_part) == 2:
                    return last_part
        return 'N/A'

    df['uf_gestora'] = df.apply(extract_uf, axis=1)
    
    return df

def save_refined_data(df, output_path):
    """Saves the refined dataframe to CSV."""
    if not df.empty:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Saved refined data to {output_path}")
    else:
        logger.warning("No data to save.")
