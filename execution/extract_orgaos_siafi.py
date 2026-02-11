import argparse
import requests
import json
import os
import csv
import time

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

def fetch_data(output_file):
    if not API_KEY:
        print("Error: PORTAL_TRANSPARENCIA_API_KEY not found in .env")
        exit(1)

    base_url = "https://api.portaldatransparencia.gov.br/api-de-dados/orgaos-siafi"
    headers = {
        "accept": "*/*",
        "chave-api-dados": API_KEY
    }

    all_data = []
    page = 1
    
    print(f"Starting extraction from {base_url}...")

    while True:
        try:
            url = f"{base_url}?pagina={page}"
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
            
            # Gentle delay to avoid hitting rate limits
            time.sleep(0.5)

        except Exception as e:
            print(f"\nException occurred: {e}")
            break

    if all_data:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Get field names from the first record
        fieldnames = all_data[0].keys()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
            
        print(f"\nSuccessfully extracted {len(all_data)} records to {output_file}")
    else:
        print("\nNo data extracted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Orgaos SIAFI data from Portal da Transparencia.")
    parser.add_argument("--output", required=True, help="The CSV file path to save the data.")
    args = parser.parse_args()
    
    fetch_data(args.output)
