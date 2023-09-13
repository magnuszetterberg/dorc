# Use the official Python image as the base image
FROM python:3.9-slim

#Update the image and install docker.io
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory
WORKDIR /app

# Copy your Python script and .env file into the container
COPY . .

# Install required packages
#COPY reqs.txt .
RUN pip install --no-cache-dir -r req.txt





# Run the Python script when the container starts
CMD ["python", "haris.py"]
