# Model Handler

Model Handler is a project designed to provide an interface for uploading custom model files and deploying them to the Ollama Model Server. It simplifies the process of managing machine learning models, enabling seamless integration and efficient operations.

## Purpose

The primary goal of Model Handler is to create an efficient workflow for managing models by:

* Providing an API to upload custom model files.

* Deploying uploaded models to Ollama.

* Supporting model lifecycle management, including creation, deletion, and listing.

## Features

* Upload Models: Upload custom model files to the server.

* Deploy to Ollama: Deploy the uploaded models to the Ollama Model Server for use.

* Manage Models: Perform operations such as listing available models, deleting models, and managing model metadata.

## API Endpoints
See more api information from [API Documents](./docs/api.md)

## Getting Started
### Prerequisites
* You must first create a models folder. Inside the models folder, there should be two subdirectories: inno and ollama.
    ```
    models/
    ├── inno/
    └── ollama/
    ```
* A running instance of Ollama Model Server [(How to Run Ollama)](https://github.com/ollama/ollama). When starting the Ollama server, ensure the models folder is mounted properly:

    - ./models/ollama:/root/.ollama

    - ./models/inno:/home   

### Installation
Run Docker:
   ```bash
   docker run -it --rm -p 5000:5000 \
      -v ${model folder path}:/workspace/models \
      -e MODEL_SERVER_IP=${Ollama IP} \
      -e MODEL_SERVER_PORT=${Ollama Port} \
      --name test_model_handler \
      innodiskorg/model_handler:v0.0.2 python3 app.py
   ```
   **Notes:**
   - **model folder path**: The directory path where your models will be stored. *(The models folder you created earlier, which contains the inno and ollama subdirectories.)*
   - **Ollama IP**: The IP address of the Ollama Model Server.
   - **Ollama Port**: The port number of the Ollama Model Server.


   