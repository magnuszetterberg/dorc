import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import subprocess
import paho.mqtt.publish as publish
import json
import threading
import time
import uuid

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

# Function to parse the MQTT payload and trigger container creation
def handle_mqtt_payload(payload):
    try:
        payload_dict = json.loads(payload)
        task_name = payload_dict.get("task", {}).get("name", "")
        
        if task_name == "start-object-detection": 
            start_container(DOCKER_CONTAINER_COMMAND)

        elif task_name == "stop-object-detection":
            stop_container(CONTAINER_NAME)
        
        else:
            pass
    
    except json.JSONDecodeError as e:
        print(f"Error decoding MQTT payload: {e}")

# Function to start a Docker container
def start_container(DOCKER_CONTAINER_COMMAND):
    try:
        start_obj_detection()
        # Start the subprocess and capture stdout
        process = subprocess.Popen(DOCKER_CONTAINER_COMMAND, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Get the return code of the subprocess
        return_code = process.returncode
        if return_code != 0:
            print(f"Subprocess exited with return code: {return_code}")
        else:
            publish_feedback() # HÄR VILL JAG SKICKA FEEDBACK VIA FEEDBACK() ATT CONTAINER GICK UPP OM JAG INTE FÅ UT NÅN RETURN CODE

    except subprocess.CalledProcessError as e:
        print(f"Error starting container: {e}")

# Function to start object-detection
def start_obj_detection():

    try:
        response_payload = [{
            "name": "loop",
            "status": "running"
        },
        {    
            "name": "loop",
            "status": "starting"
        }]

        response_json = json.dumps(response_payload)

        publish.single(RESPONSE_TOPIC, response_json, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
        
        # Call the publish_response function with data
        publish_response(AGENT_UUID, COM_UUID, RESPONSE_TO, TASK_UUID, response="running", fail_reason="")
        
    except subprocess.CalledProcessError as e:
        print(f"Error starting container: {e}")

# Function to publish a response message
def publish_response(AGENT_UUID, COM_UUID, RESPONSE_TO, TASK_UUID, response="running", fail_reason=""):
    #Generate new UUIDs
    RESPONSE_TO = str(uuid.uuid4())
    COM_UUID = str(uuid.uuid4())
    TASK_UUID = str(uuid.uuid4())
    response_message = {
        "agent-uuid": AGENT_UUID,
        "com-uuid": COM_UUID,
        "fail-reason": "",
        "response": "starting",
        "response-to": RESPONSE_TO,
        "task-uuid": TASK_UUID
        }

 
    try:
        # Convert the dictionary to a JSON string
        response_json = json.dumps(response_message)

        # Publish the JSON message to the MQTT broker
        publish.single(MQTT_TOPIC + "/response", response_json, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
    except Exception as e:
        print(f"Error publishing response: {e}")

# Function to publish a response message
def publish_feedback(AGENT_UUID, COM_UUID, status, TASK_UUID):
    #Generate new UUIDs
    COM_UUID = str(uuid.uuid4())
    TASK_UUID = str(uuid.uuid4())
    response_message = {
        "agent-uuid": AGENT_UUID,
        "com-uuid": COM_UUID,
        "status": "running",
        "task-uuid": TASK_UUID
        }

 
    try:
        # Convert the dictionary to a JSON string
        response_json = json.dumps(response_message)

        # Publish the JSON message to the MQTT broker
        publish.single(MQTT_TOPIC + "/feedback", response_json, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
    except Exception as e:
        print(f"Error publishing response: {e}")



# Function to stop a Docker container
def stop_container(container_name):
    try:
        stop_obj_detection()

        subprocess.Popen(["docker", "stop", container_name])
        # Call the publish_response function with data

        time.sleep(4) #this might have to a be while loop to regulary check if it's done or not
        remove_container(CONTAINER_NAME)

    except subprocess.CalledProcessError as e:
        print(f"Error stopping container: {e}")

# Function to remove a docker container
def remove_container(container_name):
    try:

        subprocess.Popen(["docker", "rm", container_name])
        # Call the publish_response function with data
  

    except subprocess.CalledProcessError as e:
        print(f"Error stopping container: {e}")


# Function to stop object-detection
def stop_obj_detection():
    try:
        response_payload = [{
            "name": "loop",
            "status": "running"
        }]

        response_json = json.dumps(response_payload)

        publish.single(RESPONSE_TOPIC, response_json, hostname=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
        publish_response(AGENT_UUID, COM_UUID, RESPONSE_TO, TASK_UUID, response="stopped", fail_reason="")
    except subprocess.CalledProcessError as e:
        print(f"Error starting container: {e}")


# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe(MQTT_TOPIC)

# MQTT on_message callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    #print(f"Received payload: {payload}")
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
