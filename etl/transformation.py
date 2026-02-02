from typing import List
import pandas as pd
from pathlib import Path
import os
from validate_docbr import CNPJ
from extraction import compactar_arquivo_zip



BASE_DIR = Path(__file__).resolve().parent.parent

FILE_CSV_FOLDER = os.path.join(BASE_DIR, "data", "csv")
FILE_ZIP_ARCHIVE = os.path.join(BASE_DIR, "data", "zip", "consolidado_despesas.zip")
FILE_OPERADORAS = os.path.join(FILE_CSV_FOLDER, "Relatorio_cadop.csv")
FILE_METRICAS = os.path.join(FILE_CSV_FOLDER, "despesas_agregadas.csv")

FILE_OPERADORAS_ATIVAS = os.path.join(FILE_CSV_FOLDER, "operadoras_ativas.csv")
FILE_INACTIVE_OPERADORAS = os.path.join(FILE_CSV_FOLDER, "operadoras_inativas.csv")


def carregar_cadastro_operadoras() -> pd.DataFrame:
    """Funcao responsavel por ler o cadastro de operadoras e prepara o indice para busca."""
    try:
        
        df_cadop = pd.read_csv(FILE_OPERADORAS, sep=";", dtype=str, encoding='utf-8-sig')
        
        df_cadop.columns = df_cadop.columns.str.strip()
        
        reg_col = "REGISTRO_OPERADORA"
        if reg_col not in df_cadop.columns:
            
            possible_cols = [c for c in df_cadop.columns if "REGISTRO" in c.upper() and "ANS" in c.upper()]
            if possible_cols:
                reg_col = possible_cols[0]
            else:
                reg_col = 'Registro_ANS'

        if reg_col in df_cadop.columns:
             df_cadop[reg_col] = df_cadop[reg_col].str.strip().str.replace(r'\D', '', regex=True).str.zfill(6)
             df_cadop = df_cadop.drop_duplicates(subset=[reg_col])
             df_cadop.set_index(reg_col, inplace=True)
             return df_cadop
        else:
             print(f"Coluna de Registro ANS não encontrada em {FILE_OPERADORAS}")
             return pd.DataFrame()

    except Exception as e:
        print(f"Erro ao carregar Relatorio_cadop.csv: {e}")
        return pd.DataFrame()


def processar_linha_despesa(line: list, df_cadop: pd.DataFrame, validator: CNPJ) -> List:
    """Funcao responsavel por validade inconsistencias, CNPJ e duplicidade de uma linha."""
    valor_despesas = float(str(line[5]).replace(',', '.'))
        
    reg_ans = str(line[1]).strip().zfill(6)

    if valor_despesas < 0:
        return None

    try:
        if reg_ans in df_cadop.index:
            dados_op = df_cadop.loc[reg_ans]
            cnpj_val = str(dados_op['CNPJ']).strip().zfill(14)
        else:
            return None
    except Exception:
        return None

    if not validator.validate(cnpj_val):
        return None

    data_str = str(line[0])
    try:
        parte_ano = data_str.split("-")[0]
        parte_mes = data_str.split("-")[1]
        ano = int(parte_ano)
        mes = int(parte_mes)
    except:
        return None

    trimestre = (mes - 1) // 3 + 1

    return [
        cnpj_val,
        dados_op.get('Razao_Social', dados_op.get('Razao_Social', '')),
        trimestre,
        ano,
        valor_despesas,
        reg_ans,
        dados_op.get('Modalidade', ''),
        dados_op.get('UF', '')
    ]



def analisando_inconsistencia(year: int) -> List:
    """Percorre os arquivos, extrai dados brutos e chama a validação."""
    validator = CNPJ()
    df_cadop = carregar_cadastro_operadoras()
    
    if df_cadop.empty:
        print("Cadastro de operadoras vazio, abortando.")
        return []

    data_validate = []

    try:
        for file_name in os.listdir(FILE_CSV_FOLDER):
            if file_name.endswith(f"{year}.csv") and file_name != "consolidado_despesas.csv":
                url_complete = os.path.join(FILE_CSV_FOLDER, file_name)
                print(f"Processando {file_name}...")

                df = pd.read_csv(url_complete, sep=";", decimal=",", dtype={'REG_ANS': str})
                
                df_filter = df[df["DESCRICAO"].str.contains("Despesas com Eventos / Sinistros", case=False, na=False)]
                
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
    """Funcao responsavel por consolidadar despesas"""
    data_validate = analisando_inconsistencia(year)
    
    if not data_validate:
        print("Nenhum dado encontrado para consolidar.")
        return "Sem dados"

    columns_final = [
        "CNPJ", "RAZAOSOCIAL", "TRIMESTRE", "ANO", 
        "VALOR DESPESA", "REGISTRO ANS", "MODALIDADEE", "UF"
    ]

    df_final = pd.DataFrame(data_validate, columns=columns_final)         
    columns_agrupamento = [
        "CNPJ", "RAZAOSOCIAL", "TRIMESTRE", "ANO", 
        "REGISTRO ANS", "MODALIDADEE", "UF"
    ]

    df_final["VALOR DESPESA"] = pd.to_numeric(df_final["VALOR DESPESA"], errors='coerce').fillna(0)
    df_totalizado = df_final.groupby(columns_agrupamento, as_index=False)["VALOR DESPESA"].sum()
    
    file_output = os.path.join(FILE_CSV_FOLDER, "consolidado_despesas.csv")
    df_totalizado.to_csv(file_output, sep=";", index=False, encoding='utf-8-sig')
    
    active_regs = df_totalizado["REGISTRO ANS"].unique()

    df_cadop = carregar_cadastro_operadoras()

    if not df_cadop.empty:
        mask_active = df_cadop.index.isin(active_regs)
        
        df_cadop_active = df_cadop[mask_active]
        df_cadop_inactive = df_cadop[~mask_active]
        
        df_cadop_active.reset_index(inplace=True)
        df_cadop_active.to_csv(FILE_OPERADORAS_ATIVAS, sep=";", index=False, encoding='utf-8-sig')
        
        df_cadop_inactive.reset_index(inplace=True)
        df_cadop_inactive.to_csv(FILE_INACTIVE_OPERADORAS, sep=";", index=False, encoding='utf-8-sig')

    processar_metricas(df_totalizado)
    
    compactar_arquivo_zip(file_output, FILE_ZIP_ARCHIVE)
    
    if os.path.exists(file_output):
        os.remove(file_output)
        print(f"Arquivo temporario removido: {file_output}")
    
    print(f"Consolidação concluída. {len(df_totalizado)} registros gerados.")
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