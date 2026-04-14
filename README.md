# AnaliseTermicaScript

Scripts Python para leitura, processamento e visualização de dados de **análise termogravimétrica (TGA/DTG/DTA)**, compatíveis com arquivos exportados pelo software **DTG-60AH (Shimadzu)**.

## Estrutura do projeto

```
AnaliseTermicaScript/
├── data/                     # Arquivos de entrada (.txt) e saída (.xlsx)
├── functions/
│   ├── __init__.py
│   └── process_data.py       # Funções de leitura, processamento e visualização
├── thermal_analysis.ipynb    # Notebook principal de análise
├── requirements.txt
└── README.md
```

## Funcionalidades

- Leitura automática de todos os arquivos `.txt` da pasta `data/`
- Extração de metadados do cabeçalho (nome da amostra, peso)
- Cálculo de massa percentual e derivada DTG
- Suavização das curvas TGA e DTG via média móvel configurável
- Geração de três gráficos de duplo eixo: **DTG×DTA**, **TGA×DTG** e **TGA×DTA**
- Exportação dos dados processados para `.xlsx`

## Requisitos

- Python 3.10+

## Instalação

Clone o repositório e crie um ambiente virtual:

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Como usar

1. Copie os arquivos `.txt` exportados pelo DTG-60AH para a pasta `data/`.

2. Abra e execute o notebook `thermal_analysis.ipynb`:

```bash
jupyter notebook thermal_analysis.ipynb
```

3. Ajuste os parâmetros conforme necessário:

| Parâmetro      | Descrição                                      | Padrão |
|----------------|------------------------------------------------|--------|
| `smoth_DTG`    | Janela de suavização da curva DTG (pontos)     | `75`   |
| `smoth_TGA`    | Janela de suavização da curva TGA (pontos)     | `75`   |
| `temp_inicial` | Temperatura mínima de análise (°C)             | `None` |
| `temp_final`   | Temperatura máxima de análise (°C)             | `None` |

## API das funções

### `read_txt(data_dir, smoth_DTG, smoth_TGA)`

Lê todos os `.txt` da pasta `data_dir` e retorna um dicionário `{nome_amostra: {"df": DataFrame, "sample_weight": float}}`.

O DataFrame retornado contém as colunas:

| Coluna | Descrição |
|---|---|
| `Tempo (s)` | Tempo em segundos |
| `Temperatura (°C)` | Temperatura em graus Celsius |
| `Massa_smoth (%)` | Massa percentual suavizada |
| `DTG_smoth (%.°C⁻¹)` | Derivada termogravimétrica suavizada |
| `DTA_smoth (uV)` | Sinal DTA suavizado |

### `grafico_dtg(df, temp_i, temp_f, eixo_x, eixo_y1, eixo_y2, material)`

Gera um gráfico de duplo eixo Y. Retorna o objeto `Figure` do matplotlib.

### `process_final(df, temp_inicial, temp_final, material_name)`

Filtra o DataFrame pela faixa de temperatura e gera os três gráficos padrão. Retorna o DataFrame filtrado.

## Dependências

| Pacote       | Uso                         |
|--------------|-----------------------------|
| `pandas`     | Manipulação de dados        |
| `numpy`      | Cálculos numéricos          |
| `matplotlib` | Geração de gráficos         |
| `openpyxl`   | Exportação para `.xlsx`     |

## Observações

- A pasta `data/` está no `.gitignore`. Para versionar os dados, ajuste o `.gitignore`.
- O campo `Sample Name` do cabeçalho do arquivo `.txt` é usado como nome da amostra. Se ausente, usa o nome do arquivo.
