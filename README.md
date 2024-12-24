# Location-Detection-with-ESP8266-Wi-Fi-Module

This project utilizes the ESP8266 Wi-Fi module to detect the location and distance of devices based on Wi-Fi signals. It provides a low-cost and efficient solution for IoT (Internet of Things) applications.

## Features
- **ESP8266 Wi-Fi Module**: Connects to Wi-Fi networks and scans nearby devices' signal strengths.
- **RSSI-Based Localization**: Estimates the distance of devices using Received Signal Strength Indicator (RSSI).
- **Lightweight and Portable**: Easily integrable into other systems and suitable for mobile applications.
- **IoT Compatibility**: Enables seamless integration with other IoT devices.

## Requirements
To run this project, you need the following:
- **ESP8266 NodeMCU LoLin V3**
- **Visual Studio Code** with PlatformIO extension installed
- Wi-Fi network for testing

## Setup Instructions
1. **Install PlatformIO Extension**:
   - Open Visual Studio Code and go to the Extensions tab.
   - Search for `PlatformIO IDE` and install the extension.

2. **Clone the Repository**:
   - Clone this repository to your local machine:
     ```bash
     git clone https://github.com/your-repository-name.git
     ```
   - Open the project folder in Visual Studio Code.

3. **Configure Wi-Fi Settings**:
   - In the `src/main.cpp` file, update the `SSID` and `Password` with your Wi-Fi credentials:
     ```cpp
     const char* ssid = "Your_SSID";
     const char* password = "Your_Password";
     ```

4. **Build and Upload the Code**:
   - Connect your ESP8266 board to your computer.
   - In Visual Studio Code, click on the PlatformIO icon in the sidebar.
   - Select **Build** to compile the code and **Upload** to flash it to the board.

## Usage
1. Power on the ESP8266 board.
2. Monitor the output using the PlatformIO Serial Monitor.
3. Observe the detected devices' MAC addresses, RSSI values, and estimated distances.

## Project Structure
- **`src/main.cpp`**: The main source code file.
- **`platformio.ini`**: PlatformIO configuration file.
- **`README.md`**: This documentation file.
- **`include/`**: Header files for additional functionality.
- **`lib/`**: Libraries used in the project.

## Example Output
Below is a sample output from the Serial Monitor:
