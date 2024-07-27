import json
import time
import requests
import paho.mqtt.client as mqtt
import base64
from datetime import datetime
import logging
import sys
import os

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "ohm_mqtt_poller.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_config():
    try:
        with open('config.json', 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error("config.json file not found.")
        return None
    except json.JSONDecodeError:
        logging.error("config.json is not a valid JSON file.")
        return None

def read_credentials():
    try:
        with open("enc.bin", "rb") as file:
            encoded_credentials = file.read().decode().strip()
        credentials = base64.b64decode(encoded_credentials).decode()
        username, password = credentials.split(':')
        return username, password
    except FileNotFoundError:
        logging.error("Credentials file (enc.bin) not found. Please run the credentials encoder script first.")
        return None, None
    except Exception as e:
        logging.error(f"Error reading credentials: {e}")
        return None, None

def get_ohm_data(config):
    url = f"http://{config['ohm']['server']}:{config['ohm']['port']}/data.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from OHM: {e}")
        return None

def find_component(name, data, partial_match=False):
    if isinstance(data, dict):
        if partial_match and name.lower() in data.get("Text", "").lower():
            return data
        elif data.get("Text", "").lower() == name.lower():
            return data
        for child in data.get("Children", []):
            result = find_component(name, child, partial_match)
            if result:
                return result
    return None

def extract_value(component, value_type):
    if component:
        for child in component.get("Children", []):
            if child.get("Text", "").lower() == value_type.lower():
                return child.get("Value")
    return None

def clean_value(value):
    if isinstance(value, str):
        # Remove degree symbol, Celsius, and percent sign
        value = value.replace('°C', '').replace('%', '').strip()
        try:
            return float(value)
        except ValueError:
            return value
    return value

def extract_essential_data(data):
    essential_data = {
        "timestamp": datetime.now().isoformat(),
        "cpu": {},
        "memory": {},
        "storage": [],
        "gpus": []
    }

    if not data or not isinstance(data, dict):
        logging.warning("Invalid or empty data received from OHM")
        return essential_data

    # CPU
    cpu = find_component("AMD Ryzen", data, partial_match=True)
    if cpu:
        logging.debug(f"Found CPU component: {cpu['Text']}")
        temp = find_component("temperatures", cpu)
        load = find_component("load", cpu)
        if temp:
            essential_data["cpu"]["temperature"] = clean_value(extract_value(temp, "cpu package"))
        if load:
            essential_data["cpu"]["utilization"] = clean_value(extract_value(load, "cpu total"))
    else:
        logging.warning("CPU component not found")

    # Memory
    memory = find_component("Generic Memory", data, partial_match=True)
    if memory:
        logging.debug(f"Found Memory component: {memory['Text']}")
        load = find_component("load", memory)
        if load:
            essential_data["memory"]["utilization"] = clean_value(extract_value(load, "memory"))
    else:
        logging.warning("Memory component not found")

    # Storage
    for child in data.get("Children", []):
        for device in child.get("Children", []):
            if device.get("ImageURL") == "images_icon/hdd.png":
                storage_name = device.get("Text")
                logging.debug(f"Found Storage component: {storage_name}")
                temp = find_component("temperatures", device)
                load = find_component("load", device)
                storage_data = {"name": storage_name}
                if temp:
                    storage_data["temperature"] = clean_value(extract_value(temp, "temperature"))
                if load:
                    storage_data["utilization"] = clean_value(extract_value(load, "used space"))
                essential_data["storage"].append(storage_data)

    # GPU
    gpu = find_component("NVIDIA", data, partial_match=True)
    if gpu:
        logging.debug(f"Found GPU component: {gpu['Text']}")
        temp = find_component("temperatures", gpu)
        load = find_component("load", gpu)
        gpu_data = {}
        if temp:
            gpu_data["temperature"] = clean_value(extract_value(temp, "gpu core"))
        if load:
            gpu_data["utilization"] = clean_value(extract_value(load, "gpu core"))
        essential_data["gpus"].append(gpu_data)
    else:
        logging.warning("GPU component not found")

    return essential_data

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logging.info("Connected to MQTT broker")
    else:
        logging.error(f"Failed to connect to MQTT broker with code {rc}")
        
def main():
    setup_logging()
    logging.info("Starting OHM MQTT Poller")

    config = load_config()
    if not config:
        return

    server_id = config.get('serverID')
    if not server_id:
        logging.error("serverID not found in config.json")
        return

    username, password = read_credentials()
    if username is None or password is None:
        return

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect

    mqtt_client.username_pw_set(username, password)

    try:
        mqtt_client.connect(config['mqtt']['server'], config['mqtt']['port'])
        mqtt_client.loop_start()
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker: {e}")
        return

    while True:
        try:
            ohm_data = get_ohm_data(config)
            if ohm_data:
                essential_data = extract_essential_data(ohm_data)
                mqtt_client.publish(f"servers/{server_id}/hardware", json.dumps(essential_data))
                logging.info(f"Data sent to MQTT broker: {essential_data}")
            else:
                logging.warning("No data received from OHM")
            time.sleep(60)  # Poll every 60 seconds
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    main()
