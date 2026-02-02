from sqlalchemy import create_engine, text, inspect
import pandas as pd
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

FILE_CSV_FOLDER = os.path.join(BASE_DIR, "data", "csv")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

dsn = "postgresql://root:root@localhost:5432/intuitiveCareDB"
engine = create_engine(dsn)
inspector = inspect(engine)

def iniciar_infraestrutura():
    with engine.connect() as connection:
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


def migrar_sql(file_name, table_name, colum_zero=None, colum_value=None):
    """Funcao responsavel por migrar dados de tabela csv para banco de dados"""
    file_path = os.path.join(FILE_CSV_FOLDER, file_name)

    if table_name in inspector.get_table_names():
        print(f"A tabela {table_name} ja existe")
        return
    
    df = pd.read_csv(file_path, sep=";", dtype=str, encoding='latin1')
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')

    df = df.rename(columns={'registro_operadora': 'registro_ans'})

    if colum_zero:
        for col, tamanho in colum_zero.items():
            col_norm = col.lower().replace(' ', '_')    
            if col_norm in df.columns:
                df[col] = df[col].str.zfill(tamanho)

    if colum_value:
        cols_limpar = [colum_value] if isinstance(colum_value, str) else colum_value

        for col_orig in cols_limpar:
            col_norm = col_orig.lower().replace(' ', '_')    
            
            if col_norm in df.columns:
                df[col_norm] = df[col_norm].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)

    df.to_sql(table_name, con=engine, index=False)
    print(f"Tabela {table_name}, exportado com sucesso")

def maior_crescimento_operadoras():
    """Funcao responsavel por verificar as 5 operadoras com os maior crescimento levando em conta o tamanho da operadora"""
    df = pd.read_sql("despesas_consolidadas", con=engine)
    df_ops = pd.read_sql("operadoras", con=engine)
        
    df[['ano', 'trimestre', 'valor_despesa']] = df[['ano', 'trimestre', 'valor_despesa']].apply(pd.to_numeric)
        
    df.sort_values(['registro_ans', "ano", "trimestre"])

    primeiro = df.groupby('registro_ans')['valor_despesa'].first()
    ultimo = df.groupby('registro_ans')['valor_despesa'].last()

    # Calculo para variacao percentual
    crescimento = ((ultimo - primeiro) / primeiro) * 100
    top_5 = crescimento.sort_values(ascending=False).head(5)

    df_crescimento = crescimento.reset_index()
    df_crescimento.columns = ['registro_ans', 'crescimento_percentual']

    resultado_final = pd.merge(
        df_crescimento, 
        df_ops[['registro_ans', 'razao_social']], 
        on='registro_ans', 
        how='left'
    )
        
    top_5 = resultado_final.replace([float('inf'), float('-inf')], 0).dropna()
    top_5 = top_5.sort_values(by='crescimento_percentual', ascending=False).head(5)

    print("\n--- Query 1: Top 5 Operadoras com Maior Crescimento ---")
    print(top_5[['razao_social', 'registro_ans', 'crescimento_percentual']])
    

        
def distribuicao_despesas_uf():
    """Funcao responsavel por fazer um top 5 regioes ( UF ) com as maiores despesas totais"""
    df = pd.read_sql("despesas_consolidadas", con=engine)
    

    analise_uf = df.groupby('uf')['valor_despesa'].agg(['sum', 'mean']).reset_index()
    analise_uf.columns = ['UF', 'Total_Despesas', 'Media_por_Operadora']

    top_5_uf = analise_uf.sort_values(by='Total_Despesas', ascending=False).head(5)

    print("\n--- Query 2: Distribuição por UF (Top 5) ---")
    print(top_5_uf)

def despesas_acima_media_geral():
    """Funcao responsavel por filtrar as operadoras a cima da media em pelo menos 2 trimestres"""
    df = pd.read_sql("despesas_consolidadas", con=engine)
    df_op = pd.read_sql("operadoras", con=engine)

    df['valor_despesa'] = pd.to_numeric(df['valor_despesa'], errors='coerce')
    media_geral = df['valor_despesa'].mean()

    df_pivot = df.pivot_table(index='registro_ans', columns='trimestre', values='valor_despesa')
    
    acima_media = (df_pivot > media_geral).sum(axis=1)
    resultado = acima_media[acima_media >= 2]
    
    df_resultado = resultado.reset_index()
    df_resultado.columns = ['registro_ans', 'quantidade_trimestres']

    resultado_final = pd.merge(
        df_resultado,
        df_op[['registro_ans', 'razao_social']],
        on='registro_ans',
        how='left'
    )
    
    print("\n--- Query 3: Operadoras acima da média em pelo menos 2 trimestres ---")
    print(f"Total de operadoras: {len(resultado)}")
    print(resultado_final[['razao_social', 'registro_ans', 'quantidade_trimestres']].head())

if __name__ == "__main__":
    iniciar_infraestrutura()

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

    maior_crescimento_operadoras()
    distribuicao_despesas_uf()
    despesas_acima_media_geral()
    