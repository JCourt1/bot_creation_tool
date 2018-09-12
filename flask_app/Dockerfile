# Use an official Python runtime as a parent image
FROM python:3.6-slim

RUN apt-get update
RUN apt-get -y install gcc

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt



# Make port 80 available to the world outside this container
EXPOSE 80

# Make port 4000 and 5002 available to the world outside this container
EXPOSE 4000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD python app.py
