import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import uuid
import re
import subprocess

# SETUP ENV 
# Load environment variables from .env file
load_dotenv()
# MQTT settings
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
# Docker settings
DOCKER_CONTAINER_COMMAND = os.getenv("DOCKER_CONTAINER_COMMAND")
DOCKER_CONTAINER_NAME_PREFIX = os.getenv("DOCKER_CONTAINER_NAME_PREFIX")

# Function to generate a unique container name
# def generate_container_name():
#     random_str = str(uuid.uuid4())[:8]
#     # Remove any characters that are not allowed in container names
#     sanitized_str = re.sub(r'[^a-z0-9_]', '_', random_str)
#     return f"{DOCKER_CONTAINER_NAME_PREFIX}-{sanitized_str}"

# Function to start a Docker container with a given payload
def start_container(payload):
    # container_name = generate_container_name()
    try:
        # Run the Docker command
        subprocess.run(DOCKER_CONTAINER_COMMAND, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting container: {e}")




# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe(MQTT_TOPIC)

# MQTT on_message callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(f"Received payload: {payload}")
    start_container(payload)

# Create MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

# Start the MQTT loop (this keeps the script running)
mqtt_client.loop_forever()
