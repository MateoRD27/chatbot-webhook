# orquestador del asistente virtual webhook (proyecto de grado)

middleware desarrollado en python y flask utilizando arquitectura por capas.
conecta la capa nlu (dialogflow) con la capa de inteligencia (azure ai foundry).
utiliza redis para el manejo en memoria de las sesiones conversacionales.

## configuracion inicial
solicitar las llaves de desarrollo al administrador y crear el archivo .env en la raiz.

## entorno local (linux mint / macos)
\`\`\`bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

## entorno local (windows)
\`\`\`cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

## ejecucion
\`\`\`bash
python run.py
\`\`\`
el servidor expone el endpoint en http://localhost:5000/webhook