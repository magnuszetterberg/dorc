import paho.mqtt.client as mqtt
import os
import paho.mqtt.publish as publish
import json
import threading
import time
import uuid
import docker
from dotenv import load_dotenv
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
DOCKER_IMAGE = os.getenv("DOCKER_IMAGE")

# Create a constant agent_uuid for the entire session
AGENT_UUID = str(uuid.uuid4())
COM_UUID = str(uuid.uuid4())
TASK_UUID = str(uuid.uuid4())
RESPONSE_TO = str(uuid.uuid4())

# Send heartbeat function
def send_heartbeat():
    while True:
        heartbeat_message = {
            "name": "providence",
            "agent-type": "virtual",
            "agent-description": "dorc",
            "agent-uuid": AGENT_UUID,  # Use the constant agent_uuid
            "levels": ["sensor"],
            "rate": 5,
            "stamp": time.time(),
            "type": "HeartBeat"
        }

        try:
            # Convert the dictionary to a JSON string
            heartbeat_json = json.dumps(heartbeat_message)

            # Publish the JSON message to the MQTT broker with "/heartbeat" appended to the topic
            publish.single(MQTT_TOPIC + "/heartbeat", heartbeat_json, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
            time.sleep(5)  # Wait for 5 seconds before sending the next heartbeat
        except Exception as e:
            print(f"Error sending heartbeat: {e}")

# Function to parse the MQTT payload and trigger container creation or container stop
def handle_mqtt_payload(payload):
    try:
        payload_dict = json.loads(payload)
        task_name = payload_dict.get("task", {}).get("name", "")

        if task_name == "start-object-detection": 
            start_container(payload)

        elif task_name == "stop-object-detection":
            stop_container(payload)

        else:
            pass

    except json.JSONDecodeError as e:
        print(f"Error decoding MQTT payload: {e}")

# Function to start a Docker container
def start_container(payload):
    # Parse the MQTT payload to extract the "agent" value
    payload_dict = json.loads(payload)
    agent_name = payload_dict.get("task", {}).get("params", {}).get("agent", "")

    client = docker.from_env()
    stream_id = {
        "stream_name": agent_name
    }
    # Define container options
    container_options = {
        "detach": True,  # Run the container in detached mode (in the background)
        "name": agent_name,  # Set the name of the container
        #"privileged": True,  # Give the container extended privileges (needed for mounting Docker socket)
        #"volumes": {"/usr/bin/ffmpeg": {"bind": "/usr/bin/ffmpeg", "mode": "rw"}},  # Mount the Docker socket
        "tty": True,  # Enable pseudo-TTY (equivalent to -t flag)
        "environment": stream_id,
        "remove": True 
        }
        # Start the Docker container
    try:
        response_payload = [{          
            "name": agent_name,
            "status": "starting"
            }]

        response_json = json.dumps(response_payload)
        publish.single(RESPONSE_TOPIC, response_json, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
        container = client.containers.run(DOCKER_IMAGE, **container_options)
        print(f"Container {agent_name} started successfully.")
        time.sleep(3)
        response_payload = [{          
            "name": agent_name,
            "status": "started"
            }]

        response_json = json.dumps(response_payload)
        publish.single(RESPONSE_TOPIC, response_json, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
    except docker.errors.ContainerError as e:
        print(f"Container {agent_name} encountered an error: {e}")
    except docker.errors.ImageNotFound as e:
        print(f"Image {DOCKER_IMAGE} not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Function to stop a Docker container
def stop_container(payload):
        # Parse the MQTT payload to extract the "agent" value
        payload_dict = json.loads(payload)
        agent_name = payload_dict.get("task", {}).get("params", {}).get("agent", "")
        try:
            # Create a Docker client
            client = docker.from_env()

            # Find the container by its name
            container = client.containers.get(agent_name)
                
            # Stop the container gracefully
            print("Trying to stop", agent_name)
            container.stop()
            print(f"Container {agent_name} stopped successfully.")
            response_payload = []

            response_json = json.dumps(response_payload)
            publish.single(RESPONSE_TOPIC, response_json, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
        except docker.errors.NotFound:
            print(f"Container {agent_name} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")


# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe(MQTT_TOPIC)

# MQTT on_message callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
   # print(f"Received payload: {payload}")
    handle_mqtt_payload(payload)

# Create MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

# Start the MQTT loop (this keeps the script running)
mqtt_thread = threading.Thread(target=lambda: mqtt_client.loop_forever())
mqtt_thread.start()

# Start the heartbeat thread
heartbeat_thread = threading.Thread(target=send_heartbeat)
heartbeat_thread.start()

