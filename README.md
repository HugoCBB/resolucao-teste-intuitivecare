# Teste Intuitive Care - Hugo

Este repositório contém a solução para o Teste de Entrada para Estagiários da Intuitive Care.
O projeto consiste em um pipeline ETL, um banco de dados PostgreSQL, uma API com FastAPI e um frontend em Vue.js.

## 🚀 Como Executar

### Pré-requisitos e Instalação

1.  **Python 3.10+**:
    *   Baixe e instale em [python.org](https://www.python.org/downloads/).
    *   Garanta que a opção "Add Python to PATH" esteja marcada durante a instalação.
2.  **Node.js 16+**:
    *   Baixe e instale a versão LTS em [nodejs.org](https://nodejs.org/).
3.  **Bun** (Opcional, usado no frontend):
    *   Windows (PowerShell): `powershell -c "irm bun.sh/install.ps1 | iex"`
    *   Ou use `npm` se preferir (o projeto suporta ambos).
4.  **Docker Desktop** (Para o Banco de Dados):
    *   Baixe e instale em [docker.com](https://www.docker.com/products/docker-desktop/).
    *   Execute o Docker Desktop após instalar.
5.  **Browsers do Playwright**:
    *   Serão instalados automaticamente pelo comando `playwright install` descrito abaixo.

### 1. Configuração do Backend e ETL

```bash
# Crie e ative o ambiente virtual
python -m venv venv # Windows
.\venv\Scripts\activate  # Windows

python3 -m venv venv # Linux / Mac
source ./venv/bin/activate #Linux / Mac

# Instale as dependencias
pip install -r requirements.txt
playwright install firefox

# Com o docker instalado execute o docker-compose.yaml
docker compose up --build -d

# Executar o ETL (Extração e Transformação)
# Isso baixará os arquivos, processará e gerará os CSVs/ZIPs em data/
python etl/extraction.py
python etl/transformation.py

# Migrar dados para o Banco de Dados
python server/database/db.py

# Executar as querys analiticas dentro de server
python -m database.querys

# Iniciar o Servidor da API dentro de server
fastapi dev main.py
```
A documentacao da API estará disponível em: `http://localhost:8000/docs`

### 2. Configuração do Frontend

```bash
cd frontend
bun install
bun dev
```
O Frontend estará disponível em: `http://localhost:5173`

---

## 📂 Estrutura do Projeto

```text
teste-intuitiveCare/
├── etl/                        # TESTE 1 e 2: Extração e Transformação
│   ├── extraction.py           # 1.1, 1.2: Scraper da ANS e download/unzip de arquivos
│   └── transformation.py       # 1.3, 2.1, 2.2, 2.3: Consolidação, validação, limpeza e agregação
├── server/                     # TESTE 3 e 4: Backend e Banco de Dados
│   ├── database/               # TESTE 3: Scripts de migração e conexão DB (SQLAlchemy)
│   ├── modules/                # TESTE 4: Rotas da API (FastAPI)
│   └── main.py                 # Ponto de entrada da API
├── frontend/                   # TESTE 4: Interface Web (Vue.js + Vite)
│   └── src/                    # Código fonte do frontend
├── data/                       # Arquivos gerados (CSVs e ZIPs)
└── README.md                   # Documentação
```

---

## ⚖️ Trade-offs Técnicos

### 1. ETL: Pandas em Memória vs Incremental
**Escolha:** Processamento em memória com Pandas.
**Justificativa:** O volume de dados dos trimestres (alguns MBs) não justifica a complexidade de um processamento incremental ou streaming (como Spark ou chunks). O Pandas permite desenvolvimento rápido e manipulação vetorial eficiente para este volume. Se os arquivos fossem gigabytes, usaríamos `chunksize` ou Dask.

### 2. Banco de Dados: Normalização
**Escolha:** Tabelas normalizadas (`operadoras` e `despesas_consolidadas`).
**Justificativa:** Separar os dados cadastrais das despesas evita redundância (DRY) e economiza espaço, já que os dados da operadora se repetem para cada lançamento de despesa. Facilitou também a atualização independente dos cadastros.

### 3. API: FastAPI vs Flask
**Escolha:** FastAPI.
**Justificativa:** O FastAPI oferece validação de dados automática (Pydantic), documentação interativa (Swagger UI) nativa e performance assíncrona superior (ASGI). Para um projeto moderno que requer tipagem forte e rapidez, é superior ao Flask.

### 4. Paginação: Offset-based
**Escolha:** Offset-based (`page` e `limit`).
**Justificativa:** Para a interface de usuário solicitada (tabela com números de página), a paginação por offset é a mais intuitiva e fácil de implementar. Cursor-based seria melhor para performance em volumes massivos ou scroll infinito, mas impediria pular para uma página específica.

### 5. Frontend: Busca Local vs Servidor
**Escolha:** Busca no Servidor.
**Justificativa:** Inicialmente filtrávamos no cliente, mas isso limitava a busca apenas à página atual gerando uma ui muitas vezes bugada e mal compreendida. Movi para busca no servidor (parâmetro `?search=`) para garantir que o usuário encontre qualquer registro no banco de dados, independente da página em que esteja.  

### 6. Estratégia de Arquivos (Zip)
**Decisão:** Manter apenas o ZIP final e CSVs essenciais.
**Justificativa:** Para economizar espaço e manter a organização, o script remove o CSV intermediário de despesas após a compactação bem-sucedida, mantendo apenas `consolidado_despesas.zip` e os arquivos de operadoras necessários para carga.

### 7. Banco de Dados: Tipos de Dados (CNPJ)
**Escolha:** `VARCHAR` (String).
**Justificativa:** CNPJs e Registros ANS possuem zeros à esquerda significativos. Armazená-los como `BIGINT` ou `INTEGER` removeria esses zeros (ex: `0123...` viraria `123...`), exigindo formatação constante na aplicação e quebrando chaves de busca. `VARCHAR` preserva a integridade exata do identificador.

### 8. Validação de CNPJ: Lib (`validate-docbr`) vs Manual
**Escolha:** Biblioteca `validate-docbr`.
**Justificativa:** Embora o algoritmo de módulo 11 seja conhecido, implementar validação manual é propenso a erros (ex: edge cases de formatação, regex incorreto). Usar uma biblioteca testada pela comunidade garante robustez, manutenção simplificada e reduz código "boilerplate", permitindo focar na lógica de negócio (ETL).

---

## 🛠️ Tecnologias Utilizadas
- **Python**: Playwright (Scraping), Pandas (ETL), SQLAlchemy (ORM), FastAPI.
- **Frontend**: Vue.js 3, Vite, Bootstrap 5.
- **Banco de Dados**: PostgreSQL.

Desenvolvido por Hugo.
