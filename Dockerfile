# Use an official Python runtime as a parent image
FROM python:3.6-slim

RUN apt-get update
RUN apt-get -y install gcc && apt-get -y install g++ && apt-get install -y procps && apt-get install -y lsof

# Set the working directory to /app
WORKDIR /app


# By doing this, we avoid running pip install every single time...
ADD requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN python -m spacy download en_core_web_md
RUN python -m spacy link en_core_web_md en

# Copy the current directory contents into the container at /app
ADD . /app





# Make port 80 available to the world outside this container
# EXPOSE 80

# Make port 4000 and 5002 available to the world outside this container
EXPOSE 4000 5002

# Define environment variable
ENV NAME World

ENV _bot_production_server one

WORKDIR /app/flask_app/

# Run app.py when the container launches
CMD python app.py
