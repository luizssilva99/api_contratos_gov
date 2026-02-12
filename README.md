# API Contratos Gov

Sistema completo de extração, processamento e visualização de contratos governamentais do Portal da Transparência.

## 🚀 Características

- **Pipeline Automatizado**: Extração e processamento com um único comando
- **Dashboard Interativo**: Visualização rica de dados com Streamlit
- **Dados Limpos**: Transformação automática e padronização
- **Estrutura Profissional**: Código organizado e modular
- **Pronto para Produção**: Configurações centralizadas e logging

## 📁 Estrutura do Projeto

```
api_contratos_gov/
├── src/                    # Código-fonte
│   ├── pipeline/          # Pipeline de ETL
│   │   ├── extractors/   # Extração de dados
│   │   ├── transformers/ # Transformação de dados
│   │   └── runner.py     # Orquestrador
│   └── dashboard/        # Dashboard Streamlit
├── config/                # Configurações
├── scripts/               # Scripts de automação
├── data/                  # Dados (gitignored)
│   ├── raw/              # Dados brutos
│   └── processed/        # Dados processados
├── docs/                  # Documentação
└── tests/                 # Testes
```

## 🔧 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/luizssilva99/api_contratos_gov.git
cd api_contratos_gov
```

### 2. Criar Ambiente Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
API_KEY=sua_chave_api_aqui
LOG_LEVEL=INFO
```

> **Nota**: Obtenha sua chave de API em: https://portaldatransparencia.gov.br/api-de-dados

## 📊 Uso

### Executar Pipeline Completo (Comando Único)

```bash
# Extrair todos os contratos do IBAMA (órgão 20701)
python scripts/run_pipeline.py --orgao 20701

# Extrair contratos de um período específico
python scripts/run_pipeline.py --orgao 20701 --data-inicial 01/01/2025 --data-final 31/12/2025

# Ver todas as opções
python scripts/run_pipeline.py --help
```

### Executar Dashboard

```bash
streamlit run src/dashboard/app.py
```

O dashboard estará disponível em: http://localhost:8501

## 🔄 Pipeline de Dados

O pipeline executa automaticamente as seguintes etapas:

1. **Extração**: Busca dados da API do Portal da Transparência
2. **Transformação**: Expande colunas aninhadas e limpa dados
3. **Enriquecimento**: Adiciona campos derivados (ano, tipo de contrato, etc.)
4. **Formatação**: Padroniza para formato brasileiro
5. **Salvamento**: Gera arquivo CSV processado

## 📈 Dashboard

O dashboard oferece:

- **Visão Geral**: KPIs, gráficos de distribuição e evolução temporal
- **Dados Detalhados**: Tabela completa com paginação e exportação CSV
- **Filtros Avançados**: Por ano, situação, modalidade, UF e fornecedor
- **Exportação**: Download de dados formatados

## 🛠️ Desenvolvimento

### Estrutura de Código

- `src/pipeline/extractors/`: Módulos de extração de APIs
- `src/pipeline/transformers/`: Processamento e limpeza de dados
- `src/pipeline/runner.py`: Orquestrador do pipeline
- `src/dashboard/`: Aplicação Streamlit
- `config/settings.py`: Configurações centralizadas

### Adicionar Novo Extractor

1. Criar arquivo em `src/pipeline/extractors/`
2. Implementar função de extração
3. Adicionar ao `runner.py`

### Adicionar Nova Transformação

1. Criar função em `src/pipeline/transformers/`
2. Adicionar ao fluxo em `runner.py`

## 📝 Configurações

Todas as configurações estão em `config/settings.py`:

- URLs da API
- Caminhos de diretórios
- Parâmetros de extração
- Configurações do dashboard

## 🐛 Troubleshooting

### Erro 400 na API

A API pode retornar erro 400 se:
- A chave de API está inválida
- O período solicitado é muito amplo
- O órgão não existe

**Solução**: Tente com um período menor ou verifique a chave de API.

### Dashboard não carrega dados

Certifique-se de que:
1. O pipeline foi executado com sucesso
2. Os arquivos estão em `data/processed/`
3. O caminho está correto em `config/settings.py`

## 📄 Licença

Este projeto é de código aberto para fins educacionais e de transparência.

## 👤 Autor

**Luiz Fernando**
- GitHub: [@luizssilva99](https://github.com/luizssilva99)

## 🙏 Agradecimentos

- Portal da Transparência do Governo Federal
- Comunidade Streamlit
- Comunidade Python
