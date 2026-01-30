from typing import List
import pandas as pd
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

FILE_ZIP_EXTRACTION_FOLDER = os.path.join(BASE_DIR, "download_ans","csv")
FILE_ZIP_OUTPUT = os.path.join(BASE_DIR, "download_ans", "csv", "consolidado_despesas.csv")

def analisando_inconsistencia() -> List:
    """
    Funcao responsavel por analisar inconsistencias e definir tabela com os novos dados.
    As inconsistencias foram tratadas em etapass. 

    1 - A primeira etapa eu filtrei apenas as despesas com eventos sinistros
    2 - Apos o filtro eu destrinchei a tabela, tirei o cabecalho e deixei apenas os dados 
        brutos, para serem adicionados em uma nova tabela 
    3 - Apos isso fiz um loop em todo dado bruto, e verifiquei que os valor final em alguns dados
        estava definido como 0.0 ou ate mesmo negativo, sabendo disso, estabeleci uma condicao onde
        todo dado com valor final menor ou igual a zero sera descartado e nao entrara na tabela consolidado_despesas.csv
    4 - Apos tratar as inconsistencias, defini uma nova funcao para consolidar os dados, e definir a tabela final, salvando dentro de /download_ans/csv
    """

    data_validate = []
    try: 
        for files in os.listdir(FILE_ZIP_EXTRACTION_FOLDER):
            if files.endswith(".csv"):
                url_complete = os.path.join(FILE_ZIP_EXTRACTION_FOLDER, files)

                df = pd.read_csv(url_complete, sep=";", decimal=",")
                df_filter = df[df["DESCRICAO"] == "Despesas com Eventos / Sinistros"]
                
                # EXTRAI O DADO BRUTO DA TABELA, SEM CABECALHO
                raw_data = df_filter.values.tolist()

                for line in raw_data:
                    final_balance = line[5] 
                    
                    if final_balance >= 0:
                        data = str(line[0])
                        ano = data.split("-")[0]
                        mes = int(data.split("-")[1])

                        quarter = (mes - 1) // 3 + 1
                        
                        new_line = [
                            "", 
                            "",
                            quarter,
                            ano,
                            final_balance,
                            line[1],
                            "",
                            ""                                                                            
                        ]
                        
                        data_validate.append(new_line)

        
        return data_validate if data_validate else None
    except Exception as e:
        print(f"Erro ao analisar inconsistencia\n{e}")

def consolidando_dados():
    """Funcao responsavel por consolidadar os dados """
    data = analisando_inconsistencia()

    columns_final = [
        "CNPJ", "RAZAOSOCIAL", "TRIMESTRE", "ANO", 
        "VALOR DESPESA", "REGISTRO ANS", "MODALIDADEE", "UF"
    ]

    df_final = pd.DataFrame(data, columns=columns_final)        
    df_final.to_csv(FILE_ZIP_OUTPUT, sep=";", index=False, encoding='utf-8')
    return "Tabela processsado com sucesso"

if __name__ == "__main__":
    consolidando_dados()