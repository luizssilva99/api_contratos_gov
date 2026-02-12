#!/usr/bin/env python3
"""
Script principal para executar o pipeline de extração de contratos.

Este é o ponto de entrada único para executar todo o processo de:
- Extração de dados da API do Portal da Transparência
- Transformação e limpeza dos dados
- Salvamento dos dados processados

Uso:
    python scripts/run_pipeline.py --orgao 20701
    python scripts/run_pipeline.py --orgao 20701 --data-inicial 01/01/2025 --data-final 31/12/2025
    python scripts/run_pipeline.py --help
"""

import argparse
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.runner import PipelineRunner
from config.settings import DEFAULT_ORGAO


def parse_arguments():
    """Parse argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Pipeline de extração e processamento de contratos governamentais",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Extrair todos os contratos do IBAMA
  python scripts/run_pipeline.py --orgao 20701
  
  # Extrair contratos de 2025
  python scripts/run_pipeline.py --orgao 20701 --data-inicial 01/01/2025 --data-final 31/12/2025
  
  # Extrair contratos de janeiro de 2026
  python scripts/run_pipeline.py --orgao 20701 --data-inicial 01/01/2026 --data-final 31/01/2026
        """
    )
    
    parser.add_argument(
        "--orgao",
        type=str,
        default=DEFAULT_ORGAO,
        help=f"Código do órgão SIAFI (padrão: {DEFAULT_ORGAO} - IBAMA)"
    )
    
    parser.add_argument(
        "--data-inicial",
        type=str,
        default=None,
        help="Data inicial no formato DD/MM/YYYY (opcional)"
    )
    
    parser.add_argument(
        "--data-final",
        type=str,
        default=None,
        help="Data final no formato DD/MM/YYYY (opcional)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Ativar modo verbose (mais detalhes no log)"
    )
    
    return parser.parse_args()


def main():
    """Função principal."""
    args = parse_arguments()
    
    # Configurar nível de log se verbose
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("=" * 70)
    print("Pipeline de Extração de Contratos Governamentais")
    print("=" * 70)
    print(f"Órgão: {args.orgao}")
    if args.data_inicial and args.data_final:
        print(f"Período: {args.data_inicial} a {args.data_final}")
    else:
        print("Período: Todos os contratos disponíveis")
    print("=" * 70)
    print()
    
    # Criar e executar o pipeline
    runner = PipelineRunner(
        orgao=args.orgao,
        data_inicial=args.data_inicial,
        data_final=args.data_final
    )
    
    success = runner.run()
    
    # Exibir resumo
    print()
    print("=" * 70)
    if success:
        summary = runner.get_execution_summary()
        print("✅ Pipeline executado com sucesso!")
        if "duration_seconds" in summary:
            print(f"⏱️  Tempo de execução: {summary['duration_seconds']:.2f}s")
    else:
        print("❌ Pipeline falhou. Verifique os logs acima para mais detalhes.")
    print("=" * 70)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
