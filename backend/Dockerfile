# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

RUN openssl req -newkey rsa:2048 -nodes -keyout private_key.pem -x509 -days 365 -out origin_certificate.pem -subj "/C=US/ST=YourState/L=YourCity/O=YourOrganization/CN=YourCommonName"


# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container 
CMD ["gunicorn", "--certfile", "origin_certificate.pem", "--keyfile", "private_key.pem", "-b", "0.0.0.0:5000", "app:app"]
