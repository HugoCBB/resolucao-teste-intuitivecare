CREATE TABLE IF NOT EXISTS despesas_consolidadas (
	id SERIAL PRIMARY KEY,
	cnpj CHAR(14) NOT NULL,
	razao_social VARCHAR(255) NOT NULL,
	trimestre SMALLINT NOT NULL,
	ano SMALLINT NOT NULL,
	registro_ans CHAR(6) NOT NULL,
	modalidade VARCHAR(50),
	uf CHAR(2) NOT NULL,
	valor_despesa DECIMAL(20, 2) NOT NULL 
);




CREATE TABLE IF NOT EXISTS operadoras (
	id SERIAL PRIMARY KEY,
	registro_ans CHAR(6) NOT NULL,
	cnpj CHAR(14) NOT NULL,
	razao_social VARCHAR(255) NOT NULL,
	nome_fantasia VARCHAR(255),
	modalidade VARCHAR(50) NOT NULL,
	logradouro VARCHAR(255),
	numero VARCHAR(20),
	complemento VARCHAR(255),
	bairro VARCHAR(255) NOT NULL,
	cidade VARCHAR(255) NOT NULL,
	uf CHAR(2) NOT NULL,
	cep CHAR(8),
	ddd VARCHAR(5),
	telefone VARCHAR(20),
	fax VARCHAR(50),
	endereco_eletronico VARCHAR(255),
	representante VARCHAR(255),
	cargo_representante VARCHAR(255),
	regiao_de_comercializacao VARCHAR(255),
	data_registro_ans DATE
	
);

CREATE TABLE IF NOT EXISTS dados_agregados(
	razao_social VARCHAR(255) NOT NULL,
	uf CHAR(2) NOT NULL,
	total_geral DECIMAL(20, 2) NOT NULL,
	media_trimestral DECIMAL(20, 2) NOT NULL,
	desvio_padrao_despesas DECIMAL(20, 2) NOT NULL
);