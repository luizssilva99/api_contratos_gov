"""
Configurações centralizadas do projeto API Contratos Gov.

Este módulo contém todas as configurações necessárias para:
- Extração de dados da API
- Processamento e transformação
- Dashboard
- Caminhos de arquivos
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# ===== CONFIGURAÇÕES DA API =====
API_BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"
API_CONTRATOS_ENDPOINT = f"{API_BASE_URL}/contratos"
API_ORGAOS_ENDPOINT = f"{API_BASE_URL}/orgaos-siafi"

# Chave de API (deve estar no .env)
API_KEY = os.getenv("API_KEY", "")

# Headers padrão para requisições
API_HEADERS = {
    "chave-api-dados": API_KEY,
    "Accept": "application/json"
}

# Parâmetros de paginação
API_PAGE_SIZE = 500  # Tamanho da página para requisições
API_MAX_RETRIES = 3  # Número máximo de tentativas em caso de erro
API_RETRY_DELAY = 2  # Segundos entre tentativas

# ===== CONFIGURAÇÕES DE EXTRAÇÃO =====
DEFAULT_ORGAO = "20701"  # IBAMA
DEFAULT_DATA_FORMAT = "%d/%m/%Y"

# ===== CAMINHOS DE DIRETÓRIOS =====
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"

# Criar diretórios se não existirem
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ===== CAMINHOS DE ARQUIVOS =====
def get_raw_contracts_path(orgao: str) -> Path:
    """Retorna o caminho para o arquivo de contratos brutos."""
    return DATA_RAW_DIR / f"contratos_{orgao}_raw.csv"

def get_processed_contracts_path(orgao: str) -> Path:
    """Retorna o caminho para o arquivo de contratos processados."""
    return DATA_PROCESSED_DIR / f"contratos_{orgao}_refined.csv"

def get_orgaos_path() -> Path:
    """Retorna o caminho para o arquivo de órgãos SIAFI."""
    return DATA_RAW_DIR / "orgaos_siafi.csv"

# ===== CONFIGURAÇÕES DO DASHBOARD =====
DASHBOARD_TITLE = "Dashboard Contratos Gov"
DASHBOARD_ICON = "📊"
DASHBOARD_LAYOUT = "wide"
DASHBOARD_PORT = 8501

# ===== CONFIGURAÇÕES DE PROCESSAMENTO =====
# Colunas de data para formatação
DATE_COLUMNS = {
    'dataAssinatura': 'Data de Assinatura',
    'dataInicioVigencia': 'Início da Vigência',
    'dataFimVigencia': 'Fim da Vigência',
    'dataPublicacaoDOU': 'Publicação no DOU'
}

# Colunas a serem expandidas (nested objects)
NESTED_COLUMNS = ['unidadeGestora', 'unidadeGestoraCompras', 'fornecedor']

# ===== LOGGING =====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
