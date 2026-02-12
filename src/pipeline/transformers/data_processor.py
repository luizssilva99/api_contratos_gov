import pandas as pd
import ast
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ContractTransformer:
    def __init__(self, raw_file_path):
        self.raw_file_path = raw_file_path
        self.df = None

    def load_data(self):
        """Loads data from the raw CSV file."""
        try:
            self.df = pd.read_csv(self.raw_file_path)
            logging.info(f"Loaded {len(self.df)} records from {self.raw_file_path}")
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            raise

    def _parse_dictionary_column(self, val):
        """Helper to safely parse dictionary strings."""
        try:
            if isinstance(val, str):
                return ast.literal_eval(val)
            elif isinstance(val, dict):
                return val
        except:
            pass
        return {}

    def flatten_columns(self):
        """Expands dictionary columns 'compra' and 'fornecedor'."""
        if self.df is None:
            raise ValueError("Dataframe not loaded. Call load_data() first.")

        logging.info("Flattening dictionary columns...")
        
        # Process 'compra'
        if 'compra' in self.df.columns:
            compra_data = self.df['compra'].apply(self._parse_dictionary_column).apply(pd.Series)
            compra_data.columns = [f"compra_{col}" for col in compra_data.columns]
            self.df = pd.concat([self.df.drop('compra', axis=1), compra_data], axis=1)

        # Process 'fornecedor'
        if 'fornecedor' in self.df.columns:
            fornecedor_data = self.df['fornecedor'].apply(self._parse_dictionary_column).apply(pd.Series)
            fornecedor_data.columns = [f"fornecedor_{col}" for col in fornecedor_data.columns]
            self.df = pd.concat([self.df.drop('fornecedor', axis=1), fornecedor_data], axis=1)

        # Process 'unidadeGestora'
        if 'unidadeGestora' in self.df.columns:
            ug_data = self.df['unidadeGestora'].apply(self._parse_dictionary_column)
            
            # Extract specific fields
            self.df['ug_codigo'] = ug_data.apply(lambda x: x.get('codigo', ''))
            self.df['ug_nome'] = ug_data.apply(lambda x: x.get('nome', ''))
            self.df['ug_poder'] = ug_data.apply(lambda x: x.get('descricaoPoder', ''))
            
            # Extract linked organ names
            self.df['ug_orgao_vinculado'] = ug_data.apply(lambda x: x.get('orgaoVinculado', {}).get('nome', ''))
            self.df['ug_orgao_maximo'] = ug_data.apply(lambda x: x.get('orgaoMaximo', {}).get('nome', ''))
            
        # Process 'unidadeGestoraCompras'
        if 'unidadeGestoraCompras' in self.df.columns:
            ugc_data = self.df['unidadeGestoraCompras'].apply(self._parse_dictionary_column)
            
            # Extract specific fields
            self.df['ugc_codigo'] = ugc_data.apply(lambda x: x.get('codigo', ''))
            self.df['ugc_nome'] = ugc_data.apply(lambda x: x.get('nome', ''))
            self.df['ugc_poder'] = ugc_data.apply(lambda x: x.get('descricaoPoder', ''))
            
            # Extract linked organ names
            self.df['ugc_orgao_vinculado'] = ugc_data.apply(lambda x: x.get('orgaoVinculado', {}).get('nome', ''))
            self.df['ugc_orgao_maximo'] = ugc_data.apply(lambda x: x.get('orgaoMaximo', {}).get('nome', ''))

    def clean_data(self):
        """Standardizes data types."""
        if self.df is None:
            return

        logging.info("Cleaning data types...")

        # Date columns
        date_cols = ['dataAssinatura', 'dataFimVigencia', 'dataInicioVigencia', 'dataPublicacaoDOU']
        for col in date_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

        # Clean 'fundamentoLegal' column
        if 'fundamentoLegal' in self.df.columns:
            # Remove "Fundamento Legal:" prefix (case-insensitive) and strip whitespace
            self.df['fundamentoLegal'] = self.df['fundamentoLegal'].astype(str).str.replace(r'^\s*Fundamento Legal\s*:\s*', '', regex=True, flags=re.IGNORECASE).str.strip()

        def robust_objeto_clean(val):
            if pd.isna(val): return ""
            s = str(val).strip()
            # 1. Remove "Objeto:" prefix
            s = re.sub(r'^\s*Objeto\s*:\s*', '', s, flags=re.IGNORECASE).strip()
            # 2. Remove modality prefix if present (e.g., "Pregão Eletrônico - ")
            # Only if it's followed by a dash within the first 60 chars
            match = re.match(r'^[^:]*?\-\s*', s)
            if match and len(match.group(0)) < 60:
                modality_keywords = ['pregão', 'inexigibilidade', 'dispensa', 'convite', 'tomada', 'concorrência']
                prefix = match.group(0).lower()
                if any(k in prefix for k in modality_keywords):
                    s = s[len(match.group(0)):].strip()
            return s

        # Clean 'objeto' column
        if 'objeto' in self.df.columns:
            self.df['objeto'] = self.df['objeto'].apply(robust_objeto_clean)

        # Clean 'compra_objeto' column
        if 'compra_objeto' in self.df.columns:
            self.df['compra_objeto'] = self.df['compra_objeto'].apply(robust_objeto_clean)

        # Numeric columns
        num_cols = ['valorInicialCompra', 'valorFinalCompra']
        for col in num_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0.0)

    def format_brazilian_standards(self):
        """Creates formatted columns for display in Brazilian standard."""
        if self.df is None:
            return

        logging.info("Formatting data to Brazilian standards...")

        # Format Dates (DD/MM/YYYY)
        date_cols = ['dataAssinatura', 'dataFimVigencia', 'dataInicioVigencia', 'dataPublicacaoDOU']
        for col in date_cols:
            if col in self.df.columns:
                # Create a new formatted column
                self.df[f"{col}_formatada"] = self.df[col].dt.strftime('%d/%m/%Y').fillna('')

        # Format Currency (R$ X.XXX,XX)
        def format_currency(val):
            try:
                return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                return val

        num_cols = ['valorInicialCompra', 'valorFinalCompra']
        for col in num_cols:
            if col in self.df.columns:
                self.df[f"{col}_formatado"] = self.df[col].apply(format_currency)

    def get_refined_dataframe(self):
        """Returns the processed dataframe."""
        return self.df

    def save_refined_data(self, output_path):
        """Saves the refined dataframe to CSV."""
        if self.df is not None:
            self.df.to_csv(output_path, index=False, encoding='utf-8')
            logging.info(f"Saved refined data to {output_path}")
        else:
            logging.warning("No data to save.")

    def enrich_data(self):
        """Adds derived columns like contract type and UF."""
        if self.df is None:
            return

        logging.info("Enriching data with derived columns...")

        # 1. Classify Contract Type (Bens vs Serviços)
        def classify_type(row):
            text = str(row.get('objeto', '')).lower() + " " + str(row.get('compra_objeto', '')).lower()
            if any(x in text for x in ['aquisição', 'compra', 'fornecimento', 'bens', 'material']):
                return 'Aquisição de Bens'
            if any(x in text for x in ['serviço', 'prestação', 'manutenção', 'locação', 'consultoria', 'apoio']):
                return 'Prestação de Serviços'
            return 'Outros'

        self.df['tipo_contrato'] = self.df.apply(classify_type, axis=1)

        # 2. Extract UF from Unidade Gestora
        def extract_uf(row):
            # Try unidadegestora first, then compras
            ug = str(row.get('unidadeGestora', ''))
            ug_compras = str(row.get('unidadeGestoraCompras', ''))
            
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

        self.df['uf_gestora'] = self.df.apply(extract_uf, axis=1)

        # Cleanup: Drop original dictionary columns to keep refined CSV clean
        cols_to_drop = ['unidadeGestora', 'unidadeGestoraCompras']
        self.df = self.df.drop(columns=[c for c in cols_to_drop if c in self.df.columns], errors='ignore')

    def run_pipeline(self, output_path):
        """Executes the full transformation pipeline."""
        self.load_data()
        self.flatten_columns()
        self.clean_data()
        self.enrich_data()
        self.format_brazilian_standards()
        self.save_refined_data(output_path)
