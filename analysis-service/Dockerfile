# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

ENV PYTHONPATH=/app/src

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY src/ ./src/

# Make port 8000 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME World

# Run uvicorn when the container launches
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT}
