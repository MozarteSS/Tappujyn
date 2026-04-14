"""
Funções de leitura, processamento e visualização de dados de análise térmica.

Compatível com arquivos exportados pelo software DTG-60AH (Shimadzu).
"""

from __future__ import annotations

import os
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Leitura e processamento
# ---------------------------------------------------------------------------

def read_txt(
    data_dir: str = "data",
    smoth_DTG: int = 75,
    smoth_TGA: int = 75,
) -> dict[str, dict]:
    """
    Lê todos os arquivos .txt da pasta ``data_dir`` e retorna um dicionário
    com o nome da amostra como chave e os dados processados como valor.

    Formato esperado: arquivos exportados pelo software DTG-60AH com seção
    ``[Data]`` contendo colunas ``Time(sec)``, ``Temp(C)``, ``DTA(uV)`` e
    ``TGA(mg)``.

    Parameters
    ----------
    data_dir : str
        Caminho para a pasta com os arquivos ``.txt``. Padrão: ``'data'``.
    smoth_DTG : int
        Tamanho da janela de suavização (rolling mean) para a curva DTG.
        Padrão: ``75``.
    smoth_TGA : int
        Tamanho da janela de suavização (rolling mean) para a curva TGA.
        Padrão: ``75``.

    Returns
    -------
    dict[str, dict]
        Chave: nome da amostra (``Sample Name`` do cabeçalho).

        Valor: dicionário com:

        - ``'df'`` — :class:`~pandas.DataFrame` com as colunas:
          ``Tempo (s)``, ``Temperatura (°C)``, ``Massa_smoth (%)``,
          ``DTG_smoth (%.°C⁻¹)``, ``DTA_smoth (uV)``.
        - ``'sample_weight'`` — :class:`float` com o peso da amostra em mg.
    """
    amostras: dict[str, dict] = {}

    txt_files = [f for f in os.listdir(data_dir) if f.endswith(".txt")]

    for filename in txt_files:
        filepath = os.path.join(data_dir, filename)

        sample_name: str | None = None
        sample_weight: float | None = None
        data_start: int | None = None

        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()

        for i, line in enumerate(lines):
            if line.startswith("Sample Name:"):
                sample_name = line.split(":", 1)[1].strip()
            if line.startswith("Sample Weight:"):
                raw = line.split(":", 1)[1].strip()
                # valor pode vir como "9.282[mg]" ou somente "9.282"
                sample_weight = float(raw.split("[")[0].strip())
            if line.strip() == "[Data]":
                # linha i+1: nomes das grandezas  (Time, Temp, TGA, DTA …)
                # linha i+2: unidades              (sec,  C,    mg,  uV …)
                units_line = lines[i + 2].strip().split("\t")
                col_names = [u.strip() for u in units_line]
                data_start = i + 3
                break

        if data_start is None:
            print(f"Aviso: seção [Data] não encontrada em '{filename}'.")
            continue

        if sample_name is None:
            sample_name = os.path.splitext(filename)[0]

        df = pd.read_csv(
            StringIO("".join(lines[data_start:])),
            sep="\t",
            header=None,
            names=col_names,
            dtype=float,
        )

        df = df[["sec", "C", "mg", "uV"]]
        df = df.rename(  # type: ignore[call-overload]
            columns={
                "sec": "Tempo (s)",
                "C": "Temperatura (°C)",
                "mg": "Massa (mg)",
                "uV": "DTA (uV)",
            }
        )

        # Ajuste de zero e massa percentual
        df["Massa_adj (mg)"] = df["Massa (mg)"] - df["Massa (mg)"].min()
        massa_i = df["Massa (mg)"].iloc[0]
        df["Massa (%)"] = (df["Massa (mg)"] / massa_i) * 100

        # Derivada (DTG bruto)
        df["DTG (%.°C\u207B\u00B9)"] = (
            df["Massa_adj (mg)"].diff() / df["Tempo (s)"].diff()
        )

        # Suavização
        df["DTG_smoth (%.°C\u207B\u00B9)"] = (
            df["DTG (%.°C\u207B\u00B9)"]
            .rolling(window=int(smoth_DTG), center=True, min_periods=1)
            .mean()
        )
        df["Massa_smoth (%)"] = (
            df["Massa (%)"]
            .rolling(window=int(smoth_TGA), center=True, min_periods=1)
            .mean()
        )
        df["DTA_smoth (uV)"] = (
            df["DTA (uV)"]
            .rolling(window=int(smoth_DTG), center=True, min_periods=1)
            .mean()
        )

        cols_out = [
            "Tempo (s)",
            "Temperatura (°C)",
            "Massa_smoth (%)",
            "DTG_smoth (%.°C\u207B\u00B9)",
            "DTA_smoth (uV)",
        ]
        df_out = df[cols_out].copy()

        xlsx_path = os.path.join(data_dir, f"{sample_name}.xlsx")
        df_out.to_excel(xlsx_path, index=False)

        amostras[sample_name] = {
            "df": df_out,
            "sample_weight": sample_weight,
        }

    return amostras


# ---------------------------------------------------------------------------
# Visualização
# ---------------------------------------------------------------------------

def grafico_dtg(
    df: pd.DataFrame,
    temp_i: float,
    temp_f: float,
    eixo_x: str = "Temperatura (°C)",
    eixo_y1: str = "Massa_smoth (%)",
    eixo_y2: str = "DTG_smoth (%.°C\u207B\u00B9)",
    material: str = "material",
) -> Figure:
    """
    Gera um gráfico de duplo eixo Y para análise térmica.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com os dados processados.
    temp_i : float
        Temperatura inicial do eixo X (°C).
    temp_f : float
        Temperatura final do eixo X (°C).
    eixo_x : str
        Nome da coluna utilizada no eixo X.
    eixo_y1 : str
        Nome da coluna plotada no eixo Y primário (azul).
    eixo_y2 : str
        Nome da coluna plotada no eixo Y secundário (vermelho).
    material : str
        Nome do material exibido no título do gráfico.

    Returns
    -------
    matplotlib.figure.Figure
        Objeto Figure do matplotlib.
    """
    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)

    cor_y1 = "tab:blue"
    ax1.set_xlabel(eixo_x, fontsize=14)
    ax1.set_ylabel(eixo_y1, color=cor_y1, fontsize=14)
    ax1.plot(df[eixo_x], df[eixo_y1], color=cor_y1, label=eixo_y1)
    ax1.tick_params(axis="y", labelcolor=cor_y1)
    ax1.grid(True, color="gray", linestyle="--", linewidth=0.5, alpha=0.7)

    ax2 = ax1.twinx()
    ax2.set_xlim(temp_i - 10, temp_f + 10)
    ax2.set_xticks(np.arange(temp_i - 10, temp_f + 10, 50))

    cor_y2 = "tab:red"
    ax2.set_ylabel(eixo_y2, color=cor_y2, fontsize=14)
    ax2.plot(df[eixo_x], df[eixo_y2], color=cor_y2, label=eixo_y2)
    ax2.tick_params(axis="y", labelcolor=cor_y2)

    plt.title(f"MATERIAL: {material}", pad=20, fontsize=16)
    fig.tight_layout()
    plt.show()

    return fig


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def process_final(
    df: pd.DataFrame,
    temp_inicial: float | None = None,
    temp_final: float | None = None,
    material_name: str = "material",
) -> pd.DataFrame:
    """
    Filtra o DataFrame por faixa de temperatura e gera os três gráficos
    padrão de análise térmica: DTG×DTA, TGA×DTG e TGA×DTA.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame retornado por :func:`read_txt`.
    temp_inicial : float, optional
        Temperatura mínima de corte (°C). Se ``None``, usa o mínimo dos dados.
    temp_final : float, optional
        Temperatura máxima de corte (°C). Se ``None``, usa o máximo dos dados.
    material_name : str
        Nome do material exibido no título dos gráficos.

    Returns
    -------
    pd.DataFrame
        DataFrame filtrado pela faixa de temperatura informada.
    """
    col_temp  = str(df.columns[1])
    col_massa = str(df.columns[2])
    col_dtg   = str(df.columns[3])
    col_dta   = str(df.columns[4])

    df_ = df.copy()

    if temp_inicial is not None:
        df_ = df_.loc[df_[col_temp] >= temp_inicial]
    if temp_final is not None:
        df_ = df_.loc[df_[col_temp] <= temp_final]
    df_ = df_.reset_index(drop=True)

    t_i = df_[col_temp].min() if temp_inicial is None else temp_inicial
    t_f = df_[col_temp].max() if temp_final is None else temp_final

    grafico_dtg(
        df_, temp_i=t_i, temp_f=t_f,
        eixo_x=col_temp, eixo_y1=col_dtg, eixo_y2=col_dta,
        material=material_name,
    )
    grafico_dtg(
        df_, temp_i=t_i, temp_f=t_f,
        eixo_x=col_temp, eixo_y1=col_massa, eixo_y2=col_dtg,
        material=material_name,
    )
    grafico_dtg(
        df_, temp_i=t_i, temp_f=t_f,
        eixo_x=col_temp, eixo_y1=col_massa, eixo_y2=col_dta,
        material=material_name,
    )

    return df_
