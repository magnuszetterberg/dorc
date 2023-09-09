import paho.mqtt.client as mqtt
import docker
import os
from dotenv import load_dotenv
import uuid  # For generating unique container names

# Load environment variables from .env file
load_dotenv()

# MQTT settings
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

# Docker settings
DOCKER_IMAGE_NAME = os.getenv("DOCKER_IMAGE_NAME")

# Function to generate a unique container name
def generate_container_name():
    return f"{os.getenv('DOCKER_CONTAINER_NAME')}-{str(uuid.uuid4())[:8]}"

# Function to start a Docker container with a given payload
def start_container(payload):
    client = docker.from_env()
    container_name = generate_container_name()
    container = client.containers.run(
        DOCKER_IMAGE_NAME,
        detach=True,
        name=container_name,
        environment={"PAYLOAD": payload},
    )
    print(f"Container {container.name} started with payload: {payload}")

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
