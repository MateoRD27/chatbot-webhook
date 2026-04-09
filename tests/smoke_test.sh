#!/bin/bash
# script devops exhaustivo para validacion de infraestructura externa

# cambia esto al dominio de azure en la fase de produccion
base_url="http://localhost:5000"
token="mi_token_super_secreto"

echo "Iniciando bateria integral de pruebas de infraestructura..."

# 1. diagnostico de red
echo -e "\n1. Comprobando balanceador (health check)..."
curl -s -X GET "$base_url/health"

# 2. escudo de ruta inexistente
echo -e "\n\n2. Escaneando ruta fantasma (404)..."
curl -s -X GET "$base_url/ruta-desconocida"

# 3. escudo perimetral - token falso
echo -e "\n\n3. Simulando ataque con clave falsa (401)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: Clave_incorrecta" \
-d '{"queryResult": {"queryText": "Robo de datos"}}'

# 4. escudo perimetral - token ausente
echo -e "\n\n4. Simulando peticion publica sin autorizacion (401)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-d '{"queryResult": {"queryText": "Intentando saltar seguridad"}}'

# 5. inyeccion corrupta
echo -e "\n\n5. Inyectando formato toxico texto plano (400)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: text/plain" \
-H "X-Webhook-Token: $token" \
-d 'Este es un formato invalido'

# 6. carga json vacia
echo -e "\n\n6. Simulando json vacio desde dialogflow (anomalia contenida)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: $token" \
-d '{}'

# 7. anomalia de enrutamiento
echo -e "\n\n7. Simulando accion nativa erronea (anomalia contenida)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: $token" \
-d '{
  "responseId": "Test-001",
  "queryResult": {
    "queryText": "Hola",
    "action": "Saludar",
    "intent": {"displayName": "Saludo_basico"}
  },
  "session": "projects/tesis/sessions/test_001"
}'

# 8. contingencia ia (fallback)
echo -e "\n\n8. Enviando peticion incomprensible para nlu (flujo rag fallback)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: $token" \
-d '{
  "responseId": "Test-002",
  "queryResult": {
    "queryText": "Que es la vida",
    "action": "Input.unknown",
    "intent": {"displayName": "Default Fallback Intent"}
  },
  "session": "projects/tesis/sessions/test_002"
}'

# 9. Peticion RAG Principal (Dispara el hilo de fondo)
echo -e "\n\n9. Enviando peticion RAG (Inicia hilo y primer evento)..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: $token" \
-d '{
  "queryResult": {
    "queryText": "Profesores sistemas",
    "action": "requiere_rag",
    "intent": {"displayName": "consulta_profesores"}
  },
  "session": "projects/tesis/sessions/smoke_test_001"
}'

# 10. Simulacion de Bucle de Espera (Polling)
echo -e "\n\n10. Simulando llamada de Dialogflow tras recibir el evento..."
curl -s -X POST "$base_url/webhook" \
-H "Content-Type: application/json" \
-H "X-Webhook-Token: $token" \
-d '{
  "queryResult": {
    "queryText": "",
    "intent": {"displayName": "intent_espera"}
  },
  "session": "projects/tesis/sessions/smoke_test_001"
}'
echo -e "\n\nPruebas finalizadas. el ataque de saturacion (ddos) se deja en pytest para mantener limpia la memoria de desarrollo."