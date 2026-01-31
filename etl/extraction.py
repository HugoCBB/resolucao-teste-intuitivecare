import asyncio
from playwright.async_api import async_playwright
from time import sleep
from typing import List
from pathlib import Path
import os

import zipfile


# CONFIGURACAO DE ROTAS
URL_BASE = "https://dadosabertos.ans.gov.br/FTP/PDA"
URL_DEMONSTRACOES = f"{URL_BASE}/demonstracoes_contabeis"
URL_OPERADORAS = f"{URL_BASE}/operadoras_de_plano_de_saude_ativas"


BASE_DIR = Path(__file__).resolve().parent.parent

FILE_ZIP_FOLDER = os.path.join(BASE_DIR, "download_ans","zip")
FILE_CSV_FOLDER = os.path.join(BASE_DIR, "download_ans","csv")


os.makedirs(FILE_ZIP_FOLDER, exist_ok=True)
os.makedirs(FILE_CSV_FOLDER, exist_ok=True)




def extrair_anos_limpos(data: List ) -> List:
    """Responsavel por filtrar os nomes de cada pasta"""
    anos = []
    for item in data:
        clean_item = item.strip().replace('/','')
        if clean_item.isdigit():
            anos.append(clean_item)

    return max(anos) if anos else print("Nenhum ano encontrado")



def extrair_arquivos(data: List) -> List:
    """Responsavel por filtra arquivos que terminam em .zip ou .csv"""
    file_clean = [
        item.strip() for item in data 
        if item.strip().lower().endswith('.zip') or item.strip().lower().endswith('.csv')
    ]
    return file_clean

async def baixar_arquivos(page, src: str, file_name: str):
    """Funcao responvavel por baixar os arquivos por tipo"""

    if file_name.lower().endswith('.csv'):
        final_download = os.path.join(FILE_CSV_FOLDER, file_name)
    else:
        final_download = os.path.join(FILE_ZIP_FOLDER, file_name)

    if os.path.exists(final_download):
        print(f"Arquivo {file_name} ja existe em {final_download}")
        return  
    
    try:
        url = f"{src}/{file_name}"
        print(f"Baixando arquivo: {file_name}")
        
        async with page.expect_download() as p:
            await page.locator(f"text={file_name}").click(force=True)

        download = await p.value

        await download.save_as(final_download)
        print(f"{file_name} salvo com sucesso")

    except Exception as e:
        print(f"Erro ao baixar arquivos\n{e}")


def descompactar_arquivos_zip(file_name: str):
    """Responsavel por extrair os arquivos zip automaticamente"""
    file_src = os.path.join(FILE_ZIP_FOLDER, file_name)
    
    if os.path.exists(file_src):
        print(f"Arquivo {file_name} ja foi descompactado em {file_src}")
        return
    
    with zipfile.ZipFile(file_src, "r") as zip_ref:
        zip_ref.extractall(FILE_CSV_FOLDER)
        print(f"{file_name} extraido em {FILE_CSV_FOLDER}")


async def processar_secao_ans(page, url_secao):
    """Funcao responsavel por processar a secao que esta ocorrendo"""
    try:
        print(f"\nVerificando arquivos em: {url_secao}")
        await page.goto(url_secao, wait_until="load")
        await page.wait_for_selector("td a")
        
        links = await page.locator("td a").all_inner_texts()
        files = extrair_arquivos(links)

        for file_name in files:
            await baixar_arquivos(page, url_secao, file_name)

            if file_name.lower().endswith('.zip'):
                descompactar_arquivos_zip(file_name)
        
    except Exception as e:
        print(f"Erro na secao {url_secao}: {e}")


async def buscar_dados_ans():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(URL_DEMONSTRACOES)
            links_years = await page.locator("td a").all_inner_texts()
            max_year = extrair_anos_limpos(links_years)
            
            if max_year:
                url_final = f"{URL_DEMONSTRACOES}/{max_year}"
                await processar_secao_ans(page, url_final)
            
            await page.goto(URL_OPERADORAS)
            sleep(5)
            await processar_secao_ans(page, URL_OPERADORAS)

        finally:
            await browser.close()
            
if __name__ == "__main__":
    asyncio.run(buscar_dados_ans())