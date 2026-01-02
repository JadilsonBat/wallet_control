# Controle de Investimentos (Local)

Sistema local em Streamlit para substituir a planilha `Investimentos.xlsx`, com persistência em SQLite e dashboards interativos.

## Requisitos
- Python 3.10+
- Linux (Fedora/Ubuntu)

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução
```bash
streamlit run app.py
```

## Importar a planilha
Você pode importar pelo app (página **Transações**) ou via CLI:
```bash
python import_excel.py /caminho/para/Investimentos.xlsx
```

## SQLite
O banco é salvo em `data/portfolio.db`.
Para apontar outro caminho, defina a variável de ambiente:
```bash
export WALLET_DB_PATH=/caminho/para/arquivo.db
```

## Estrutura do projeto
- `app.py`: entrada do Streamlit.
- `pages/`: páginas do app (Visão Geral, Transações, Proventos, Ativos, Comparação CDI, Dashboard).
- `src/`: modelos, serviços e utilitários.
- `import_excel.py`: importador da planilha.

## Cálculos
- **Preço médio**: método de preço médio por ativo (compras somam custo; vendas reduzem custo pela média).
- **Investido líquido**: compras menos vendas, considerando `valor_total`.
- **Curva do patrimônio**: usa preços de transações como proxy quando não há histórico de preços.

## Testes
```bash
pytest
```
