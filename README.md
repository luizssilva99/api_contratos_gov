# 🏛️ API Contratos Gov - Agente de Extração de Dados

Este projeto implementa uma arquitetura de agente inteligente de 3 camadas para extração, processamento e análise de dados governamentais do Portal da Transparência do Governo Federal.

## 🏗 Arquitetura do Sistema

O projeto adota uma estrutura robusta baseada em **Diretivas**, **Orquestração** e **Execução**, conforme definido em `agente.md`:

1.  **📜 Diretivas (`directives/`)**:
    *   SOPs (Procedimentos Operacionais Padrão) em Markdown.
    *   Definem *o que* deve ser feito, inputs, outputs e regras de negócio.
2.  **🧠 Orquestração (Agente de IA)**:
    *   O agente lê as diretivas e determina o fluxo de execução.
3.  **⚙️ Execução (`execution/`)**:
    *   Scripts Python determinísticos e otimizados.
    *   Responsáveis pela interação com APIs, tratamento de dados e geração de arquivos.

---

## 🚀 Guia de Instalação

### Pré-requisitos
*   **Python 3.8** ou superior.
*   **Chave de API** do Portal da Transparência ([Obtenha aqui](https://www.portaldatransparencia.gov.br/api-de-dados)).

### 🐧 Instalação no Linux (Ubuntu/Debian)

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/luizssilva99/api_contratos_gov.git
    cd api_contratos_gov
    ```

2.  **Instale as dependências do sistema (opcional, mas recomendado):**
    ```bash
    sudo apt update
    sudo apt install python3-pip python3-venv
    ```

3.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  **Instale os pacotes Python:**
    ```bash
    pip install requests
    ```

5.  **Configure o ambiente:**
    *   Crie o arquivo `.env`:
        ```bash
        touch .env
        ```
    *   Adicione sua chave de API ao arquivo `.env`:
        ```env
        PORTAL_TRANSPARENCIA_API_KEY=sua_chave_aqui_sem_aspas
        ```

### 🪟 Instalação no Windows

1.  **Clone o repositório:**
    *   Abra o **PowerShell** ou **Git Bash**.
    ```bash
    git clone https://github.com/luizssilva99/api_contratos_gov.git
    cd api_contratos_gov
    ```

2.  **Crie e ative um ambiente virtual:**
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
    *   *Nota: Se houver erro de permissão, execute `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` no PowerShell.*

3.  **Instale os pacotes Python:**
    ```powershell
    pip install requests
    ```

4.  **Configure o ambiente:**
    *   Crie um arquivo chamado `.env` na raiz do projeto.
    *   Abra-o com o Bloco de Notas e adicione:
        ```env
        PORTAL_TRANSPARENCIA_API_KEY=sua_chave_aqui_sem_aspas
        ```

---

## 🛠 Como Executar

O projeto possui scripts específicos na pasta `execution/` para diferentes tipos de dados.

### 1. Extração de Órgãos do SIAFI
Extrai a lista completa de órgãos cadastrados no SIAFI.

*   **Comando:**
    ```bash
    python execution/extract_orgaos_siafi.py --output .tmp/orgaos_siafi.csv
    ```

*   **Comando Básico:**
    ```bash
    python execution/extract_contratos.py --orgao 20701 --output-dir .tmp
    ```
*   **Comando com Filtro de Data (Recomendado):**
    ```bash
    python execution/extract_contratos.py --orgao 20701 --output-dir .tmp --data-inicial 01/01/2023 --data-final 31/12/2023
    ```
    *   **Resultados:**
        *   `.tmp/contratos_20701_raw.csv`: Dados brutos da API.
        *   `.tmp/contratos_20701_refined.csv`: Dados transformados e formatados (padrão Brasil).

---

## 📂 Estrutura de Diretórios

```plaintext
api_contratos_gov/
├── directives/       # 📜 Instruções de trabalho (SOPs)
│   ├── extract_orgaos_siafi.md
│   └── extract_contratos_20701.md
├── execution/        # ⚙️ Scripts de automação Python
│   ├── extract_orgaos_siafi.py
│   └── extract_contratos.py
├── .tmp/             # 🗑️ Arquivos temporários (CSV, JSON) - Ignorados pelo Git
├── .env              # 🔐 Chaves de API e Segredos - Ignorado pelo Git
├── agente.md         # 🧠 Definição do comportamento do Agente
└── README.md         # 📘 Documentação do Projeto
```

## 🛡 Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.
