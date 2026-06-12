# ESP-NOW Communication between Two ESP32 Boards

This project demonstrates **ESP-NOW**, a connectionless WiFi protocol by Espressif, used to send and receive messages directly between two ESP32 boards via their Serial Monitors — without needing a WiFi router or internet connection.

## 📋 Overview

- Type a message in **Board 1's** Serial Monitor → it appears on **Board 2's** Serial Monitor.
- Type a message in **Board 2's** Serial Monitor → it appears on **Board 1's** Serial Monitor.
- Communication is bidirectional and works purely over WiFi radio using MAC addresses.

## 📁 Project Structure

```
ESP_NOW/
├── Get_the_MAC_address_of_each_ESP32/
│   └── Get_the_MAC_address_of_each_ESP32.ino   # Find the MAC address of a board
├── Board_1_peer_Board_2s_MAC/
│   └── Board_1_peer_Board_2s_MAC.ino           # Sketch for Board 1
├── Board_2_peer_Board_1s_MAC/
│   └── Board_2_peer_Board_1s_MAC.ino           # Sketch for Board 2
└── README.md
```

## 🛠️ Hardware Required

- 2 x ESP32 development boards
- 2 x USB cables
- A laptop/PC with the Arduino IDE installed

## ⚙️ Setup Instructions

### Step 1: Get the MAC address of each board

1. Upload `Get_the_MAC_address_of_each_ESP32.ino` to **each** ESP32 (one at a time).
2. Open the Serial Monitor (115200 baud).
3. Note down the printed MAC address for each board.

### Step 2: Configure peer MAC addresses

- In `Board_1_peer_Board_2s_MAC.ino`, set `peerMAC[]` to **Board 2's** MAC address.
- In `Board_2_peer_Board_1s_MAC.ino`, set `peerMAC[]` to **Board 1's** MAC address.

### Step 3: Upload sketches

- Upload `Board_1_peer_Board_2s_MAC.ino` to Board 1.
- Upload `Board_2_peer_Board_1s_MAC.ino` to Board 2.

### Step 4: Test communication

1. Open the Serial Monitor for **both** boards (115200 baud, line ending set to **Newline**).
2. Type a message (e.g., `hi`) in Board 1's Serial Monitor and press Enter.
3. It should appear as `Received: hi` on Board 2's Serial Monitor — and vice versa.

## 🧠 How It Works

- Each ESP32 is identified by its unique **MAC address**.
- Devices register each other as **peers** using `esp_now_add_peer()`.
- `esp_now_send()` transmits a small struct of data directly to the peer's MAC address.
- `esp_now_register_recv_cb()` sets up a callback that fires automatically when data is received.
- No WiFi router, IP address, or internet connection is required — communication happens directly over the WiFi radio.

## 📌 Notes

- Maximum payload size per ESP-NOW packet is **250 bytes**.
- Both boards must be on the same WiFi channel to communicate (default `channel = 0` uses the current channel).
- Typical range: ~100-200m line of sight (less indoors).

## 🔧 Requirements

- [Arduino IDE](https://www.arduino.cc/en/software) with ESP32 board support installed
- ESP32 core version 3.x (uses `wifi_tx_info_t` callback signature)

## 📜 License

This project is open-source and free to use for educational purposes.