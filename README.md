# AnaliseTermicaScript

Projeto de analise termica em Python usando Jupyter Notebook.

## Estrutura

- `thermala_ analisys.ipynb`: notebook principal da analise.
- `requirements.txt`: dependencias Python do projeto.
- `data/`: arquivos de entrada de dados (ignorado no Git por padrao).

## Requisitos

- Python 3.10+
- pip

## Instalacao

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Como usar

1. Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

2. Inicie o Jupyter Notebook:

```bash
jupyter notebook
```

3. Abra o arquivo `thermala_ analisys.ipynb` e execute as celulas na ordem.

## Dependencias

- numpy
- pandas
- matplotlib
- openpyxl

## Observacoes

- O diretorio `data/` esta no `.gitignore`. Se quiser versionar os dados, ajuste o arquivo `.gitignore`.
- O notebook pode depender de arquivos da pasta `data/` com nomes especificos.
