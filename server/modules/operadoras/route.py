from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Operadora, DespesaConsolidada
from .schema import OperadoraResponse, DespesaConsolidadaSchema, EstatisticasResponse
from database.db import get_db

routes = APIRouter()

@routes.get("/operadoras", response_model=list[OperadoraResponse])
async def get_all_operators(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(None)):
    
    query = db.query(Operadora)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Operadora.razao_social.ilike(search_term)) | 
            (Operadora.cnpj.ilike(search_term))
        )
    
    offset = (page - 1) * limit
    operators = query.offset(offset).limit(limit).all()
    
    results = []
    for op in operators:
        has_expenses = db.query(DespesaConsolidada).filter(DespesaConsolidada.cnpj == op.cnpj).first() is not None
        status = "Ativa com despesas" if has_expenses else "Sem despesas registradas"
        
        op_dict = OperadoraResponse.model_validate(op)
        op_dict.status = status
        results.append(op_dict)
        
    return results


@routes.get("/operadoras/{cnpj}", response_model=OperadoraResponse)
async def get_operator_by_cnpj(cnpj: str, db: Session = Depends(get_db)):
    operator = db.query(Operadora).filter(Operadora.cnpj == cnpj).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operadora not found")
    
    has_expenses = db.query(DespesaConsolidada).filter(DespesaConsolidada.cnpj == cnpj).first() is not None
    status = "Ativa com despesas" if has_expenses else "Sem despesas registradas"
    
    op_response = OperadoraResponse.model_validate(operator)
    op_response.status = status
    return op_response

@routes.get("/operadoras/{cnpj}/despesas", response_model=list[DespesaConsolidadaSchema])
async def get_operator_expenses(cnpj: str, db: Session = Depends(get_db)):
    
    operator = db.query(Operadora).filter(Operadora.cnpj == cnpj).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operadora not found")
        
    expenses = db.query(DespesaConsolidada).filter(DespesaConsolidada.cnpj == cnpj).all()
    return expenses

@routes.get("/estatisticas", response_model=EstatisticasResponse)
async def get_statistics(db: Session = Depends(get_db)):
    total_despesas = db.query(func.sum(DespesaConsolidada.valor_despesa)).scalar() or 0
    
    media_despesas = db.query(func.avg(DespesaConsolidada.valor_despesa)).scalar() or 0
    
    top_5 = db.query(
        DespesaConsolidada.registro_ans,
        DespesaConsolidada.razao_social,
        func.sum(DespesaConsolidada.valor_despesa).label("total_despesa")
    ).group_by(
        DespesaConsolidada.registro_ans,
        DespesaConsolidada.razao_social
    ).order_by(func.sum(DespesaConsolidada.valor_despesa).desc()).limit(5).all()
    
    formatted_top_5 = [
        {"registro_ans": row.registro_ans, "razao_social": row.razao_social, "total_despesa": row.total_despesa}
        for row in top_5
    ]
    
    return {
        "total_despesas": total_despesas,
        "media_despesas": media_despesas,
        "top_5_operadoras": formatted_top_5
    }