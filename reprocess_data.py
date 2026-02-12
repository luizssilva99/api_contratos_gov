import os
import logging
from execution.transformers import ContractTransformer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_file = os.path.join(base_dir, '.tmp', 'contratos_20701_raw.csv')
    refined_file = os.path.join(base_dir, '.tmp', 'contratos_20701_refined.csv')

    print(f"Reprocessing data from {raw_file}...")
    
    if not os.path.exists(raw_file):
        print(f"Error: Raw file not found at {raw_file}")
        return

    transformer = ContractTransformer(raw_file)
    transformer.run_pipeline(refined_file)
    print(f"Successfully saved enriched data to {refined_file}")

if __name__ == "__main__":
    main()
