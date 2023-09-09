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
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
# Docker settings
DOCKER_CONTAINER_COMMAND = os.getenv("DOCKER_CONTAINER_COMMAND")




# Function to start a Docker container
def start_container(payload):
    try:
        start_obj_detection()
        subprocess.run([DOCKER_CONTAINER_COMMAND], shell=True)
        
    
    except subprocess.CalledProcessError as e:
        print(f"Error starting container: {e}")

#Function to stop a Docker container
def stop_container(container_name):
    try:
        stop_obj_detection()
        subprocess.run(["docker", "stop", container_name])
        print(f"Container {container_name} stopped successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping container: {e}")

# Function to parse the MQTT payload and trigger container creation
def handle_mqtt_payload(payload):
    try:
        payload_dict = json.loads(payload)
        #agent = payload_dict.get("task", {}).get("params", {}).get("agent", "")
        task_name = payload_dict.get("task", {}).get("name", "")
        
        if task_name == "start-object-detection":
            start_container(payload)
        
        else:
            if task_name == "stop-object-detection":
                stop_container(CONTAINER_NAME)

                
    except json.JSONDecodeError as e:
        print(f"Error decoding MQTT payload: {e}")

#Function to start a object-detection
def start_obj_detection():
    try:
        # Create a dictionary for the response payload
        response_payload = [{
            "name": "loop",
            "status": "running"
        },
        {    
            "name": "loop",
            "status": "starting"
        }]

        # Convert the dictionary to a JSON string
        response_json = json.dumps(response_payload)

        # Publish the JSON message back to the specified topic
        publish.single(RESPONSE_TOPIC, response_json, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
        
    except subprocess.CalledProcessError as e:
        print(f"Error starting container: {e}")

#Function to start a object-detection
def stop_obj_detection():
    try:
        # Create a dictionary for the response payload
        response_payload = [{
            "name": "loop",
            "status": "running"
        }]

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
    handle_mqtt_payload(payload)

# Create MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

# Start the MQTT loop (this keeps the script running)
mqtt_client.loop_forever()
