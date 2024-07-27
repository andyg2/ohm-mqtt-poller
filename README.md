# OHM MQTT Poller

## Overview

OHM MQTT Poller is a Python script that polls data from Open Hardware Monitor (OHM) [https://github.com/openhardwaremonitor/openhardwaremonitor.git](https://github.com/openhardwaremonitor/openhardwaremonitor.git) and sends essential hardware information (CPU, Memory, Storage, and GPU metrics) to a Mosquitto MQTT broker. This tool is designed to run as a background process on Windows systems, providing real-time hardware monitoring data that can be consumed by other applications or monitoring systems.

## Features

- Polls data from Open Hardware Monitor at regular intervals
- Extracts essential hardware metrics:
  - CPU temperature and utilization
  - Memory utilization
  - Storage devices' temperature and utilization
  - GPU temperature and utilization
- Sends data to an MQTT broker in a structured JSON format
- Runs as a background process without a console window
- Logs activities and errors to a file for easy troubleshooting

## Requirements

- Python 3.6 or higher
- Open Hardware Monitor running on the local or remote Windows machine
- Access to an MQTT broker

## Installation

1. Clone this repository or download the source code.
2. Install the required Python packages:
   
   ```
   pip install requests paho-mqtt pyinstaller
   ```
3. Create a `config.json` file in the same directory as the script with the following structure:
   
   ```json
   {
     "serverID": 123765123,
     "ohm": {
       "server": "192.168.88.5",
       "port": 8085
     },
     "mqtt": {
       "server": "168.212.226.204",
       "port": 1883
     }
   }
   ```
   
   Replace the values with your specific configuration.
4. Run the credential encoder script to create the `enc.bin` file:
   
   ```
   python encode_mqtt_credentials.py
   ```
   
   Follow the prompts to enter your MQTT username and password.
5. (Optional) Create an executable:
   
   ```
   pyinstaller --onefile --noconsole ohm_mqtt_poller.py
   ```
   
   This will create a standalone executable in the `dist` directory.

## Configuration

### config.json

- `serverID`: A unique identifier for the server running this script
- `ohm`:
  - `server`: IP address or hostname of the machine running Open Hardware Monitor
  - `port`: Port number of the Open Hardware Monitor web server (default is usually 8085)
- `mqtt`:
  - `server`: IP address or hostname of your MQTT broker
  - `port`: Port number of your MQTT broker (default is usually 1883)

### Credentials

MQTT credentials are stored in an encoded format in the `enc.bin` file. Please note this is not at all secure, it's very simply to extract the credentials from this format. Use the `encode_mqtt_credentials.py` script to create or update this file.

## Usage

### Running the Script

You can run the script directly with Python:

```
python ohm_mqtt_poller.py
```

Or, if you've created an executable, simply place the executable in the **same directory** as the `config.json` and `enc.bin` files and double-click the executable file or run it from the command line.

### Running at Startup

To make the script start automatically when Windows boots:

1. Create a shortcut to the executable (or to `pythonw.exe` with the script as an argument).
2. Press `Win + R`, type `shell:startup`, and press Enter.
3. Move the shortcut to the Startup folder that opens.

### Logging

The script logs its activities and any errors to `logs/ohm_mqtt_poller.log`. Check this file for troubleshooting if you encounter any issues.

## Data Format

The script sends data to the MQTT broker in the following JSON format:

```json
{
  "timestamp": "2024-07-27T09:20:00.946719",
  "cpu": {
    "temperature": 86.5,
    "utilization": 13.1
  },
  "memory": {
    "utilization": 44.8
  },
  "storage": [
    {
      "name": "Hitachi HUA723020ALA641",
      "temperature": 42.0,
      "utilization": 82.6
    },
    {
      "name": "Ramsta  SSD S800 1TB",
      "temperature": 40.0,
      "utilization": 65.0
    }
  ],
  "gpus": [
    {
      "temperature": 47.0,
      "utilization": 28.0
    }
  ]
}
```

## Contributing

Contributions to this project are welcome! Please fork the repository and submit a pull request with your changes.

## License

[MIT License](LICENSE)

## Acknowledgements

This project uses the following open-source libraries:

- [requests](https://docs.python-requests.org/en/master/)
- [paho-mqtt](https://pypi.org/project/paho-mqtt/)
- [PyInstaller](https://www.pyinstaller.org/)

Special thanks to the Open Hardware Monitor project for providing the hardware monitoring capabilities.

