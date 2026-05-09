## Integrantes:

* Gabriel Herrera
* Nicole Gomez
* Fernando Rodriguez


# Especificación de Requerimientos Funcionales
## Proyecto: Skill de Alexa - Ventiladora Inteligente

### Objetivo General
Controlar remotamente una ventiladora mediante comandos de voz a través de Alexa, utilizando AWS IoT Core como intermediario entre Alexa y el hardware (ESP32).

---

### 1. Control de Encendido/Apagado
| ID | Requerimiento | Descripción |
| :--- | :--- | :--- |
| **RF-01** | Encender ventiladora | El usuario puede decir: "Alexa, enciende la ventiladora", "Alexa, prende el ventilador" o "Alexa, turn on the fan". La skill envía al shadow "desired": {"speed": 100} o restaura la última velocidad guardada. |
| **RF-02** | Apagar ventiladora | El usuario puede decir: "Alexa, apaga la ventiladora", "Alexa, apaga el ventilador" o "Alexa, turn off the fan". La skill envía al shadow "desired": {"speed": 0}. |
| **RF-03** | Estado On/Off en tiempo real | Alexa debe poder responder si la ventiladora está encendida o apagada cuando el usuario pregunta: "Alexa, ¿está encendida la ventiladora?" o "Alexa, is the fan on?". |

---

### 2. Control de Velocidad
| ID | Requerimiento | Descripción |
| :--- | :--- | :--- |
| **RF-04** | Ajustar velocidad por porcentaje | El usuario debe poder establecer la velocidad exacta: "Alexa, pon la ventiladora al 50%", "Alexa, set the fan to 75%", "Alexa, cambia la velocidad del ventilador a 40%". |
| **RF-05** | Ajustar velocidad relativa | El usuario debe poder subir o bajar la velocidad: "Alexa, sube la velocidad", "Alexa, baja la velocidad". Incremento/decremento sugerido: +/- 25%. |
| **RF-06** | Velocidad mínima configurable | Cuando se encienda el ventilador, la velocidad mínima debe ser 35% (no puede ser menor a este valor cuando esté encendido). |
| **RF-07** | Velocidad máxima | La velocidad máxima debe ser 100%. |
| **RF-08** | Validación de rango | Si el usuario solicita una velocidad fuera de rango (ej: 10%), Alexa debe responder: "La velocidad debe estar entre 35% y 100% cuando el ventilador está encendido". |
| **RF-09** | Velocidades predefinidas | Implementar comandos para velocidades comunes: Mínimo (35%), Medio (50%), Alto (75%), Máximo (100%). |

---

### 3. Consulta de Temperatura
| ID | Requerimiento | Descripción |
| :--- | :--- | :--- |
| **RF-10** | Consultar temperatura actual | El usuario debe poder preguntar la temperatura: "Alexa, ¿qué temperatura hace?". La skill debe obtener la temperatura del shadow reported. |
| **RF-11** | Unidad de temperatura | Alexa debe responder con la temperatura en grados Celsius: "La temperatura actual es de 23.5 grados Celsius". |
| **RF-12** | Temperatura no disponible | Si el sensor falla, Alexa debe responder: "No puedo obtener la temperatura en este momento, el sensor no está disponible". |

---

### 4. Consulta de Estado Completo
| ID | Requerimiento | Descripción |
| :--- | :--- | :--- |
| **RF-13** | Estado general del ventilador | El usuario debe poder preguntar el estado completo: "Alexa, ¿cómo está la ventiladora?", "¿Estado del ventilador?". |
| **RF-14** | Respuesta detallada del estado | Alexa debe responder con un resumen: "La ventiladora está encendida al 60%, la temperatura actual es de 24.2 grados Celsius". |
| **RF-15** | Estado cuando está apagada | Si está apagada, responder: "La ventiladora está apagada. La temperatura actual es de 22.8 grados Celsius". |

---

### 5. Seguridad y Manejo de Errores
| ID | Requerimiento | Descripción |
| :--- | :--- | :--- |
| **RF-16** | Límite de velocidad mínima al encender | Si se intenta encender con velocidad < 35%, automáticamente establecer al 35% y notificar al usuario. |
| **RF-17** | Apagado cuando velocidad = 0 | Si la velocidad se establece en 0%, interpretar automáticamente como un comando de apagado. |
| **RF-18** | Timeout de comunicación | Si AWS IoT no responde en 5 segundos, Alexa debe decir: "La ventiladora no está respondiendo en este momento, intenta de nuevo más tarde". |
| **RF-19** | Notificar cambios realizados | Cada comando exitoso debe ser confirmado: "Ventiladora encendida al 50%", "Velocidad ajustada al 75%". |

---

### 6. Integración con AWS IoT Shadow
| ID | Requerimiento | Descripción |
| :--- | :--- | :--- |
| **RF-20** | Comunicación bidireccional | La skill de Alexa debe enviar comandos al shadow desired y leer el shadow reported para telemetría. |
| **RF-21** | Formato del Shadow | Estructura requerida: {"state": {"desired": {"speed": 0}, "reported": {"temperature": 23.4, "speed": 0}}}. |
| **RF-22** | Sincronización inicial | Al vincular la skill, debe leer el estado actual del shadow para conocer la velocidad y temperatura actuales. |

---

### 7. Interfaz de Voz (Utterances sugeridas)
* Encendido/Apagado:
    * "Enciende la ventiladora"
    * "Prende el ventilador"
    * "Apaga la ventiladora"
    * "Turn off the fan"
* Velocidad:
    * "Pon la ventiladora al {porcentaje} por ciento"
    * "Sube la velocidad"
    * "Pon la ventiladora al máximo"
* Consulta:
    * "¿Qué temperatura hace?"
    * "¿Cómo está la ventiladora?"
    * "Is the fan on?"

## Diagramas 

### ***Diagrama Electrico Ventiladora Inteligente***
<p align="center">
  <img src="diagrams/Diagrama_Electronico.jpeg" width="600" alt="Diagrama Eléctrico Ventiladora Inteligente"/>
</p>


### ***Diagrama de Arquitectura de la Ventiladora Inteligente***
<p align="center">
<img src="diagrams/ARQUITECTURA _DE _VENTILADORA.jpg" width="600">

