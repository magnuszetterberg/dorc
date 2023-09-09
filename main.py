import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import subprocess
import paho.mqtt.publish as publish
import json

# SETUP ENV
# Load environment variables from .env file
load_dotenv()

# MQTT settings
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
RESPONSE_TOPIC = os.getenv("RESPONSE_TOPIC")
RESPONSE_PAYLOAD = os.getenv("RESPONSE_PAYLOAD")

# Docker settings
DOCKER_CONTAINER_COMMAND = os.getenv("DOCKER_CONTAINER_COMMAND")
DOCKER_CONTAINER_NAME_PREFIX = os.getenv("DOCKER_CONTAINER_NAME_PREFIX")

# Function to start a Docker container with a given payload
def start_container(payload):
    try:
        subprocess.run([DOCKER_CONTAINER_COMMAND], shell=True)
        print(f"Container started with payload: {payload}")

        # Create a dictionary for the response payload
        response_payload = {
            "active": RESPONSE_PAYLOAD
        }

        # Convert the dictionary to a JSON string
        response_json = json.dumps(response_payload)

        # Publish the JSON message back to the specified topic
        publish.single(RESPONSE_TOPIC, response_json, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
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
