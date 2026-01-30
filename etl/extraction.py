import asyncio
from playwright.async_api import async_playwright
from time import sleep
from typing import List
from pathlib import Path
import os

import zipfile



URL_BASE = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis"

BASE_DIR = Path(__file__).resolve().parent.parent


FILE_ZIP_FOLDER = os.path.join(BASE_DIR, "download_ans","zip")
FILE_ZIP_EXTRACTION_FOLDER = os.path.join(BASE_DIR, "download_ans","csv")


os.makedirs(FILE_ZIP_FOLDER, exist_ok=True)
os.makedirs(FILE_ZIP_EXTRACTION_FOLDER, exist_ok=True)




def extrair_anos_limpos(data: List ) -> List:
    """Responsavel por filtrar os nomes de cada pasta"""
    anos = []
    for item in data:
        clean_item = item.strip().replace('/','')
        if clean_item.isdigit():
            anos.append(clean_item)

    return max(anos) if anos else print("Nenhum ano encontrado")



def extrair_trimestre_limpos(data: List) -> List:
    """Responsavel por filtrar os 3 ultimos trimestres dos arquivos .zip"""
    file_clean = [
        item.strip() for item in data if item.strip().lower().endswith('.zip')
    ]
    return file_clean



async def baixar_arquivos(page, src: str, file_name: str):
    try:
        url = f"{src}/{file_name}"
        print(f"Baixando arquivo: {file_name}")
        
        async with page.expect_download() as p:
            await page.click(f"text={file_name}")
        
        download = await p.value
        await download.save_as(os.path.join(FILE_ZIP_FOLDER, file_name))
        print(f"{file_name} salvo com sucesso")

        extrair_arquivos_zip(file_name)
    except Exception as e:
        print(f"Erro ao baixar arquivos e extrair arquivos\n{e}")


def extrair_arquivos_zip(file_name: str):
    """Responsavel por extrair os arquivos zip automaticamente"""
    file_src = os.path.join(FILE_ZIP_FOLDER, file_name)
    
    with zipfile.ZipFile(file_src, "r") as zip_ref:
        zip_ref.extractall(FILE_ZIP_EXTRACTION_FOLDER)
        print(f"{file_name} extraido em {FILE_ZIP_EXTRACTION_FOLDER}")

async def buscar_dados_ans():
    async with async_playwright() as p:
        try:
                
            browser = await p.firefox.launch(headless=True)

            page = await browser.new_page()
            await page.goto(URL_BASE)
            
            links = await page.locator("td a").all_inner_texts()
            
            max_years = extrair_anos_limpos(links)
            src = f"{URL_BASE}/{max_years}"
            await page.goto(src)

            files_links = await page.locator("td a").all_inner_texts()  
            file_clean = extrair_trimestre_limpos(files_links)

            for file_name in file_clean: 
                await baixar_arquivos(page, src, file_name)

            await browser.close()
        
        except Exception as e:
            print("Erro ao tentar buscar dados ans\n{e}")

if __name__ == "__main__":
    asyncio.run(buscar_dados_ans())