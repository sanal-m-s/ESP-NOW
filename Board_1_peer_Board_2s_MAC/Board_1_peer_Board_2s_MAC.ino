// Board 1 (peer = Board 2's MAC: 20:E7:C8:67:51:74)

#include <esp_now.h>
#include <WiFi.h>

uint8_t peerMAC[] = {0x20, 0xE7, 0xC8, 0x67, 0x51, 0x74}; // Board 2's MAC

typedef struct struct_message {
  char text[64];
} struct_message;

struct_message outgoing;
struct_message incoming;

void OnDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  memcpy(&incoming, data, sizeof(incoming));
  Serial.print("Received: ");
  Serial.println(incoming.text);
}

void OnDataSent(const wifi_tx_info_t *info, esp_now_send_status_t status) {}

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    return;
  }

  esp_now_register_send_cb(OnDataSent);
  esp_now_register_recv_cb(OnDataRecv);

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, peerMAC, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Failed to add peer");
    return;
  }

  Serial.println("Board 1 Ready. Type a message and press Enter.");
}

void loop() {
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg.length() > 0) {
      msg.toCharArray(outgoing.text, sizeof(outgoing.text));
      esp_now_send(peerMAC, (uint8_t *)&outgoing, sizeof(outgoing));
      Serial.print("Sent: ");
      Serial.println(outgoing.text);
    }
  }
}