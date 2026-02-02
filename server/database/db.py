from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CURRENT_DIR = Path(__file__).resolve().parent

FILE_CSV_FOLDER = os.path.join(BASE_DIR, "data", "csv")
FILE_ZIP_FOLDER = os.path.join(BASE_DIR, "data", "zip")
SCHEMA_PATH = os.path.join(CURRENT_DIR, "schema.sql")

dsn = "postgresql://root:root@localhost:5432/intuitiveCareDB"
try:
    engine = create_engine(dsn)

    inspector = inspect(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()
except Exception as e:
    print(f"Erro ao contectar ao banco de dados: \n{e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def iniciar_infraestrutura():
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
        connection.execute(text("CREATE SCHEMA public;"))
        connection.execute(text("GRANT ALL ON SCHEMA public TO public;"))

        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r") as s:
                sql_schema = s.read()
                connection.execute(text(sql_schema))            
            print("Tabelas criadas com sucesso")
        else:
            print(f"Arquivo {SCHEMA_PATH} nao encontrado")


def migrar_sql(file_name, table_name):
    """Funcao responsavel por migrar o csv para o banco de dados"""
    if file_name.endswith('.zip'):
        file_path = os.path.join(FILE_ZIP_FOLDER, file_name)
    else:
        file_path = os.path.join(FILE_CSV_FOLDER, file_name)
    
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo {file_path} nao encontrado.")
        return

    print(f"Lendo arquivo: {file_path}")
    df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig", dtype=str)
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_', regex=False)
    
    df = df.rename(columns={
        'registro_operadora': 'registro_ans',
        'razaosocial': 'razao_social',
        'modalidadee': 'modalidade',
        'total_geral': 'total_geral',
    })
    
    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    if 'cnpj' in df.columns:
        df['cnpj'] = df['cnpj'].str.replace(r'\D', '', regex=True).str.zfill(14)
    
    if 'registro_ans' in df.columns:
         df['registro_ans'] = df['registro_ans'].str.replace(r'\D', '', regex=True).str.zfill(6)

    numeric_floats = ['valor_despesa', 'total_geral', 'media_trimestral', 'desvio_padrao_despesas']
    for col in numeric_floats:
        if col in df.columns:
            df[col] = df[col].str.replace(',', '.').astype(float)
            
    numeric_ints = ['ano', 'trimestre']
    for col in numeric_ints:
        if col in df.columns:
             df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    df = df.drop_duplicates()
    
    df.to_sql(table_name, con=engine, if_exists="append", index=False, chunksize=500)
    print(f"{table_name}: {len(df)} registros migrados")

if __name__ == "__main__":
    iniciar_infraestrutura()
    migrar_sql("consolidado_despesas.zip", "despesas_consolidadas")
    
    file_ops = "operadoras_ativas.csv"
    if os.path.exists(os.path.join(FILE_CSV_FOLDER, file_ops)):
        migrar_sql(file_ops, "operadoras")
    else:
        print(f"Alerta: arquivo {file_ops} nao encontrado. Rodar ETL primeiro.")
        
    migrar_sql("despesas_agregadas.csv", "dados_agregados")