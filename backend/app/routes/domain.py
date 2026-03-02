from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.domain import Domain
from app.schemas.schemas import DomainCreate, DomainResponse
from app.database import get_db
from uuid import uuid4

router = APIRouter(prefix="/domains", tags=["Domains"])

# Simulação de autenticação (substitua por OAuth2/JWT em produção)
def get_current_user_id():
    return 1  # Exemplo fixo

@router.get("/", response_model=List[DomainResponse])
def list_domains(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return db.query(Domain).filter_by(user_id=user_id).all()

@router.post("/", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
def create_domain(domain_in: DomainCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    if db.query(Domain).filter_by(domain=domain_in.domain).first():
        raise HTTPException(status_code=400, detail="Domínio já cadastrado")
    token = str(uuid4())
    domain = Domain(user_id=user_id, domain=domain_in.domain, token=token)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain

@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_domain(domain_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    domain = db.query(Domain).filter_by(id=domain_id, user_id=user_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domínio não encontrado")
    db.delete(domain)
    db.commit()
    return

@router.post("/{domain_id}/regenerate-token", response_model=DomainResponse)
def regenerate_token(domain_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    domain = db.query(Domain).filter_by(id=domain_id, user_id=user_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domínio não encontrado")
    domain.token = str(uuid4())
    db.commit()
    db.refresh(domain)
    return domain
