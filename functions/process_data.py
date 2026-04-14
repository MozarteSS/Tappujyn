# funcao de leitura dos arquivos .txt e organizacao dos dados em um dataframe

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def read_txt(data_dir='data'):
    """
    Lê todos os arquivos .txt da pasta data e retorna um dicionário
    com o nome da amostra como chave e um DataFrame com os dados como valor.

    Formato esperado: arquivos exportados pelo software DTG-60AH com
    seção [Data] contendo colunas Time(sec), Temp(C), DTA(uV), TGA(mg).

    Parameters
    ----------
    data_dir : str
        Caminho para a pasta com os arquivos .txt. Padrão: 'data'.

    Returns
    -------
    dict[str, dict]
        Chave: nome da amostra (Sample Name do cabeçalho).
        Valor: dicionário com:
            'df'            : DataFrame com colunas ['sec', 'C', 'uV', 'mg']
            'sample_weight' : float com o peso da amostra em mg
    """
    from io import StringIO

    amostras = {}

    txt_files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]

    for filename in txt_files:
        filepath = os.path.join(data_dir, filename)

        sample_name = None
        sample_weight = None
        data_start = None

        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith('Sample Name:'):
                sample_name = line.split(':', 1)[1].strip()
            if line.startswith('Sample Weight:'):
                raw = line.split(':', 1)[1].strip()
                # valor pode vir como "9.282[mg]" ou somente "9.282"
                sample_weight = float(raw.split('[')[0].strip())
            if line.strip() == '[Data]':
                # linha i+1: nomes (Time, Temp, TGA, DTA...)
                # linha i+2: unidades (sec, C, mg, uV...) — usadas como nomes das colunas
                units_line = lines[i + 2].strip().split('\t')
                col_names = [u.strip() for u in units_line]
                data_start = i + 3  # primeira linha de dados
                break

        if data_start is None:
            print(f'Aviso: seção [Data] não encontrada em {filename}')
            continue

        if sample_name is None:
            sample_name = os.path.splitext(filename)[0]

        data_lines = lines[data_start:]
        df = pd.read_csv(
            StringIO(''.join(data_lines)),
            sep='\t',
            header=None,
            names=col_names,
            dtype=float,
        )

        df = df[['sec', 'C', 'mg', 'uV']]

        #xlsx_path = os.path.join(data_dir, f'{sample_name}.xlsx')
        #df.to_excel(xlsx_path, index=False)

        amostras[sample_name] = {
            'df': df,
            'sample_weight': sample_weight,
        }

    return amostras



# definiçao da funcao de primaria
def calc_dtg(df, smoth_DTG=75, smoth_TGA=75):

  # ajuste de massa zero
  df['mg'] = df['mg'] - df['mg'].min()

  # Obter massa porcentual
  massa_i = df['mg'].iloc[0]
  df['massa (%)'] = (df['mg'] / massa_i) * 100

  # Agora que as colunas são numéricas, calcule a derivada
  df['DTG'] = df['mg'].diff() / df['sec'].diff()

  # suavizaçao
  df['DTG_smoth'] = df['DTG'].rolling(window=int(smoth_DTG), center=True, min_periods=1).mean()
  df['massa (%)_smoth'] = df['massa (%)'].rolling(window=int(smoth_TGA), center=True, min_periods=1).mean()

  df_ = df.rename(columns={'sec': 'Tempo (s)',
                            'C': 'Temperatura (°C)',
                            'mg': 'Massa (mg)',
                            'massa (%)': 'Massa (%)',
                            'DTG': 'DTG_bruto (%/°C)',
                            'uV': 'DTA (uV)',
                            'DTG_smoth': 'DTG (%.°C\u207B\u00B9)'})

  # Verifique o resultado
  #print(df_1.head())
  #print(df_1.info())
  return df_



# definiçao da funcao de grafico
def grafico_dtg(df, temp_i, temp_f,eixo_x='Temperatura (°C)', eixo_y1 ='Massa (mg)', eixo_y2 = 'DTG (%.°C\u207B\u00B9)', material = 'nome_do_material'):
  # Garante que as colunas são numéricas (caso ainda não sejam)
  df[eixo_y1] = pd.to_numeric(df[eixo_y1], errors='coerce')
  df[eixo_y2] = pd.to_numeric(df[eixo_y2], errors='coerce')
  df[eixo_x] = pd.to_numeric(df[eixo_x], errors='coerce')

  # Cria a figura e o primeiro eixo (ax1)
  fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)

  # Cor para o primeiro eixo e gráfico (massa)
  cor_eixo_y1 = 'tab:blue'
  ax1.set_xlabel(eixo_x, fontsize=14)
  ax1.set_ylabel(eixo_y1, color=cor_eixo_y1, fontsize=14)
  ax1.plot(df[eixo_x], df[eixo_y1], color=cor_eixo_y1, label=eixo_y1)
  ax1.tick_params(axis='y', labelcolor=cor_eixo_y1)
  #ax1.grid(True, linestyle='--', alpha=0.6)
  ax1.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

  # Cria um segundo eixo (ax2) que compartilha o mesmo eixo X
  ax2 = ax1.twinx()
  ax2.set_xlim(temp_i-10, temp_f+10)
  ax2.set_xticks(np.arange(temp_i-10, temp_f+10, 50))

  # Cor para o segundo eixo e gráfico (derivada)
  cor_eixo_y2 = 'tab:red'
  ax2.set_ylabel(eixo_y2, color=cor_eixo_y2, fontsize=14)
  ax2.plot(df[eixo_x], df[eixo_y2], color=cor_eixo_y2, label=eixo_y2)
  ax2.tick_params(axis='y', labelcolor=cor_eixo_y2)

  # Adiciona um título geral e exibe o gráfico
  plt.title(f'MATERIAL: {material}', pad=20, fontsize=16)
  fig.tight_layout() # Ajusta o layout para evitar sobreposição
  plt.show()



# definiçao da funcao secundaria
def process_final(df, temp_inicial=None, temp_final=None, material_name='material'):

      df_ = df.copy()

      # filtro por faixa de temperatura
      if temp_inicial is not None:
          df_ = df_[df_['Temperatura (°C)'] >= temp_inicial]
      if temp_final is not None:
          df_ = df_[df_['Temperatura (°C)'] <= temp_final]
      df_ = df_.reset_index(drop=True)

      # limites para os graficos
      t_i = df_['Temperatura (°C)'].min() if temp_inicial is None else temp_inicial
      t_f = df_['Temperatura (°C)'].max() if temp_final is None else temp_final

      dtg_dta = grafico_dtg(df_, temp_i=t_i, temp_f=t_f, eixo_x='Temperatura (°C)', eixo_y1='DTG (%.°C\u207B\u00B9)', eixo_y2='DTA (uV)', material=material_name)
      tga_dtg = grafico_dtg(df_, temp_i=t_i, temp_f=t_f, eixo_x='Temperatura (°C)', eixo_y1='Massa (%)', eixo_y2='DTG (%.°C\u207B\u00B9)', material=material_name)
      tga_dta = grafico_dtg(df_, temp_i=t_i, temp_f=t_f, eixo_x='Temperatura (°C)', eixo_y1='Massa (%)', eixo_y2='DTA (uV)', material=material_name)

      return df_
