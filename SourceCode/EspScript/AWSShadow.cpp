#include "AWSShadow.h"

AWSShadow* AWSShadow::instance_ = nullptr;

AWSShadow::AWSShadow(const char* thingName, const char* endpoint, int port,
                     const char* rootCA, const char* deviceCert, const char* privateKey,
                     Motor& motor, Sensor& sensor, Display& display)
  : thingName_(thingName), endpoint_(endpoint), port_(port),
    rootCA_(rootCA), deviceCert_(deviceCert), privateKey_(privateKey),
    mqtt_(net_),
    motor_(motor), sensor_(sensor), display_(display)
{
  deltaTopic  = String("$aws/things/") + thingName_ + "/shadow/update/delta";
  getTopic    = String("$aws/things/") + thingName_ + "/shadow/get";
  updateTopic = String("$aws/things/") + thingName_ + "/shadow/update";

  net_.setCACert(rootCA_);
  net_.setCertificate(deviceCert_);
  net_.setPrivateKey(privateKey_);

  mqtt_.setServer(endpoint_, port_);
  mqtt_.setCallback(mqttCallback);
  mqtt_.setBufferSize(512);
  
  instance_ = this;
}

bool AWSShadow::connect() {
  display_.showMessage("Conectando AWS...", "", motor_.getSpeedPercent());
  Serial.print("Conectando a AWS IoT...");
  if (mqtt_.connect(thingName_)) {
    Serial.println(" Conectado");
    mqtt_.subscribe(deltaTopic.c_str());
    Serial.printf("Suscrito a %s\n", deltaTopic.c_str());
    display_.showMessage("AWS Conectado", "", motor_.getSpeedPercent());
    return true;
  } else {
    Serial.println(" Fallo conexión MQTT");
    return false;
  }
}

void AWSShadow::loop() {
  if (!mqtt_.connected()) {
    if (connect()) {
      requestShadowDocument();
    } else {
      delay(1000);
      return;
    }
  }
  mqtt_.loop();
}

void AWSShadow::requestShadowDocument() {
  mqtt_.publish(getTopic.c_str(), "{}");
  Serial.println("Solicitado shadow document");
}

void AWSShadow::mqttCallback(char* topic, byte* payload, unsigned int length) {
  char msg[length + 1];
  memcpy(msg, payload, length);
  msg[length] = '\0';
  Serial.printf("MQTT mensaje en %s: %s\n", topic, msg);

  if (instance_ && String(topic) == instance_->deltaTopic) {
    instance_->handleDelta(msg);
  }
}

void AWSShadow::handleDelta(const char* json) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, json);
  if (error) {
    Serial.println("Error parseando JSON delta");
    return;
  }
  if (doc.containsKey("state") && doc["state"].containsKey("speed")) {
    int percent = doc["state"]["speed"];
    motor_.setSpeedFromShadow(percent);
    // Actualiza la pantalla inmediatamente con el nuevo valor
    float temp = sensor_.readTemperature();
    display_.showNormal(temp, motor_.getSpeedPercent());
  }
}

void AWSShadow::publishReported(float temperature, int speedPercent) {
  StaticJsonDocument<256> doc;
  JsonObject state = doc.createNestedObject("state");
  JsonObject reported = state.createNestedObject("reported");

  if (!isnan(temperature)) {
    reported["temperature"] = temperature;
  }
  reported["speed"] = speedPercent;

  char buffer[256];
  serializeJson(doc, buffer);
  Serial.printf("Publicando shadow update: %s\n", buffer);

  if (mqtt_.publish(updateTopic.c_str(), buffer)) {
    Serial.println("Publicado correctamente");
  } else {
    Serial.println("Fallo en publicación");
  }
}