# app/clients/azure_ai_client.py
import logging
import time
# from openai import azureopenai # linea real para produccion

logger = logging.getLogger(__name__)

class AzureAIFoundryClient:
    """
    cliente para interactuar con azure ai foundry y consultar la base de conocimiento rag
    """
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
        
        # --- inicio bloque de produccion ---
        # self.client = azureopenai(
        #     azure_endpoint=self.endpoint,
        #     api_key=self.api_key,
        #     api_version="2024-02-15-preview"
        # )
        # self.assistant_id = "tu_id_de_asistente_en_azure"
        # --- fin bloque de produccion ---

    def create_new_thread(self) -> str:
        """
        solicita a azure la creacion de un hilo nuevo para guardar el contexto
        """
        # --- inicio bloque de produccion ---
        # thread = self.client.beta.threads.create()
        # return thread.id
        # --- fin bloque de produccion ---
        
        nuevo_id = f"thread_azure_{int(time.time())}"
        logger.info(f"nuevo thread simulado: {nuevo_id}")
        return nuevo_id

    def generate_rag_response(self, user_query: str, thread_id: str, context_params: dict) -> str:
        """
        envia la consulta al modelo rag y espera la respuesta generada
        """
        # --- inicio bloque de produccion ---
        # prompt_final = user_query
        # if context_params:
        #     prompt_final += f" [contexto adicional: {context_params}]"
        #
        # self.client.beta.threads.messages.create(
        #     thread_id=thread_id, role="user", content=prompt_final
        # )
        #
        # run = self.client.beta.threads.runs.create(
        #     thread_id=thread_id, assistant_id=self.assistant_id
        # )
        #
        # while run.status != "completed":
        #     time.sleep(1)
        #     run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        #     if run.status in ["failed", "cancelled", "expired"]:
        #         raise exception(f"el modelo de azure fallo. estado final: {run.status}")
        #
        # messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        # return messages.data[0].content[0].text.value
        # --- fin bloque de produccion ---

        # --- inicio bloque de simulacion (prueba de matriculas) ---
        logger.info(f"simulando busqueda en base de conocimiento rag. hilo: {thread_id}")
        time.sleep(1.5) 
        
        query_lower = user_query.lower()
        if "matricula" in query_lower or "fecha" in query_lower:
            return "segun el calendario academico oficial, las matriculas para el proximo semestre estan programadas del 15 al 30 de agosto."
        
        return f"respuesta dinamica generada por ia para: '{user_query}'"
        # --- fin bloque de simulacion ---