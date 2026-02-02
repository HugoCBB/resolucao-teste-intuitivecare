import pandas as pd
from .db import engine

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
    
    maior_crescimento_operadoras()
    distribuicao_despesas_uf()
    despesas_acima_media_geral()