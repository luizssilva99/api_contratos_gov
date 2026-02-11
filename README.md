# API Contratos Gov - Agente de Extração de Dados

Este projeto utiliza uma arquitetura de agente de 3 camadas para extrair e processar dados de APIs do governo brasileiro, especificamente do Portal da Transparência.

## 🏗 Arquitetura

O projeto segue a estrutura definida em `agente.md`:

1.  **Diretivas (`directives/`)**: Instruções (SOPs) em Markdown que definem *o que* deve ser feito.
2.  **Orquestração (Agente)**: O agente de IA lê as diretivas e decide quais scripts executar.
3.  **Execução (`execution/`)**: Scripts Python determinísticos que realizam o trabalho pesado (extração de dados, processamento, etc.).

## 🚀 Como Começar

### Pré-requisitos

-   Python 3.8+
-   Chave de API do Portal da Transparência (cadastre-se em [portaldatransparencia.gov.br](https://www.portaldatransparencia.gov.br/api-de-dados))

### Instalação

1.  Clone o repositório.
2.  Configure as variáveis de ambiente:
    ```bash
    cp .env.example .env  # Se houver um exemplo, ou crie manualmente
    ```
    Edite o arquivo `.env` e adicione sua chave de API:
    ```env
    PORTAL_TRANSPARENCIA_API_KEY=sua_chave_aqui
    ```

### Uso

Para executar a extração de dados dos Órgãos do SIAFI manualmente:

```bash
python3 execution/extract_orgaos_siafi.py --output .tmp/orgaos_siafi.csv
```

O script irá:
1.  Ler a chave da API do arquivo `.env`.
2.  Iterar por todas as páginas disponíveis na API.
3.  Salvar os dados consolidados em `.tmp/orgaos_siafi.csv`.

## 📂 Estrutura de Arquivos

```
├── directives/       # Procedimentos Operacionais Padrão (SOPs)
├── execution/        # Scripts Python para tarefas específicas
├── .tmp/             # Arquivos temporários e saídas de dados (não commitados)
├── agente.md         # Definição da arquitetura do agente
└── README.md         # Documentação do projeto
```

## 🛡 Licença

[Inserir Licença Aqui]
