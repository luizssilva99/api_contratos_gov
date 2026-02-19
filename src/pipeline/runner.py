"""
Orquestrador do pipeline de extração e processamento de contratos.

Este módulo coordena a execução de todas as etapas do pipeline:
1. Extração de dados da API
2. Transformação e limpeza
3. Salvamento dos dados processados
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Adicionar o diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import (
    get_raw_contracts_path,
    get_processed_contracts_path,
    LOG_LEVEL,
    LOG_FORMAT
)
from src.pipeline.extractors.contratos import extract_contracts
from src.pipeline.transformers.data_processor import (
    load_data,
    flatten_nested_columns,
    clean_data_types,
    enrich_data,
    format_to_brazilian_standards,
    save_refined_data
)

# Configurar logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class PipelineRunner:
    """Orquestrador do pipeline de extração e processamento."""
    
    def __init__(self, orgao: str, data_inicial: str = None, data_final: str = None):
        """
        Inicializa o runner do pipeline.
        
        Args:
            orgao: Código do órgão SIAFI
            data_inicial: Data inicial no formato DD/MM/YYYY (opcional)
            data_final: Data final no formato DD/MM/YYYY (opcional)
        """
        self.orgao = orgao
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.start_time = None
        self.end_time = None
        
    def run(self) -> bool:
        """
        Executa o pipeline completo.
        
        Returns:
            True se executado com sucesso, False caso contrário
        """
        self.start_time = datetime.now()
        logger.info(f"Iniciando pipeline para órgão {self.orgao}")
        
        try:
            # Etapa 1: Extração
            logger.info("Etapa 1/5: Extraindo dados da API...")
            raw_path = self._extract_data()
            if not raw_path:
                logger.error("Falha na extração de dados")
                return False
            
            # Etapa 2: Carregamento
            logger.info("Etapa 2/5: Carregando dados brutos...")
            df = load_data(raw_path)
            if df.empty:
                logger.warning("Nenhum dado foi extraído")
                return False
            logger.info(f"Carregados {len(df)} registros")
            
            # Etapa 3: Transformação
            logger.info("Etapa 3/5: Expandindo colunas aninhadas...")
            df = flatten_nested_columns(df)
            
            logger.info("Etapa 4/5: Limpando e enriquecendo dados...")
            df = clean_data_types(df)
            df = enrich_data(df)
            df = format_to_brazilian_standards(df)
            
            # Etapa 5: Salvamento
            logger.info("Etapa 5/5: Salvando dados processados...")
            processed_path = get_processed_contracts_path(self.orgao)
            save_refined_data(df, processed_path)
            
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            logger.info(f"Pipeline concluído com sucesso em {duration:.2f}s")
            logger.info(f"Dados processados salvos em: {processed_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro durante execução do pipeline: {str(e)}", exc_info=True)
            return False
    
    def _extract_data(self) -> Path:
        """
        Executa a extração de dados da API.
        
        Returns:
            Caminho do arquivo de dados brutos ou None em caso de erro
        """
        raw_path = get_raw_contracts_path(self.orgao)
        
        success = extract_contracts(
            orgao_codigo=self.orgao,
            output_file=str(raw_path),
            data_inicial=self.data_inicial,
            data_final=self.data_final
        )
        
        if not success:
            logger.warning(f"Falha na extração de dados da API. Verificando existência de cache local em: {raw_path}")
            if raw_path.exists():
                logger.info("Cache encontrado! Prosseguindo com dados locais.")
                return raw_path
            else:
                logger.error("Cache local não encontrado. Impossível continuar.")
                return None
        
        return raw_path
    
    def get_execution_summary(self) -> dict:
        """
        Retorna um resumo da execução do pipeline.
        
        Returns:
            Dicionário com informações da execução
        """
        if not self.start_time:
            return {"status": "not_started"}
        
        summary = {
            "orgao": self.orgao,
            "start_time": self.start_time.isoformat(),
            "status": "completed" if self.end_time else "running"
        }
        
        if self.end_time:
            summary["end_time"] = self.end_time.isoformat()
            summary["duration_seconds"] = (self.end_time - self.start_time).total_seconds()
        
        return summary


if __name__ == "__main__":
    # Exemplo de uso direto
    runner = PipelineRunner(orgao="20701")
    success = runner.run()
    sys.exit(0 if success else 1)
