# Use an official Python runtime as a parent image
FROM python:3.6-slim

RUN apt-get update
RUN apt-get -y install gcc
RUN apt-get -y install g++

# Set the working directory to /app
WORKDIR /app


# By doing this, we avoid running pip install every single time...
ADD requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /app
ADD . /app

RUN python -m spacy download en_core_web_md
RUN python -m spacy link en_core_web_md en


# Make port 5002 available to the world outside this container
EXPOSE 5002

# Define environment variable
ENV NAME World

WORKDIR /app/rasa_utils/

# Run app.py when the container launches
CMD python -m bot -d ../models/current/dialogue -u ../models/current/nlu
