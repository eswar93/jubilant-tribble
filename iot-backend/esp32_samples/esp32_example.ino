/*
  Minimal ESP32 sample (Arduino) showing registration, telemetry POST, and WebSocket
  - Replace WIFI_SSID, WIFI_PASS, and SERVER_URL before use.
  - Requires ArduinoWebsockets library: https://github.com/gilmaimon/ArduinoWebsockets
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ArduinoWebsockets.h>

using namespace websockets;

const char* WIFI_SSID = "YOUR_SSID";
const char* WIFI_PASS = "YOUR_PASS";
const char* SERVER_URL = "http://192.168.1.100:8000"; // adjust
const char* WS_URL = "ws://192.168.1.100:8000/ws/";   // append device id

String device_id = "esp32-demo-1"; // pick or set from server response

WebsocketsClient ws;

void connectWiFi(){
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void registerDevice(){
  HTTPClient http;
  String url = String(SERVER_URL) + "/devices/register";
  http.begin(url);
  http.addHeader("Content-Type","application/json");
  String body = "{\"device_id\": \"" + device_id + "\", \"model\": \"esp32-demo\"}";
  int res = http.POST(body);
  if(res>0){
    // ignore response for now
  }
  http.end();
}

void sendTelemetry(){
  HTTPClient http;
  String url = String(SERVER_URL) + "/devices/" + device_id + "/telemetry";
  http.begin(url);
  http.addHeader("Content-Type","application/json");
  String body = "{\"temp\": 24.5, \"uptime\": " + String(millis()/1000) + "}";
  int res = http.POST(body);
  http.end();
}

void onMessageCallback(WebsocketsMessage message){
  // Message expected as JSON: {"id":"...","command":{...}}
  Serial.print("WS msg: ");
  Serial.println(message.data());
  // parse and act on command here
}

void setup(){
  Serial.begin(115200);
  connectWiFi();
  registerDevice();

  // open websocket to receive commands
  String wsFull = String(WS_URL) + device_id;
  ws.onMessage(onMessageCallback);
  if(!ws.connect(wsFull)){
    // failed to connect, will retry later
  }
}

unsigned long lastTelemetry = 0;

void loop(){
  ws.poll();
  if(millis() - lastTelemetry > 10000){
    sendTelemetry();
    lastTelemetry = millis();
  }
  delay(10);
}
