from sqlalchemy import Column, Integer, String, Date, CHAR, DECIMAL, SmallInteger
from database.db import Base 

class Operadora(Base):
    __tablename__ = "operadoras"

    id = Column(Integer, primary_key=True, index=True)
    registro_ans = Column(String(6), nullable=False)
    cnpj = Column(String(14), nullable=False)
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255))
    modalidade = Column(String(50), nullable=False)
    logradouro = Column(String(255))
    numero = Column(String(20))
    complemento = Column(String(255))
    bairro = Column(String(255), nullable=False)
    cidade = Column(String(255), nullable=False)
    uf = Column(String(2), nullable=False)
    cep = Column(String(8))
    ddd = Column(String(5))
    telefone = Column(String(20))
    fax = Column(String(50))
    endereco_eletronico = Column(String(255))
    representante = Column(String(255))
    cargo_representante = Column(String(255))
    regiao_de_comercializacao = Column(String(255))
    data_registro_ans = Column(Date)

class DespesaConsolidada(Base):
    __tablename__ = "despesas_consolidadas"

    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(14), nullable=False)
    razao_social = Column(String(255), nullable=False)
    trimestre = Column(SmallInteger, nullable=False)
    ano = Column(SmallInteger, nullable=False)
    registro_ans = Column(String(6), nullable=False)
    modalidade = Column(String(50))
    uf = Column(String(2), nullable=False)
    valor_despesa = Column(DECIMAL(20, 2), nullable=False)