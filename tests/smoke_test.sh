#!/bin/bash
# script devops exhaustivo para validacion de infraestructura externa

# cambia esto al dominio de azure en la fase de produccion
base_url="http://localhost:5000"
token="mi_token_super_secreto"

echo "Iniciando bateria integral de pruebas de infraestructura..."

# diagnostico de red
echo -e "\n1. Comprobando balanceador (health check)..."
curl -s -X GET "$base_url/health"

# escudo de ruta inexistente
echo -e "\n\n2. Escaneando ruta fantasma (404)..."
curl -s -X GET "$base_url/ruta-desconocida"

# escudo perimetral - token falso
echo -e "\n\n3. Simulando ataque con clave falsa (401)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: clave_incorrecta" \
-d '{"queryResult": {"queryText": "Robo de datos"}}'

# escudo perimetral - token ausente
echo -e "\n\n4. Simulando peticion publica sin autorizacion (401)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-d '{"queryResult": {"queryText": "Intentando saltar seguridad"}}'

# inyeccion corrupta
echo -e "\n\n5. Inyectando formato toxico texto plano (400)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: text/plain" \
-H "X-Webhook-Token: $token" \
-d 'Este es un formato invalido'

# carga json vacia
echo -e "\n\n6. Simulando json vacio desde dialogflow (anomalia contenida)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: $token" \
-d '{}'

# anomalia de enrutamiento
echo -e "\n\n7. Simulando accion nativa erronea (anomalia contenida)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: $token" \
-d '{
  "responseId": "test-001",
  "queryResult": {
    "queryText": "Hola",
    "action": "saludar",
    "intent": {"displayName": "saludo_basico"}
  },
  "session": "projects/tesis/sessions/test_001"
}'

# contingencia ia (fallback)
echo -e "\n\n8. Enviando peticion incomprensible para nlu (flujo rag fallback)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: $token" \
-d '{
  "responseId": "test-002",
  "queryResult": {
    "queryText": "Que es la vida",
    "action": "input.unknown",
    "intent": {"displayName": "Default Fallback Intent"}
  },
  "session": "projects/tesis/sessions/test_002"
}'

# orquestacion exitosa
echo -e "\n\n9. Enviando peticion valida esperada (flujo rag principal)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: $token" \
-d '{
  "responseId": "test-003",
  "queryResult": {
    "queryText": "Fecha de matriculas",
    "action": "requiere_rag",
    "intent": {"displayName": "consulta_fechas"}
  },
  "session": "projects/tesis/sessions/test_003"
}'

echo -e "\n\nPruebas finalizadas. el ataque de saturacion (ddos) se deja en pytest para mantener limpia la memoria de desarrollo."