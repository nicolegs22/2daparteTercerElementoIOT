#ifndef AWS_SHADOW_H
#define AWS_SHADOW_H

#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "Motor.h"
#include "Sensor.h"
#include "Display.h"

class AWSShadow {
public:
  AWSShadow(const char* thingName, const char* endpoint, int port,
            const char* rootCA, const char* deviceCert, const char* privateKey,
            Motor& motor, Sensor& sensor, Display& display);

  bool connect();
  void loop();
  void requestShadowDocument();
  void publishReported(float temperature, int speedPercent);

  // topics
  String deltaTopic;
  String getTopic;
  String updateTopic;

private:
  static void mqttCallback(char* topic, byte* payload, unsigned int length);
  void handleDelta(const char* json);
  

  const char* thingName_;
  const char* endpoint_;
  int port_;
  const char* rootCA_;
  const char* deviceCert_;
  const char* privateKey_;

  WiFiClientSecure net_;
  PubSubClient mqtt_;

  Motor& motor_;
  Sensor& sensor_;
  Display& display_;
  static AWSShadow* instance_;

};

#endif