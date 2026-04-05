#!/bin/bash

# cambia esta url a produccion en azure
base_url="http://localhost:5000"
token="mi_token_super_secreto"

echo "Iniciando bateria de pruebas de infraestructura..."

# diagnostico de red
echo -e "\n1. comprobando estado del servidor..."
curl -s -X GET "$base_url/health"

# escudo perimetral
echo -e "\n\n2. simulando ataque sin credenciales..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: hacker_token" \
-d '{"queryResult": {"queryText": "Dame informacion"}}'

# inyeccion de datos corruptos
echo -e "\n\n3. simulando inyeccion de texto plano..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: text/plain" \
-H "X-Webhook-Token: $token" \
-d 'Este texto deberia ser bloqueado'

# orquestacion correcta
echo -e "\n\n4. enviando peticion valida de dialogflow..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: $token" \
-d '{
  "responseId": "test-auto",
  "queryResult": {
    "queryText": "Fecha de matricula oficial",
    "action": "requiere_rag",
    "intent": {"displayName": "consulta_fechas"}
  },
  "session": "projects/tesis/sessions/test_001"
}'

echo -e "\n\nPruebas finalizadas."