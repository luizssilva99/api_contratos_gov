# Directive: Extract Contratos Data (Órgão 20701)

## Goal
Extract all contracts for a specific government organ (default: 20701) from the "Contratos" API (Portal da Transparência) and save them to a consolidated CSV file.

## Inputs
- API Endpoint: `https://api.portaldatransparencia.gov.br/api-de-dados/contratos`
- Default Organ Code (`codigoOrgao`): `20701`
- Output File: `.tmp/contratos_20701.csv`
- Environment Variable: `PORTAL_TRANSPARENCIA_API_KEY` (required for authentication)

## Execution Steps
1.  Check if `execution/extract_contratos.py` exists.
2.  Run `python3 execution/extract_contratos.py --orgao 20701 --output <Output File>`
3.  The script should:
    -   Read the API key from the environment.
    -   Iterate through pages (starting at 1) with `codigoOrgao=20701` until no more data is returned.
    -   Consolidate all records.
    -   Save to the output CSV file.

## Edge Cases
-   **API Limits**: Respect rate limits (add delays).
-   **Pagination**: Continue fetching until an empty list is returned.
-   **Errors**: Retry on network failures.
