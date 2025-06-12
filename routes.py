from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pandas as pd
import io
from fastapi.responses import StreamingResponse

# Carrega .env do mesmo diretório ou pai automaticamente
load_dotenv()

router = APIRouter()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
API_KEY = os.getenv("API_KEY")

# Log para debug
print("MONGO_URI:", MONGO_URI)
print("MONGO_DB:", MONGO_DB)
print("API_KEY:", API_KEY)

# Verifica conexão com MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
except Exception as e:
    print("Erro ao conectar no MongoDB:", e)
    raise

def verificar_token(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Token inválido")

@router.get("/associados", dependencies=[Depends(verificar_token)])
def listar_associados():
    return list(db.todos_associados.find({}, {"_id": 0}))

@router.get("/fichas-cobranca", dependencies=[Depends(verificar_token)])
def listar_fichas(
    nome: str = Query(None),
    cpf_cnpj: str = Query(None),
    cooperativa_origem_divida: str = Query(None),
    pac: str = Query(None),
    acionado: str = Query(None),
    a_cobrar: str = Query(None),
    produto: str = Query(None),
    carteira: str = Query(None),
    risco: str = Query(None),
    contrato: str = Query(None),
    qtd_dias_atraso_min: int = Query(None),
    valor_operacao_min: float = Query(None),
    valor_atualizado_min: float = Query(None),
    skip: int = Query(0),
    limit: int = Query(1000)
):
    filtro = {}

    # Textos com regex (Nome)
    if nome:
        filtro["Nome"] = {"$regex": nome, "$options": "i"}
    
    # Filtros exatos
    if cpf_cnpj:
        filtro["CPF_CNPJ"] = cpf_cnpj
    if cooperativa_origem_divida:
        filtro["Cooperativa_Origem_Divida"] = cooperativa_origem_divida
    if pac:
        filtro["PAC"] = pac
    if acionado:
        filtro["Acionado"] = acionado
    if a_cobrar:
        filtro["A_Cobrar"] = a_cobrar
    if produto:
        filtro["Produto"] = produto
    if carteira:
        filtro["Carteira"] = carteira
    if risco:
        filtro["Risco"] = risco
    if contrato:
        filtro["Contrato"] = contrato
    
    # Filtros numéricos
    if qtd_dias_atraso_min is not None:
        filtro["Qtd_Dias_Atraso"] = {"$gte": qtd_dias_atraso_min}
    if valor_operacao_min is not None:
        filtro["Valor_Operacao"] = {"$gte": valor_operacao_min}
    if valor_atualizado_min is not None:
        filtro["Valor_Atualizado"] = {"$gte": valor_atualizado_min}

    fichas = list(db.fichas_cobranca.find(filtro, {"_id": 0}).skip(skip).limit(limit))
    return fichas

@router.get("/fichas-cobranca/exportar", dependencies=[Depends(verificar_token)])
def exportar_fichas():
    # Pega tudo sem limite
    fichas = list(db.fichas_cobranca.find({}, {"_id": 0}))
    df = pd.DataFrame(fichas)
    
    # Converte para CSV em memória
    stream = io.StringIO()
    df.to_csv(stream, index=False, sep=';')
    stream.seek(0)
    
    # Retorna como download de arquivo
    return StreamingResponse(stream, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=fichas_cobranca.csv"})

@router.get("/avisos", dependencies=[Depends(verificar_token)])
def listar_avisos(
    nome_cliente: str = Query(None),
    numero_cpf_cnpj: str = Query(None),
    nome_gerente: str = Query(None),
    carteira: str = Query(None),
    finalidade_operacao_credito: str = Query(None),
    numero_contrato_credito: str = Query(None),
    situacao_parcela: str = Query(None),
    valor_parcela_min: float = Query(None),
    saldo_devedor_cliente_min: float = Query(None),
    skip: int = Query(0),
    limit: int = Query(1000)
):
    filtro = {}

    # Textos com regex
    if nome_cliente:
        filtro["nome_cliente"] = {"$regex": nome_cliente, "$options": "i"}
    if nome_gerente:
        filtro["nome_gerente"] = {"$regex": nome_gerente, "$options": "i"}
    if finalidade_operacao_credito:
        filtro["finalidade_operacao_credito"] = {"$regex": finalidade_operacao_credito, "$options": "i"}
    
    # Filtros exatos
    if numero_cpf_cnpj:
        filtro["numero_cpf_cnpj"] = numero_cpf_cnpj
    if carteira:
        filtro["carteira"] = carteira
    if numero_contrato_credito:
        filtro["numero_contrato_credito"] = numero_contrato_credito
    if situacao_parcela:
        filtro["situacao_parcela"] = situacao_parcela
    
    # Filtros numéricos
    if valor_parcela_min is not None:
        filtro["valor_parcela"] = {"$gte": valor_parcela_min}
    if saldo_devedor_cliente_min is not None:
        filtro["saldo_devedor_cliente"] = {"$gte": saldo_devedor_cliente_min}

    avisos = list(db.avisos.find(filtro, {"_id": 0}).skip(skip).limit(limit))
    return avisos

@router.get("/avisos/exportar", dependencies=[Depends(verificar_token)])
def exportar_avisos():
    # Pega tudo sem limite
    avisos = list(db.avisos.find({}, {"_id": 0}))
    df = pd.DataFrame(avisos)
    
    # Converte para CSV em memória
    stream = io.StringIO()
    df.to_csv(stream, index=False, sep=';')
    stream.seek(0)
    
    # Retorna como download de arquivo
    return StreamingResponse(stream, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=avisos.csv"})
