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
        filtro["CPF/CNPJ"] = cpf_cnpj
    if cooperativa_origem_divida:
        filtro["Cooperativa Origem Divida"] = cooperativa_origem_divida
    if pac:
        filtro["PAC"] = pac
    if acionado:
        filtro["Acionado"] = acionado
    if a_cobrar:
        filtro["A Cobrar"] = a_cobrar
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
        filtro["Qtd. Dias Atraso"] = {"$gte": qtd_dias_atraso_min}
    if valor_operacao_min is not None:
        filtro["Valor Operacao"] = {"$gte": valor_operacao_min}
    if valor_atualizado_min is not None:
        filtro["Valor Atualizado"] = {"$gte": valor_atualizado_min}

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
def listar_avisos():
    return list(db.avisos.find({}, {"_id": 0}))
