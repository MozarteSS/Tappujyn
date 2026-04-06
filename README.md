# AnaliseTermicaScript

Projeto de analise termica em Python usando Jupyter Notebook.

## Estrutura

- `thermal_analysis.ipynb`: notebook principal da analise.
- `requirements.txt`: dependencias Python do projeto.
- `data/`: arquivos de entrada de dados (ignorado no Git por padrao).

## Requisitos

- Python 3.10+
- pip

## Instalacao

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Windows (Prompt de Comando - CMD)

```bat
py -m venv .venv
.venv\Scripts\activate.bat
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

3. Abra o arquivo `thermal_analysis.ipynb` e execute as celulas na ordem.

## Dependencias

- numpy
- pandas
- matplotlib
- openpyxl

## Observacoes

- O diretorio `data/*` esta no `.gitignore`. Se quiser versionar os dados, ajuste o arquivo `.gitignore`.
- O notebook pode depender de arquivos da pasta `data/` com nomes especificos.
- O nome do arquivo `.txt` lido (sem extensao) sera utilizado como nome do material no título dos gráficos gerados.
