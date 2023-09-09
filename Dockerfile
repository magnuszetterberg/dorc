# Use the official Python image as the base image
FROM python:3.9-slim

# Install required packages
COPY reqs.txt .
RUN pip install -r reqs.txt

# Copy your Python script and .env file into the container
COPY main.py /app/main.py
COPY .env /app/.env

# Set the working directory
WORKDIR /app

# Run the Python script when the container starts
#CMD ["python", "main.py"]
