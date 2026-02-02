from sqlalchemy import create_engine
import pandas as pd
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_CSV_FOLDER = os.path.join(BASE_DIR, "data", "csv")

dsn = "postgresql://root:root@localhost:5432/intuitiveCareDB"
engine = create_engine(dsn)

def migrar_sql(file_name, table_name, colum_zero=None, colum_value=None):
    """Funcao responsavel por migrar dados de tabela csv para banco de dados"""
    file_path = os.path.join(FILE_CSV_FOLDER, file_name)
    
    df = pd.read_csv(file_path, sep=";", dtype=str, encoding='latin1')

    if colum_zero:
        for col, tamanho in colum_zero.items():
            if col in df.columns:
                df[col] = df[col].str.zfill(tamanho)

    if colum_value:
        cols_para_limpar = [colum_value] if isinstance(colum_value, str) else colum_value
        for col in cols_para_limpar:
            if col in df.columns:
                df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)

    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f"Tabela {table_name}, exportado com sucesso")



if __name__ == "__main__":
    migrar_sql(
        "consolidado_despesas.csv",
        "despesas_consolidadas",
        colum_zero={'cnpj': 14, 'registro_ans': 6}, 
        colum_value='VALOR DESPESA'
    )

    migrar_sql(
        "Relatorio_cadop.csv", 
        "operadoras",
        colum_zero={'cnpj': 14, 'registro_ans': 6, 'cep': 8}
    )

    migrar_sql(
        "despesas_agregadas.csv", 
        "dados_agregados", 
        colum_value=['Total_Geral', 'Media_Trimestral', 'Desvio_Padrao_Despesas']
    )
