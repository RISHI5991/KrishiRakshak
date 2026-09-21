#include "config.h"
#include "../camera/camera_init.h"
#include "../networking/http_client.h"

void connectWiFi() {
    Serial.print("Connecting to WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected.");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
}

void setup() {
    Serial.begin(115200);
    
    pinMode(LED_FLASH_PIN, OUTPUT);
    digitalWrite(LED_FLASH_PIN, LOW);

    if (!initCamera()) {
        Serial.println("Camera init failed");
        while (true) { delay(100); }
    }
    Serial.println("Camera initialized.");

    connectWiFi();
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        connectWiFi();
    }

    // Flash LED
    digitalWrite(LED_FLASH_PIN, HIGH);
    delay(100); // brief flash to let auto-exposure adjust

    camera_fb_t * fb = esp_camera_fb_get();
    
    digitalWrite(LED_FLASH_PIN, LOW);

    if (!fb) {
        Serial.println("Camera capture failed");
        delay(1000);
        return;
    }

    String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/analyze";
    String response = sendImageToServer(fb->buf, fb->len, url.c_str());
    
    Serial.println("Server response: " + response);

    esp_camera_fb_return(fb);
    
    delay(CAPTURE_INTERVAL);
}
