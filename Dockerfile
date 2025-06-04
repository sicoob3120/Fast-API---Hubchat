FROM python:3.11-slim

WORKDIR /app

# Copia tudo
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta
EXPOSE 8080

# Comando de execução
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port=8080", "--lifespan", "on"]
