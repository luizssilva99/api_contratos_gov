import argparse
import requests
import json
import os
import csv
import time
from transformers import ContractTransformer

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

def fetch_data(orgao_codigo, raw_output_file, refined_output_file, data_inicial=None, data_final=None):
    if not API_KEY:
        print("Error: PORTAL_TRANSPARENCIA_API_KEY not found in .env")
        exit(1)

    base_url = "https://api.portaldatransparencia.gov.br/api-de-dados/contratos"
    headers = {
        "accept": "*/*",
        "chave-api-dados": API_KEY
    }

    all_data = []
    page = 1
    
    msg = f"Starting extraction for organ {orgao_codigo}"
    if data_inicial and data_final:
        msg += f" from {data_inicial} to {data_final}"
    print(msg + "...")

    # Extraction Loop
    while True:
        try:
            url = f"{base_url}?codigoOrgao={orgao_codigo}&pagina={page}"
            if data_inicial and data_final:
                url += f"&dataInicial={data_inicial}&dataFinal={data_final}"
            
            print(f"Fetching page {page}...", end="\r")
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                 print(f"\nError fetching page {page}: {response.status_code} - {response.text}")
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
            break

    # Save RAW Data
    if all_data:
        print(f"\nExtracted {len(all_data)} raw records.")
        os.makedirs(os.path.dirname(raw_output_file), exist_ok=True)
        
        # Determine fields for CSV
        fieldnames = set()
        for item in all_data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(raw_output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
        print(f"Saved RAW data to {raw_output_file}")
        
        # Transform Data
        print("Starting transformation pipeline...")
        transformer = ContractTransformer(raw_output_file)
        transformer.run_pipeline(refined_output_file)
        print(f"Saved REFINED data to {refined_output_file}")
        
    else:
        print("\nNo data extracted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and Transform Contratos data.")
    parser.add_argument("--orgao", default="20701", help="The organ code.")
    parser.add_argument("--data-inicial", help="Start date (DD/MM/YYYY). Optional.")
    parser.add_argument("--data-final", help="End date (DD/MM/YYYY). Optional.")
    parser.add_argument("--output-dir", default=".tmp", help="Directory to save output files.")
    
    args = parser.parse_args()
    
    raw_path = os.path.join(args.output_dir, f"contratos_{args.orgao}_raw.csv")
    refined_path = os.path.join(args.output_dir, f"contratos_{args.orgao}_refined.csv")
    
    fetch_data(args.orgao, raw_path, refined_path, args.data_inicial, args.data_final)
