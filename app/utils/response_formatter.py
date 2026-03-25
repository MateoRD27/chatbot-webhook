
def build_text_response(text: str) -> dict:
    """
    construye la respuesta estandar de texto plano para dialogflow
    """
    return {
        "fulfillmentText": text
    }

def build_card_response(text: str, title: str, subtitle: str, button_text: str, button_link: str) -> dict:
    """
    construye una tarjeta interactiva con botones.
    esta funcion queda lista por si la inteligencia artificial decide 
    enviar enlaces enriquecidos en el futuro.
    """
    return {
        "fulfillmentText": text,
        "fulfillmentMessages": [
            {
                "card": {
                    "title": title,
                    "subtitle": subtitle,
                    "buttons": [
                        {
                            "text": button_text,
                            "postback": button_link
                        }
                    ]
                }
            }
        ]
    }