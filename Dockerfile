# Use the official Python 3.11 base image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /workspace

# Copy your application code into the container
COPY . /workspace

RUN pip install flit
ENV FLIT_ROOT_INSTALL=1

# Install any necessary Python dependencies
RUN flit install --symlink

WORKDIR /workspace/test

# Define the command to run your application
CMD ["python", "gta6/main.py"]
