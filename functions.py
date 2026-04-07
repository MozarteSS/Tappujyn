# libs
import os
import io
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt



# definiçao da funcao de primaria
def dtg(df, smoth_DTG=75, smoth_TGA=75):

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
  plt.title(f'MATERIAL: {material}')
  fig.tight_layout() # Ajusta o layout para evitar sobreposição
  plt.show()


# definiçao da funcao secundaria
def open_file(path_, smoth_DTG=75, smoth_TGA=75, temp_inicial=None, temp_final=None):
  try:
      material_name = os.path.splitext(os.path.basename(path_))[0]

      # abre o docuemnto txt como csv
      df = pd.read_csv(path_, sep="\t", skiprows=2)
      df_ = df.iloc[60:].copy()

      for col in df_.columns:
          try:
              df_[col] = df_[col].str.replace(',', '.')
              df_[col] = pd.to_numeric(df_[col])
          except AttributeError:
              continue

      # filtro por faixa de temperatura
      if temp_inicial is not None:
          df_ = df_[df_['C'] >= temp_inicial]
      if temp_final is not None:
          df_ = df_[df_['C'] <= temp_final]
      df_ = df_.reset_index(drop=True)

      #execuçao da funçao primaria
      DF = dtg(df_, smoth_DTG=smoth_DTG, smoth_TGA=smoth_TGA)

      # salva o dataframe em xlsx
      xlsx_path = path_.replace('.txt', '.xlsx')
      DF.to_excel(xlsx_path, index=False)

      dtg_dta = grafico_dtg(DF, temp_i=temp_inicial, temp_f=temp_final, eixo_x='Temperatura (°C)', eixo_y1='DTG (%.°C\u207B\u00B9)', eixo_y2='DTA (uV)', material = material_name)
      tga_dtg = grafico_dtg(DF, temp_i=temp_inicial, temp_f=temp_final, eixo_x='Temperatura (°C)', eixo_y1='Massa (mg)', eixo_y2='DTG (%.°C\u207B\u00B9)', material = material_name)
      tga_dta = grafico_dtg(DF, temp_i=temp_inicial, temp_f=temp_final, eixo_x='Temperatura (°C)', eixo_y1='Massa (mg)', eixo_y2='DTA (uV)', material = material_name)

      return DF
  except FileNotFoundError:
      print(f"O arquivo '{path_}' não foi encontrado.")
      return None
  except Exception as e:
      print(f"Ocorreu um erro ao abrir o arquivo: {e}")
      return None