# Use the official Python image as the base image
FROM python:3.9-slim

#Update the image and install docker.io
RUN apt-get update && apt-get install -y docker.io

# Set the working directory
WORKDIR /app

# Copy your Python script and .env file into the container
COPY main.py /app/main.py
COPY .env /app/.env

# Install required packages
COPY reqs.txt .
RUN pip install --no-cache-dir -r reqs.txt





# Run the Python script when the container starts
#CMD ["python", "main.py"]
