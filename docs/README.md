# Documentação Técnica - API Contratos Gov

## Arquitetura do Sistema

### Visão Geral

O sistema é composto por três componentes principais:

1. **Pipeline de Extração** (`src/pipeline/`)
2. **Dashboard de Visualização** (`src/dashboard/`)
3. **Configurações Centralizadas** (`config/`)

### Fluxo de Dados

```
API Portal da Transparência
        ↓
   Extractors (src/pipeline/extractors/)
        ↓
   Dados Brutos (data/raw/)
        ↓
   Transformers (src/pipeline/transformers/)
        ↓
   Dados Processados (data/processed/)
        ↓
   Dashboard (src/dashboard/)
```

## Módulos

### Pipeline

#### Extractors

**`src/pipeline/extractors/contratos.py`**
- Extrai contratos da API do Portal da Transparência
- Suporta filtros por órgão e período
- Paginação automática
- Retry em caso de erro

**`src/pipeline/extractors/orgaos.py`**
- Extrai lista de órgãos SIAFI
- Usado para enriquecimento de dados

#### Transformers

**`src/pipeline/transformers/data_processor.py`**
- `flatten_nested_columns()`: Expande objetos JSON aninhados
- `clean_data_types()`: Limpa e converte tipos de dados
- `enrich_data()`: Adiciona campos derivados
- `format_to_brazilian_standards()`: Formata datas e valores

#### Runner

**`src/pipeline/runner.py`**
- Orquestra todo o pipeline
- Logging detalhado
- Tratamento de erros
- Geração de relatórios

### Dashboard

**`src/dashboard/app.py`**
- Interface Streamlit
- Duas abas: Visão Geral e Dados Detalhados
- Filtros dinâmicos
- Exportação de dados

**`src/dashboard/utils.py`**
- Funções auxiliares
- Formatação de dados
- Componentes reutilizáveis

### Configurações

**`config/settings.py`**
- URLs da API
- Caminhos de arquivos
- Parâmetros de extração
- Configurações do dashboard
- Logging

## Dados

### Estrutura dos Dados Brutos

Os dados brutos da API contêm:
- Informações do contrato (número, valor, datas)
- Unidade Gestora (objeto aninhado)
- Unidade Gestora de Compras (objeto aninhado)
- Fornecedor (objeto aninhado)
- Informações da compra

### Estrutura dos Dados Processados

Após o processamento:
- Objetos aninhados são expandidos em colunas
- Datas formatadas (DD/MM/YYYY)
- Valores formatados (R$ X.XXX,XX)
- Campos derivados adicionados:
  - `ano_assinatura`
  - `tipo_contrato`
  - `uf_gestora`
  - `nome_fornecedor`

### Colunas Principais

**Contrato:**
- id, numero, numeroProcesso
- situacaoContrato, modalidadeCompra
- objeto, fundamentoLegal
- valorInicialCompra, valorFinalCompra
- dataAssinatura, dataInicioVigencia, dataFimVigencia

**Unidade Gestora:**
- ug_codigo, ug_nome, ug_poder
- ug_orgao_vinculado, ug_orgao_maximo

**Fornecedor:**
- fornecedor_id, fornecedor_nome
- fornecedor_cpfFormatado, fornecedor_cnpjFormatado
- fornecedor_razaoSocialReceita

## Scripts

### `scripts/run_pipeline.py`

Script principal para executar o pipeline.

**Argumentos:**
- `--orgao`: Código do órgão SIAFI (padrão: 20701)
- `--data-inicial`: Data inicial (DD/MM/YYYY)
- `--data-final`: Data final (DD/MM/YYYY)
- `-v, --verbose`: Modo verbose

**Exemplos:**
```bash
python scripts/run_pipeline.py --orgao 20701
python scripts/run_pipeline.py --orgao 20701 --data-inicial 01/01/2025 --data-final 31/12/2025
```

## Deployment

### Requisitos

- Python 3.8+
- Chave de API do Portal da Transparência
- Mínimo 2GB RAM
- 1GB espaço em disco

### Variáveis de Ambiente

```env
API_KEY=sua_chave_api
LOG_LEVEL=INFO
```

### Executar em Produção

1. Clone o repositório
2. Configure `.env`
3. Instale dependências: `pip install -r requirements.txt`
4. Execute pipeline: `python scripts/run_pipeline.py --orgao 20701`
5. Inicie dashboard: `streamlit run src/dashboard/app.py --server.port 8501`

### Docker (Futuro)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "src/dashboard/app.py"]
```

## Manutenção

### Atualizar Dados

Execute o pipeline periodicamente:
```bash
python scripts/run_pipeline.py --orgao 20701
```

### Logs

Logs são exibidos no console. Para salvar:
```bash
python scripts/run_pipeline.py --orgao 20701 > pipeline.log 2>&1
```

### Backup

Faça backup regular de:
- `data/processed/` - Dados processados
- `.env` - Configurações sensíveis

## Troubleshooting

### Problema: ImportError

**Solução**: Certifique-se de estar no diretório raiz e com ambiente virtual ativado.

### Problema: API retorna 400

**Solução**: Verifique a chave de API e tente com período menor.

### Problema: Dashboard não carrega

**Solução**: Execute o pipeline primeiro para gerar os dados.

## Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'feat: adicionar nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## Roadmap

- [ ] Testes unitários
- [ ] CI/CD com GitHub Actions
- [ ] Docker e Docker Compose
- [ ] Suporte a múltiplos órgãos
- [ ] Cache de dados
- [ ] API REST própria
