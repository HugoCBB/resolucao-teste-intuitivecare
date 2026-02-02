CREATE TABLE IF NOT EXISTS despesas_consolidadas (
	id SERIAL PRIMARY KEY,
	cnpj CHAR(14) NOT NULL,
	razao_social VARCHAR(100) NOT NULL,
	trimestre SMALLINT NOT NULL,
	ano SMALLINT NOT NULL,
	registro_ans CHAR(6) NOT NULL,
	modalidade VARCHAR(50),
	uf CHAR(2) NOT NULL,
	valor_despesa DECIMAL(17, 2) NOT NULL 
);




CREATE TABLE IF NOT EXISTS operadoras (
	id SERIAL PRIMARY KEY,
	registro_ans CHAR(6) NOT NULL,
	cnpj CHAR(14) NOT NULL,
	nome_fantasia VARCHAR(100),
	modalidade VARCHAR(50) NOT NULL,
	logradouro VARCHAR(50),
	numero VARCHAR(20) NOT NULL,
	complemento VARCHAR(200),
	bairro VARCHAR(100) NOT NULL,
	cidade VARCHAR(100) NOT NULL,
	UF CHAR(2) NOT NULL,
	cep CHAR(8),
	telefone VARCHAR(20) NOT NULL,
	fax VARCHAR(50),
	endereco_eletronico VARCHAR(50),
	cargo_representante VARCHAR(50),
	regiao_comercializacao VARCHAR(50),
	data_registroans DATE
	
);

CREATE TABLE IF NOT EXISTS dados_agregados(
	razao_social VARCHAR(100) NOT NULL,
	UF CHAR(2) NOT NULL,
	total_geral DECIMAL(17, 2) NOT NULL,
	media_trimestral DECIMAL(17, 2) NOT NULL,
	desvio_padrao_despesas DECIMAL(17, 2) NOT NULL
)