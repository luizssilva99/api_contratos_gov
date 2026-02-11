# Directive: Extract Orgaos SIAFI Data

## Goal
Extract all records from the "Órgãos do SIAFI" API (Portal da Transparência) and save them to a consolidated CSV file.

## Inputs
- API Endpoint: `https://api.portaldatransparencia.gov.br/api-de-dados/orgaos-siafi`
- Output File: `.tmp/orgaos_siafi.csv`
- Environment Variable: `PORTAL_TRANSPARENCIA_API_KEY` (required for authentication)

## Execution Steps
1.  Check if `execution/extract_orgaos_siafi.py` exists.
2.  Run `python3 execution/extract_orgaos_siafi.py --output <Output File>`
3.  The script should:
    -   Read the API key from the environment.
    -   Iterate through pages (starting at 1) until no more data is returned.
    -   Consolidate all records.
    -   Save to the output CSV file.

## Edge Cases
-   **API Limits**: Respect rate limits if applicable (though this API is generally open with a key).
-   **Errors**: If a page fails, retry 3 times before aborting. Log the error.
-   **Empty Response**: If the first page returns no data, verify the API key and endpoint.
