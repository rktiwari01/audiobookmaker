# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt requirements.txt

# Install the required packages
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Flask is running on
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
