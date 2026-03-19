import logging
import time
# from openai import azureopenai  # descomentar para produccion

logger = logging.getLogger(__name__)

class AzureAIFoundryClient:
    """
    cliente de conexion con azure ai foundry para rag y asistentes
    """
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
        
        # codigo produccion
        # self.client = azureopenai(
        #     azure_endpoint=self.endpoint,
        #     api_key=self.api_key,
        #     api_version="2024-02-15-preview"
        # )
        # self.assistant_id = "tu_id_de_asistente_en_azure"

    def create_new_thread(self) -> str:
        """
        crea un hilo conversacional nuevo en azure
        """
        # codigo produccion
        # thread = self.client.beta.threads.create()
        # return thread.id
        
        nuevo_id = f"thread_azure_{int(time.time())}"
        logger.info(f"nuevo thread creado: {nuevo_id}")
        return nuevo_id

    def generate_rag_response(self, user_query: str, thread_id: str, context_params: dict) -> str:
        """
        envia la consulta y parametros al modelo en azure
        """
        # codigo produccion
        # prompt_final = user_query
        # if context_params:
        #     prompt_final += f" [contexto: {context_params}]"
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
        #         raise exception(f"falla en azure con estado: {run.status}")
        #
        # messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        # return messages.data[0].content[0].text.value

        # simulacion
        logger.info(f"simulando generacion rag en hilo {thread_id}")
        time.sleep(1.5) 
        
        query_lower = user_query.lower()
        if "simulacro" in query_lower:
            return "los simulacros se habilitan el fin de semana segun la base de datos."
        
        return f"respuesta inteligente generada para la consulta: {user_query}"