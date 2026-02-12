import pandas as pd
import re
import ast

def clean_value(val):
    if pd.isna(val): return ""
    val = str(val).strip()
    
    # regex matches:
    # 1. Objeto: (case insensitive)
    # 2. Potential modality like "Pregão Eletrônico - " or just the dash
    # We want to remove "Objeto:" and if it's followed by a dash, remove up to the dash.
    
    # First, remove "Objeto:" prefix
    val = re.sub(r'^\s*Objeto\s*:\s*', '', val, flags=re.IGNORECASE).strip()
    
    # Then, if it starts with "Pregão Eletrônico - " or similar dash pattern, remove it
    # We only remove up to the first dash if it's within the first 50 chars (safety)
    match = re.match(r'^[^:]*?\-\s*', val)
    if match and len(match.group(0)) < 50:
         # Check if the part before the dash looks like a modality (Pregão, Inexigibilidade, etc)
         modality_keywords = ['pregão', 'inexigibilidade', 'dispensa', 'convite', 'tomada', 'concorrência']
         prefix = match.group(0).lower()
         if any(k in prefix for k in modality_keywords):
             val = val[len(match.group(0)):].strip()
    
    return val

# Test with samples
samples = [
    "Objeto: Pregão Eletrônico -  Contratação de empresa para prestação de serviços...",
    "Objeto: SERVIÇO DE DEDETIZAÇÃO",
    "Objeto: Contratação de serviço...",
    "Objeto: Inexigibilidade -  Prestação de serviço...",
    "PREGÃO ELETRÔNICO - Aquisição de mobiliário"
]

print("Testing cleaning logic:")
for s in samples:
    print(f"Input:  {s}")
    print(f"Output: {clean_value(s)}")
    print("-" * 20)
