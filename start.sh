#!/bin/bash
echo "Iniciando servidor Uvicorn na porta 8080..."
exec uvicorn main:app --host 0.0.0.0 --port=8080 --lifespan on --timeout-keep-alive 120 --log-level debug
