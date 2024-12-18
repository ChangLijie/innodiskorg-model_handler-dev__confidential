FROM python:3.10-slim

# Set the working directory
WORKDIR /workspace
COPY ./model_handler /workspace/

# Install the dependencies from requirements.txt
RUN pip install -r requirements.txt

