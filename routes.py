from fastapi import APIRouter, Depends, Header, HTTPException
from pymongo import MongoClient
import os
from dotenv import load_dotenv

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
def listar_fichas():
    return list(db.fichas_cobranca.find({}, {"_id": 0}))

@router.get("/avisos", dependencies=[Depends(verificar_token)])
def listar_avisos():
    return list(db.avisos.find({}, {"_id": 0}))
