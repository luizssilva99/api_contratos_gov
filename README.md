# 🏛️ Dashboard de Contratos Governamentais (Projeto de Estudo)

Este projeto é um estudo de caso focado na extração, transformação e visualização de dados públicos provenientes do **Portal da Transparência do Governo Federal**. O objetivo principal é demonstrar a viabilidade de transformar dados brutos de APIs governamentais em informações estratégicas e visuais para análise de conformidade e gastos públicos.

## 🎯 Objetivo do Projeto
O projeto foi desenvolvido para explorar técnicas de ETL (Extract, Transform, Load) e visualização de dados, utilizando uma arquitetura modular que garante a integridade e a padronização das informações de contratos públicos, especificamente focada em órgãos do governo (ex: IBAMA).

## 🏗️ Arquitetura e Fluxo de Dados
O sistema é estruturado em três estágios principais:

1.  **Extração**: Consumo da API de Dados do Portal da Transparência, lidando com paginação e armazenamento de dados brutos (Raw Data) em conformidade com as restrições da API.
2.  **Transformação (ETL)**: Uma camada robusta de processamento que:
    *   Padroniza formatos de data (padrão brasileiro DD/MM/AAAA).
    *   Converte valores monetários para a moeda local (BRL).
    *   "Achata" (Flatten) estruturas JSON complexas, transformando dados aninhados (Unidade Gestora, Fornecedores) em colunas relacionais.
    *   Classifica automaticamente os contratos entre "Aquisição de Bens" e "Prestação de Serviços" através de análise de texto.
3.  **Visualização**: Um dashboard interativo desenvolvido em Streamlit que oferece uma visão gerencial e detalhada dos dados processados.

## 📊 Principais Funcionalidades do Dashboard
*   **Visão Geral Estratégica**: KPIs em tempo real mostrando o valor total contratado, volume de contratos e distribuição por tipo.
*   **Análise Temporal**: Gráficos de evolução histórica que permitem visualizar tendências de gastos ao longo dos anos.
*   **Filtros Inteligentes**: Capacidade de filtrar por estado (UF), fornecedor, modalidade de contratação e status.
*   **Dados Detalhados**: Uma tabela paginada com todas as informações tratadas, permitindo a exploração individual de cada contrato.
*   **Exportação**: Ferramenta de exportação para CSV formatado, facilitando o uso dos dados tratados em outras ferramentas como Excel.

## 🛠️ Tecnologias Utilizadas
*   **Linguagem**: Python 3.11+
*   **Manipulação de Dados**: Pandas
*   **Visualização**: Streamlit e Plotly
*   **Comunicação**: Requests (API HTTP)
*   **Formatação**: Regex e Ast para tratamento de strings complexas

## 📒 Nota de Estudo
Como este é um projeto educacional, ele prioriza a clareza do código e a separação de responsabilidades (Camada de Extração vs Camada de Transformação) em detrimento de uma interface de produção complexa. Os dados utilizados são reais e provenientes de fontes oficiais.
