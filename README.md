# Raspberry Pi Sensor Network

A distributed sensor network system using Raspberry Pi 3 as a central server and multiple Raspberry Pi Pico (RP2040) clients with SCD4X CO2 sensors.

## System Architecture

- **Server (Raspberry Pi 3)**
  - SQLite database for storing sensor readings
  - TCP server handling multiple client connections
  - Data validation and storage management

- **Clients (Raspberry Pi Pico)**
  - SCD40 integration
  - WiFi connectivity
  - Automatic reconnection handling
  - Data transmission with error checking

## Hardware Requirements

- 1x Raspberry Pi 3 (Server)
- 3x Raspberry Pi Pico W (Clients)
- 3x Sensirion SCD4X CO2 Sensors
- Power supplies for all devices
- WiFi network access

## Installation

### Server Setup (Raspberry Pi 3) _ This works fine

1. Clone this repository:
   ```bash
   git clone https://github.com/[your-username]/rpi-sensor-network.git
   cd rpi-sensor-network
   ```

2. Run the server:
   ```bash
   python3 server.py
   ```

### Client Setup (Raspberry Pi Pico)

This part is not quite finished.  I may need to change the libraries and resultant calls

1. Install MicroPython on your Raspberry Pi Pico W if not already installed

2. Copy the following files to each Pico:
   - `client.py

3. Edit `client.py` and update the configuration:
   ```python
   WIFI_SSID = "your_wifi_ssid"
   WIFI_PASSWORD = "your_wifi_password"
   SERVER_IP = "your_server_ip"
   DEVICE_ID = "pico_1"  # Change for each Pico (pico_1, pico_2, pico_3)
   ```

4. Connect the SCD30 or SCD4X sensor to the Pico:
   - SCL: GPIO 17
   - SDA: GPIO 16
   - VCC: 3.3V
   - GND: GND

## Data Format

The system stores the following data for each reading:
- Device ID
- Timestamp
- Temperature (°C)
- Humidity (%)
- CO2 (ppm)

## License

MIT License - feel free to use and modify as needed.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
