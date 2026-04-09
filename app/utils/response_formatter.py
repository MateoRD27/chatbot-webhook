def build_text_response(text: str) -> dict:
    """
    construye la respuesta estandar de texto plano para dialogflow
    """
    return {
        "fulfillmentText": text
    }

def build_event_response(event_name: str) -> dict:
    """
    construye la respuesta especial para reiniciar el contador de 5s de dialogflow
    """
    return {
        "followupEventInput": {
            "name": event_name,
            "languageCode": "es"
        }
    }

def build_card_response(text: str, title: str, subtitle: str, button_text: str, button_link: str) -> dict:
    """
    construye una tarjeta interactiva con botones.
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