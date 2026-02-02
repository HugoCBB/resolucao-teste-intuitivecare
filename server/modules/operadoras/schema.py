from pydantic import BaseModel
from datetime import date
from typing import Optional

class OperadoraSchema(BaseModel):
    registro_ans: str
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    modalidade: str
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    uf: str
    cep: Optional[str] = None
    ddd: Optional[str] = None
    telefone: Optional[str] = None
    fax: Optional[str] = None
    endereco_eletronico: Optional[str] = None
    representante: Optional[str] = None
    cargo_representante: Optional[str] = None
    regiao_de_comercializacao: Optional[str] = None
    data_registro_ans: Optional[date] = None

    class Config:
        from_attributes = True

class OperadoraResponse(OperadoraSchema):
    id: int
    status: str = "Sem despesas registradas"

class DespesaConsolidadaSchema(BaseModel):
    cnpj: str
    razao_social: str
    trimestre: int
    ano: int
    registro_ans: str
    modalidade: Optional[str] = None
    uf: str
    valor_despesa: float

    class Config:
        from_attributes = True

class TopOperator(BaseModel):
    registro_ans: str
    razao_social: str
    total_despesa: float

class EstatisticasResponse(BaseModel):
    total_despesas: float
    media_despesas: float
    top_5_operadoras: list[TopOperator]