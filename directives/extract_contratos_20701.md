# Directive: Extract and Transform Contratos Data (Órgão 20701)

## Goal
Extract contract data for "Ministério da Justiça e Segurança Pública" (ID 20701) from the Portal da Transparência API, save the raw data, and then process it using a dedicated Transformer class to produce a refined, dashboard-ready dataset.

## Inputs
- API Endpoint: `https://api.portaldatransparencia.gov.br/api-de-dados/contratos`
- Organ Code: `20701`
- Output Directory: `.tmp/`
- Environment Variable: `PORTAL_TRANSPARENCIA_API_KEY` (required)

## Execution Steps
1.  Check if `execution/extract_contratos.py` and `execution/transformers.py` exist.
2.  Run `python3 execution/extract_contratos.py --orgao 20701 --output-dir .tmp`
3.  The script will:
    -   **Extract**: Fetch data from API and save to `.tmp/contratos_20701_raw.csv`.
    -   **Transform**: Instantiate `ContractTransformer`, process the raw file (flatten dictionaries, clean types, format to Brazilian standards), and save to `.tmp/contratos_20701_refined.csv`.

## Outputs
-   **RAW File**: `.tmp/contratos_20701_raw.csv` (Original API response)
-   **REFINED File**: `.tmp/contratos_20701_refined.csv` (Cleaned, enriched, and formatted)

## Formatting Standards
-   **Dates**: `DD/MM/YYYY` (in `_formatada` columns)
-   **Currency**: `R$ X.XXX,XX` (in `_formatado` columns)
