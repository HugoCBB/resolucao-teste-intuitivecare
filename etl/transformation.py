from typing import List, Set
import pandas as pd
from pathlib import Path
import os

from validate_docbr import CNPJ


BASE_DIR = Path(__file__).resolve().parent.parent


FILE_CSV_FOLDER = os.path.join(BASE_DIR, "data","csv")
FILE_ZIP_OUTPUT = os.path.join(BASE_DIR, "data", "csv", "consolidado_despesas.csv")
FILE_OPERADORAS = os.path.join(FILE_CSV_FOLDER, "Relatorio_cadop.csv")
FILE_METRICAS = os.path.join(FILE_CSV_FOLDER, "despesas_agregadas.csv")


def carregar_cadastro_operadoras() -> pd.DataFrame:
    """Funcao responsavel por ler o cadastro de operadoras e prepara o índice para busca."""

    try:
        df_cadop = pd.read_csv(FILE_OPERADORAS, sep=";", dtype=str, encoding='utf-8-sig')

        df_cadop.columns = df_cadop.columns.str.strip()

        if "REGISTRO_OPERADORA" not in df_cadop.columns:
            df_cadop = pd.read_csv(FILE_OPERADORAS, sep=";", dtype=str, encoding='latin-1')
            df_cadop.columns = df_cadop.columns.str.strip()

        df_cadop = df_cadop.drop_duplicates(subset=["REGISTRO_OPERADORA"])
        df_cadop.set_index("REGISTRO_OPERADORA", inplace=True)

        return df_cadop

    except Exception as e:
        print(f"Erro ao carregar Relatorio_cadop.csv: {e}")
        return pd.DataFrame()


def processar_linha_despesa(line: list, df_cadop: pd.DataFrame, validator: CNPJ) -> List:
    """Funcao responsavel por validade inconsistencias, CNPJ e duplicidade de uma linha."""

    valor_despesas = line[5]
    reg_ans = str(line[1])

    if valor_despesas <= 0:
        return None

    try:
        dados_op = df_cadop.loc[reg_ans]
        cnpj_val = str(dados_op['CNPJ'])
    except Exception:
        return None

    if not validator.validate(cnpj_val):
        return None

    data_str = str(line[0])
    ano = data_str.split("-")[0]
    mes = int(data_str.split("-")[1])
    trimestre = (mes - 1) // 3 + 1

    return [
        cnpj_val,
        dados_op['Razao_Social'],
        trimestre,
        ano,
        valor_despesas,
        reg_ans,
        dados_op['Modalidade'],
        dados_op['UF']

    ]



def analisando_inconsistencia(year: int) -> List:
    """Percorre os arquivos, extrai dados brutos e chama a validação."""
    validator = CNPJ()
    df_cadop = carregar_cadastro_operadoras()
    data_validate = []

    try:

        for file_name in os.listdir(FILE_CSV_FOLDER):
            if file_name.endswith(f"{year}.csv") and file_name != "consolidado_despesas.csv":
                url_complete = os.path.join(FILE_CSV_FOLDER, file_name)

                df = pd.read_csv(url_complete, sep=";", decimal=",", dtype={'REG_ANS': str})
                df_filter = df[df["DESCRICAO"] == "Despesas com Eventos / Sinistros"]
                raw_data = df_filter.values.tolist()

                for line in raw_data:
                    resultado = processar_linha_despesa(line, df_cadop, validator)
                    if resultado:
                        data_validate.append(resultado)


        return data_validate

    except Exception as e:
        print(f"Erro no processamento de arquivos: {e}")
        return []


def consolidando_dados(year):
    """Funcao responsavel por consolidadar despesas e gerar tabela a consolidado_despesas.csv"""
    data = analisando_inconsistencia(year)

    columns_final = [
        "CNPJ", "RAZAOSOCIAL", "TRIMESTRE", "ANO", 
        "VALOR DESPESA", "REGISTRO ANS", "MODALIDADEE", "UF"
    ]

    df_final = pd.DataFrame(data, columns=columns_final)         
    columns_agrupamento = [
        "CNPJ", "RAZAOSOCIAL", "TRIMESTRE", "ANO", 
        "REGISTRO ANS", "MODALIDADEE", "UF"
    ]

    df_final["VALOR DESPESA"] = pd.to_numeric(df_final["VALOR DESPESA"], errors='coerce').fillna(0)
    df_totalizado = df_final.groupby(columns_agrupamento, as_index=False)["VALOR DESPESA"].sum()
    df_totalizado.to_csv(FILE_ZIP_OUTPUT, sep=";", index=False, encoding='utf-8-sig')
    
    processar_metricas(df_totalizado)
    
    return "Tabela processsado com sucesso"

def processar_metricas(df_totalizado):
    """Funcao responsavel por gerar as metricas e consolidar em despesas_agregadas.csv"""

    df_metricas = df_totalizado.groupby(["RAZAOSOCIAL", "UF"]).agg(
        Total_Geral=("VALOR DESPESA", "sum"),
        Media_Trimestral=("VALOR DESPESA", "mean"),
        Desvio_Padrao_Despesas=("VALOR DESPESA", "std")
    ).reset_index()

    df_metricas["Desvio_Padrao_Despesas"] = df_metricas["Desvio_Padrao_Despesas"].fillna(0)
    df_metricas.to_csv(FILE_METRICAS, sep=";", index=False, encoding='utf-8-sig')
    

if __name__ == "__main__":

    consolidando_dados(2025) 