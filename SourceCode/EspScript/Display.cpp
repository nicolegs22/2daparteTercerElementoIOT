#include "Display.h"

Display::Display(uint8_t addr, int sda, int scl)
  : oled_(128, 64, &Wire, -1)
{
  Wire.begin(sda, scl);
}

bool Display::begin() {
  if (!oled_.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("Display: init failed");
    return false;
  }
  oled_.clearDisplay();
  oled_.setTextSize(1);
  oled_.setTextColor(SSD1306_WHITE);
  return true;
}

void Display::showNormal(float temperature, int speedPercent) {
  oled_.clearDisplay();
  oled_.setCursor(0, 0);
  if (isnan(temperature)) {
    oled_.print("Sensor error");
  } else {
    oled_.print("Temp: ");
    oled_.print(temperature, 1);
    oled_.print(" C");
  }

  oled_.setCursor(0, 20);
  oled_.print("Motor: ");
  oled_.print(speedPercent);
  oled_.print(" %");

  int barWidth = map(speedPercent, 0, 100, 0, 100);
  oled_.fillRect(20, 32, barWidth, 8, SSD1306_WHITE);
  oled_.drawRect(20, 32, 100, 8, SSD1306_WHITE);

  oled_.setCursor(0, 50);
  oled_.print("Ventilador Inteligente");
  oled_.display();
}

void Display::showMessage(const char* line1, const char* line2, int speedPercent) {
  oled_.clearDisplay();
  oled_.setCursor(0, 0);
  oled_.print(line1);
  if (strlen(line2) > 0) {
    oled_.setCursor(0, 12);
    oled_.print(line2);
  }
  oled_.setCursor(0, 30);
  oled_.print("Motor: ");
  oled_.print(speedPercent);
  oled_.print("%");
  oled_.display();
}