#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

// Wi-Fi bilgileri
const char* ssid = "iPhone";  // Wi-Fi ağ adı
const char* password = "12345678";  // Wi-Fi şifre  

// NTP istemcisi ayarları
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 3600 * 3, 60000);  // Türkiye: GMT+3

void setup() {
  Serial.begin(115200);  // Seri haberleşmeyi başlat
  WiFi.begin(ssid, password);

  // Wi-Fi bağlantısı
  Serial.print("Wi-Fi'ye bağlaniliyor");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi bağlantisi başarili!");

  // NTP istemcisini başlat
  timeClient.begin();
}

void loop() {
  // NTP zamanını güncelle
  timeClient.update();

  // JSON verisi oluşturma
  StaticJsonDocument<200> doc;
  doc["Time"] = timeClient.getFormattedTime();  // Güncel zaman
  doc["AP_ID"] = ssid;  // Wi-Fi ağı ID'si (SSID)
  doc["RSSI"] = WiFi.RSSI();  // Wi-Fi sinyal gücü
  doc["LowBattery"] = false;  // Batarya durumu sabit olarak false
  
  // JSON'u String formatına dönüştür
  String jsonOutput;
  serializeJson(doc, jsonOutput);

  // JSON'u seri monitöre yazdır
  Serial.println("JSON Verisi:");
  Serial.println(jsonOutput);

  delay(5000);  // 5 saniye bekle
}
