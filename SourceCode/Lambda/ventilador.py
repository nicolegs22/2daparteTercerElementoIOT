import json
import boto3
import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

THING_NAME = "Esp32Ventilador"
REGION     = "us-east-1"

REPROMPT = "¿Qué más quieres saber del ventilador?"


def get_iot_data_client():
    iot = boto3.client("iot", region_name=REGION)
    endpoint = iot.describe_endpoint(endpointType="iot:Data-ATS")["endpointAddress"]
    return boto3.client(
        "iot-data",
        region_name=REGION,
        endpoint_url=f"https://{endpoint}",
    )

def get_shadow_state() -> dict:
    client = get_iot_data_client()
    response = client.get_thing_shadow(thingName=THING_NAME)
    return json.loads(response["payload"].read())

def get_shadow_variable(variable: str, section: str = "reported", default=None):
    try:
        payload = get_shadow_state()
        return payload.get("state", {}).get(section, {}).get(variable, default)
    except Exception as e:
        logger.error(f"Error obteniendo {variable} de {section}: {e}")
        return default

def set_shadow_speed(speed: int) -> bool:
    try:
        client = get_iot_data_client()
        client.update_thing_shadow(
            thingName=THING_NAME,
            payload=json.dumps({
                "state": {"desired": {"speed": speed}}
            })
        )
        return True
    except Exception as e:
        logger.error(f"Error actualizando speed: {e}")
        return False



class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech = (
            "Bienvenido al control del ventilador. "
            "Puedes preguntarme la temperatura, la velocidad, "
            "el estado completo, o decirme que cambie la velocidad."
        )
        return (
            handler_input.response_builder
            .speak(speech)
            .ask(REPROMPT)       
            .response
        )



class HelloIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("HelloIntent")(handler_input)

    def handle(self, handler_input):
        speech = "Hola! Estoy aquí para ayudarte a controlar tu ventilador."
        return (
            handler_input.response_builder
            .speak(speech)
            .ask(REPROMPT)       
            .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech = (
            "Puedes decirme: temperatura, velocidad actual, estado completo, "
            "enciende el ventilador, apaga el ventilador, "
            "o cambia la velocidad a un número entre cero y cien."
        )
        return (
            handler_input.response_builder
            .speak(speech)
            .ask(REPROMPT)       
            .response
        )



class GetTemperatureIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GetTemperatureIntent")(handler_input)

    def handle(self, handler_input):
        temp = get_shadow_variable("temperature")
        if temp is None:
            speech = "No pude obtener la temperatura del ventilador."
        else:
            speech = f"La temperatura actual es de {temp} grados."
        return (
            handler_input.response_builder
            .speak(speech)
            .ask(REPROMPT)       
            .response
        )



class GetSpeedLevelIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GetSpeedLevelIntent")(handler_input)

    def handle(self, handler_input):
        speed = get_shadow_variable("speed")
        if speed is None:
            speech = "No pude obtener la velocidad del ventilador."
        elif speed == 0:
            speech = "El ventilador está apagado, su velocidad es cero."
        else:
            speech = f"La velocidad actual del ventilador es {speed}."
        return (
            handler_input.response_builder
            .speak(speech)
            .ask(REPROMPT)       
            .response
        )



class GetAllValuesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GetAllValuesIntent")(handler_input)

    def handle(self, handler_input):
        try:
            payload  = get_shadow_state()
            reported = payload.get("state", {}).get("reported", {})
            speed    = reported.get("speed", None)
            temp     = reported.get("temperature", None)

            if speed is None or temp is None:
                speech = "No pude obtener el estado completo del ventilador."
            else:
                estado = "apagado" if speed == 0 else f"encendido a velocidad {speed}"
                speech = (
                    f"Estado completo: temperatura {temp} grados, "
                    f"velocidad {speed}, el ventilador está {estado}."
                )
        except Exception as e:
            logger.error(f"GetAllValuesIntent error: {e}")
            speech = "Hubo un error al obtener el estado completo."

        return (
            handler_input.response_builder
            .speak(speech)
            .ask(REPROMPT)       
            .response
        )


class UpdateSpeedLevelIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("UpdateSpeedLevelIntent")(handler_input)

    def handle(self, handler_input):
        slots     = handler_input.request_envelope.request.intent.slots
        raw_speed = slots.get("speed") and slots["speed"].value

        if raw_speed is None:
            speech = "¿A qué velocidad quieres poner el ventilador? Di un número entre cero y cien."
            return handler_input.response_builder.speak(speech).ask(speech).response

        try:
            speed = int(float(raw_speed))
        except (ValueError, TypeError):
            speech = "No entendí el número. Di una velocidad entre cero y cien."
            return handler_input.response_builder.speak(speech).ask(speech).response

        if not (0 <= speed <= 100):
            speech = f"{speed} está fuera de rango. La velocidad debe ser entre cero y cien."
            return handler_input.response_builder.speak(speech).ask(speech).response

        ok = set_shadow_speed(speed)
        if ok:
            speech = "El ventilador ha sido apagado." if speed == 0 else f"Velocidad actualizada a {speed}."
        else:
            speech = "No pude actualizar la velocidad. Inténtalo de nuevo."

        return (
            handler_input.response_builder
            .speak(speech)
            .ask(REPROMPT)       
            .response
        )


class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input)
            or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)
        )

    def handle(self, handler_input):
        # Sin .ask() → cierra la sesión intencionalmente
        return handler_input.response_builder.speak("Hasta luego.").response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(f"Excepción no controlada: {exception}", exc_info=True)
        speech = "Hubo un problema. Por favor intenta de nuevo."
        return (
            handler_input.response_builder
            .speak(speech)
            .ask(REPROMPT)
            .response
        )


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(GetTemperatureIntentHandler())
sb.add_request_handler(GetSpeedLevelIntentHandler())
sb.add_request_handler(GetAllValuesIntentHandler())
sb.add_request_handler(UpdateSpeedLevelIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()