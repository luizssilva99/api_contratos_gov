import argparse
import requests
import json
import os
import csv
import time
import sys
from pathlib import Path

# Adicionar raiz ao path para permitir imports absolutos se executado diretamente
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))


# Load environment variables manually
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

API_KEY = os.getenv("PORTAL_TRANSPARENCIA_API_KEY")


def extract_contracts(orgao_codigo, output_file, data_inicial=None, data_final=None):
    """
    Extrai contratos da API do Portal da Transparência.
    
    Args:
        orgao_codigo: Código do órgão
        output_file: Caminho para salvar o arquivo CSV bruto
        data_inicial: Data inicial (DD/MM/YYYY)
        data_final: Data final (DD/MM/YYYY)
        
    Returns:
        bool: True se extração bem sucedida (mesmo que vazia), False se erro crítico
    """
    if not API_KEY:
        print("Error: PORTAL_TRANSPARENCIA_API_KEY not found in .env")
        return False

    base_url = "https://api.portaldatransparencia.gov.br/api-de-dados/contratos"
    headers = {
        "accept": "*/*",
        "chave-api-dados": API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    all_data = []
    page = 1
    
    msg = f"Starting extraction for organ {orgao_codigo}"
    if data_inicial and data_final:
        msg += f" from {data_inicial} to {data_final}"
    print(msg + "...")

    # Extraction Loop
    success = True
    while True:
        try:
            url = f"{base_url}?codigoOrgao={orgao_codigo}&pagina={page}"
            if data_inicial and data_final:
                url += f"&dataInicial={data_inicial}&dataFinal={data_final}"
            
            print(f"Fetching page {page}...", end="\r")
            
            # Rate limiting: 1 request per second (conservative to avoid blocks)
            # API Limit: 180-700 req/min depending on time/endpoint. 60 req/min is safe.
            time.sleep(1.0)
            
            try:
                response = requests.get(url, headers=headers, verify=False, timeout=30)
            except requests.exceptions.RequestException as e:
                print(f"\nNetwork error fetching page {page}: {e}")
                time.sleep(5) # Wait before retry or break
                break

            if response.status_code == 429:
                print(f"\nRate limit exceeded (429). Waiting 60 seconds...")
                time.sleep(60)
                continue # Retry same page (would need loop restructuring, simply breaking for now or implementing cleaner retry)

            if response.status_code != 200:
                 print(f"\nError fetching page {page}: {response.status_code} - {response.text}")
                 # If error is 400 and message is generic, maybe we hit a soft block
                 if response.status_code == 400:
                     print("API returned 400. This might be a block or invalid parameter. Stopping.")
                 break

            data = response.json()

            if not data:
                print(f"\nNo more data found at page {page}. Stopping.")
                break

            all_data.extend(data)
            page += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"\nException occurred: {e}")
            success = False
            break

    # Save RAW Data
    if all_data:
        print(f"\nExtracted {len(all_data)} raw records.")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Determine fields for CSV
        fieldnames = set()
        for item in all_data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_data)
            print(f"Saved RAW data to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
        
    else:
        print("\nNo data extracted.")
        # If successfully attempted but no data, returns True (empty result is valid result)
        # Unless 'success' flag was set to False by exception
        return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Contratos data.")
    parser.add_argument("--orgao", default="20701", help="The organ code.")
    parser.add_argument("--data-inicial", help="Start date (DD/MM/YYYY). Optional.")
    parser.add_argument("--data-final", help="End date (DD/MM/YYYY). Optional.")
    parser.add_argument("--output-dir", default=".tmp", help="Directory to save output files.")
    
    args = parser.parse_args()
    
    # Path construction for standalone run
    raw_path = os.path.join(args.output_dir, f"contratos_{args.orgao}_raw.csv")
    
    extract_contracts(args.orgao, raw_path, args.data_inicial, args.data_final)

